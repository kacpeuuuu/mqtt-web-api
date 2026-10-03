from devices import Device, DeviceFactory, BlindsDevice
from core import StateManager, Orchestrator
from utils import Formatter
from network import Transport, MqttWrapper

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocketDisconnect
#from enum import Enum
import os
import json
import time


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

@app.get("/devices/report")
async def get_devices(request: Request):
    print(stateManager.getDeviceDict())
    orchestrator.getReport()
    await asyncio.sleep(0.3)

    devices_data = orchestrator.getDevicesToJson()
    print(devices_data)
    if devices_data is None:
        raise HTTPException(status_code=404, detail="Devices not found")
    return {"DevicesList": devices_data}

@app.get("/devices/{device_mac}")
async def get_device(device_mac: str):
    orchestrator.getReport()
    await asyncio.sleep(0.3)

    device_data = orchestrator.getDeviceJson(device_mac)
    if device_data is None:
        raise HTTPException(status_code=404, details="Device not found")

    return device_data


app.mount("/", StaticFiles(directory="static", html=True), name="static")