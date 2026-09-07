import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from mqtt_connection import MqttWrapper
from fastapi import WebSocketDisconnect
#from enum import Enum
import os
import json
import time

brokerAddress = str(os.getenv("BROKER_ADDRESS", ""))
brokerPort = int(os.getenv("BROKER_PORT", 1883))
brokerKeepAlive = int(os.getenv("KEEP_ALIVE", 60))
mqttClient = MqttWrapper(brokerAddress, brokerPort, brokerKeepAlive)

print(brokerKeepAlive)
sensors = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        mqttClient.start()
    except Exception as e:
        print(f"Could not connect to broker! {e}")
        raise

    yield

    mqttClient.stop()

app = FastAPI(lifespan = lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")



# @app.get("/")
# async def get():
#     return HTMLResponse(content=html)

@app.get("/devices/report")
async def get_devices(request: Request):
    mqttClient.get_report()
    await asyncio.sleep(0.5) 

    sensors = mqttClient.sensorMac
    print({"topics": sensors})
    return {"topics": sensors}

@app.get("/heartbeat")
async def heartbeat():
    return {"time": time.time()}


@app.get("/devices/{device_mac}")
async def get_device(device_mac: str):
    mqttClient.get_report()
    await asyncio.sleep(0.5) 
    sensors = mqttClient.sensorMac
    return sensors[f"{device_mac}"]

@app.put("/devices/{device_mac}/changeDevicePin")
async def set_device_pin(device_mac: str, devicePin: int):
    json_content = {"devicePin": devicePin}
    mqttClient.publish_on_topic(f"devices/{device_mac}/changeDevicePin", json.dumps(json_content), 1)

    mqttClient.get_report()
    await asyncio.sleep(0.5) 
    sensors = mqttClient.sensorMac
    try:
        result = sensors[f"{device_mac}"]

    except:
        return None
    
    return result

@app.put("/devices/{device_mac}/changeDeviceTypeId")
async def set_device_type_id(device_mac: str, deviceTypeId):
    json_content = {"deviceTypeId": deviceTypeId}
    mqttClient.publish_on_topic(f"/devices/{device_mac}/changeDeviceTypeId", json.dumps(json_content), 1)
    mqttClient.get_report()
    await asyncio.sleep(0.5) 
    sensors = mqttClient.sensorMac
    try:
        result = sensors[f"{device_mac}"]

    except:
        return None
    
    return result
    

@app.put("/devices/{device_mac}/enableDevice")
async def enable_device(device_mac: str, duration: int):
    json_content = {"duration": duration}
    mqttClient.publish_on_topic(f"devices/{device_mac}/enableDevice", json.dumps(json_content), 1)
    

@app.put("/devices/{device_mac}/disableDevice")
async def disable_device(device_mac: str):
    mqttClient.publish_on_topic(f"devices/{device_mac}/disableDevice", "disable", 1)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()


    try:
        while True:
            # Grab the latest dictionary from your wrapper
            mqttClient.get_report()
            await asyncio.sleep(0.5) 
            current_data = mqttClient.sensorMac 
            
            # Send the entire dictionary to the frontend as a JSON object
            await websocket.send_json(current_data)
            

            
    except WebSocketDisconnect:
        print("User closed the dashboard.")

    except Exception as e:
        print(f"Error: {e}")



app.mount("/", StaticFiles(directory="static", html=True), name="static")