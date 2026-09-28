from devices import Device, BlindsDevice, DeviceFactory
from utils import Formatter
import paho.mqtt.client as mqtt
import json
import time
from network import Transport, MqttWrapper

class StateManager:
    # is responsible for coupling Device type object with last message sent by it
    # if timed out, it should be hidden from display
    # state manager calls the factory to creare an unseen device
    def __init__(self, deviceFactory: DeviceFactory, deviceTimeout = 5):
        self.deviceFactory = deviceFactory

        self.devicesDict: dict[str, Device] = {}       # "{mac-address}": Device-like object
        self.deviceTimeout = deviceTimeout
        
        # self.lastPayload = {}               # dict version of bytes payload
        # self.lastPayloadTopic = ""
        # self.lastPayloadTimestamp = 0.0

    def processPayload(self, msg: mqtt.MQTTMessage) -> None:
        print(msg.payload)
        payload = Formatter.formatMqttPayloadToJson(msg.payload)
        topic = msg.topic
        macAddress = Formatter.getMacFromTopic(msg.topic)
        payloadTimestamp = time.time()
        # try:
        Formatter.validateRequiredFields(payload)

        device = self.devicesDict.get(macAddress)

        if device is None:
            newObject = self.deviceFactory.createSensor("blindsDevice", payload)
            newObject.lastMessageTime = payloadTimestamp
            newObject.topic = topic
            self.devicesDict[macAddress] = newObject
            
        else:
            device.updateData(payload)
            device.updateLastMessageTime(payloadTimestamp)
            if device.topic is None:
                device.topic = topic



        # except Exception as e:
        #     print(f"exception in: processPayload(), {e}")

    def getDevice(self, key: str):
        if key in self.devicesDict:
            return self.devicesDict[key]

    def getDeviceDict(self):
        return self.devicesDict

    def flagTimedOutDevices(self): # if timed out changes the showDevice property to false
        currentTime = time.time()

        for device in self.devicesDict.values():
            if currentTime - device.lastMessageTime >= self.deviceTimeout:
                device.showDevice = False



class Orchestrator:
    #TODO: modify stateManager to return a Device-like object with a getter method
    #TODO: create a way for orchestrator to read the command instance returned by the device's method of send_message 
    #TODO: create Transport class, implement queue to not block cpu
    #TODO: create Command class
        
    def __init__(self, stateManager: StateManager, transport: Transport):
        self.stateManager = stateManager
        self.transport = transport

        self.setTransportCallback(stateManager.processPayload)
        self.transport.start()

    def getReport(self):
        self.transport.getReport()

    def getDevicesToJson(self):
        response = {}
        devicesDict = self.stateManager.getDeviceDict()
        for device in devicesDict.values():
            device_data = device.getData()
            response[device.topic] = device_data

        return json.dumps(response) 

    def getDevice(self, key):
        tempDevice = self.stateManager.getDevice(key)
        command = tempDevice.enableDevice()
        topic = tempDevice.topic
        self.transport.sendMessage(command, topic)

    def setTransportCallback(self, function) -> None:
        self.transport.setCallback(function)