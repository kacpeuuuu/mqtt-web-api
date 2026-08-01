from fastapi import FastAPI
from mqtt_connection import MqttWrapper
import os


brokerAddress = str(os.getenv("BROKER_ADDRESS"))
brokerPort = int(os.getenv("BROKER_PORT"))
brokerKeepAlive = int(os.getenv("KEEP_ALIVE"))


mqttClient = MqttWrapper(brokerAddress, brokerPort, brokerKeepAlive)
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": f"Twoje API w Dockerze działa! {brokerAddress}:{brokerPort}   KA: {brokerKeepAlive}"}

@app.get("/hello/{name}")
def say_hello(name: int):
    return {"message": f"Cześć {name}!"}

