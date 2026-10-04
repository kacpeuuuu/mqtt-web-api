from devices import Device, DeviceFactory, BlindsDevice
from core import StateManager, Orchestrator
from utils import Formatter
from network import Transport, MqttWrapper

import asyncio
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocketDisconnect
#from enum import Enum
import os
import json
import time

from typing import Annotated


brokerAddress = str(os.getenv("BROKER_ADDRESS", ""))
brokerPort = int(os.getenv("BROKER_PORT", 1883))
brokerKeepAlive = int(os.getenv("KEEP_ALIVE", 60))
mqttClient = MqttWrapper(brokerAddress, brokerPort, brokerKeepAlive)
transport = Transport(mqttClient=mqttClient)
deviceFactory = DeviceFactory()
stateManager = StateManager(deviceFactory=deviceFactory, deviceTimeout=5)
orchestrator = Orchestrator(stateManager=stateManager, transport=transport)
wsSleepTimer = 1 # how much time until the next message is passed to the /ws

@asynccontextmanager
async def lifespan(app: FastAPI):
    # try:

    mqttClient.start()
    # except Exception as e:
    #     print(f"Could not connect to broker! {e}")
        # raise

    yield

    mqttClient.stop()

app = FastAPI(lifespan = lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/devices")
async def get_devices():
    devices_data = orchestrator.getDevicesToJson()
    print(devices_data)
    print(orchestrator.getReport())
    if not devices_data:
        raise HTTPException(status_code=404, detail="Devices not found")
    return {"DevicesList": devices_data}

@app.get("/devices/refresh")
async def refresh_devices():
    orchestrator.getReport()
    return {"status": "success", "detail": "Device data refreshed"}

@app.get("/devices/{device_mac}")
async def get_device(device_mac: str):
    device_data = orchestrator.getDeviceJson(device_mac)
    if not device_data:
        raise HTTPException(status_code=404, detail="Device not found")

    return device_data

#TODO: update to accomodate new functionability
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
            # get the latest sensor dictionary from wrapper
            await asyncio.sleep(wsSleepTimer)
            orchestrator.getReport()
            devices_data = orchestrator.getDevicesToJson()
            print(devices_data)
            # send the entire sensor dictionary to the frontend as a JSON object
            await websocket.send_json(devices_data)
            

            
    except WebSocketDisconnect:
        print("User closed the dashboard.")

    except Exception as e:
        print(f"Error: {e}")


app.mount("/", StaticFiles(directory="/pod/static", html=True), name="static")