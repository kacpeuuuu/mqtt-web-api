from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from mqtt_connection import MqttWrapper
#from enum import Enum
import os

brokerAddress = str(os.getenv("BROKER_ADDRESS"))
brokerPort = int(os.getenv("BROKER_PORT"))
brokerKeepAlive = int(os.getenv("KEEP_ALIVE"))
mqttClient = MqttWrapper(brokerAddress, brokerPort, brokerKeepAlive)

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

templates = Jinja2Templates(directory="templates")

    
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request, "home.html", {})


@app.get("/devices/report")
async def get_devices(request: Request):
    mqttClient.get_report()
    topics = mqttClient.sensorTopics
    print(f"TOPICS: {topics}")
    return templates.TemplateResponse(request, "report.html", {"request": request, "conetnt": topics})
