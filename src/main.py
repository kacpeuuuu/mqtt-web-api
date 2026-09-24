from devices import *
from core import *
from utils import *
from network import *

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from api.src.mqtt_connection import MqttWrapper
from fastapi import WebSocketDisconnect
#from enum import Enum
import os
import json
import time


brokerAddress = str(os.getenv("BROKER_ADDRESS", ""))
brokerPort = int(os.getenv("BROKER_PORT", 1883))
brokerKeepAlive = int(os.getenv("KEEP_ALIVE", 60))
mqttClient = MqttWrapper(brokerAddress, brokerPort, brokerKeepAlive)
wsSleepTimer = 1 # how much time until the next message is passed to the /ws

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


