from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from mqtt_connection import MqttWrapper
import os


brokerAddress = str(os.getenv("BROKER_ADDRESS"))
brokerPort = int(os.getenv("BROKER_PORT"))
brokerKeepAlive = int(os.getenv("KEEP_ALIVE"))

templates = Jinja2Templates(directory="templates")


mqttClient = MqttWrapper(brokerAddress, brokerPort, brokerKeepAlive)
app = FastAPI()

@app.get("/", )
def read_root(request: Request):
    return templates.TemplateResponse(request, "home.html")
