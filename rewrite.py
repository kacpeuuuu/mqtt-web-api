from abc import ABC, abstractmethod
import json
import paho.mqtt.client as mqtt
import time
import queue

class Formatter:

    # msg.payload is bytes in paho mqtt
    @staticmethod
    def formatMqttPayloadToString(msg_payload: bytes) -> str:
        return msg_payload.decode("utf-8", errors="ignore")

    @staticmethod
    def formatMqttPayloadToJson(msg_payload: bytes) -> dict:
        return json.loads(msg_payload.decode("utf-8", errors="ignore"))

    @staticmethod       #this bases on the assumption that i will not change the length of /devices/report/{mac-address}
    def getMacFromTopic(msg_topic: str) -> str:
        try: 
            return str(msg_topic[15:])
        except:
            raise IndexError(f"the topic was shorter than expected: {msg_topic}")
        
    @staticmethod
    def validateRequiredFields(msg_formatted: dict) -> None:
        _requiredFields = ("topic", "devicePin", "isRunning", "durationLeft", "pinState")

        missing_fields = []
        for key in _requiredFields:
            if key not in msg_formatted:
                missing_fields.append(key)
            # else:
            #     if (msg_formatted[key] == None) or (msg_formatted[key] == ""):
            #         raise ValueError("")
            

        if missing_fields != []:
            raise ValueError(f"the payload was missing the required fields: {missing_fields}")
       
        
        
# ConcreteCreators 



# Products

class Device(ABC):
    def __init__(self, topic: str, devicePin: int, isRunning: bool, durationLeft: int, pinState: int, **kwargs): #
        self.topic = topic
        self.devicePin = devicePin
        self.isRunning = isRunning
        self.durationLeft = durationLeft
        self.pinState = pinState
        self.extraConfig = kwargs

        self.showDevice = True     # if false sensor will not appear on the website
        self.lastMessageTime = 0      


    @abstractmethod
    def enableDevice(self):
        pass

    @abstractmethod
    def disableDevice(self):
        pass

    @abstractmethod
    def updateLastMessageTime(self, time: float):
        self.lastMessageTime = time

    @abstractmethod
    def updateData(self, formattedPayload: dict):
        pass
    

class BlindsDevice(Device):
    def __init__(self, topic: str, devicePin: int, isRunning: bool, durationLeft: int, pinState: int, **kwargs):
        super().__init__(topic, devicePin, isRunning, durationLeft, pinState, **kwargs) 

    def enableDevice(self):
        return '{"duration": 10000}'

    def disableDevice(self):
        pass

    def updateLastMessageTime(self, time):
        self.lastMessageTime = time

    def updateData(self, formattedPayload):
        self.topic = formattedPayload["topic"]
        self.devicePin = formattedPayload["devicePin"]
        self.isRunning = formattedPayload["isRunning"]
        self.durationLeft = formattedPayload["durationLeft"]
        self.pinState = formattedPayload["pinState"]

        
 

class DeviceFactory:
    # provides easy to use interface in creating and modifying Devices
    def createSensor(self, type: str, formattedPayload: dict):
        _deviceTypes = {
            "blindsdevice": BlindsDevice
        }

        if type.lower() in _deviceTypes:
            deviceObject = _deviceTypes[type.lower()]
            return deviceObject(**formattedPayload)
  
        else:
            raise KeyError("Factory could not find approperiate key for the sensor {type}")



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

        payload = Formatter.formatMqttPayloadToJson(msg.payload)
        topic = msg.topic
        macAddress = Formatter.getMacFromTopic(msg.topic)
        payloadTimestamp = time.time()
        try:
            Formatter.validateRequiredFields(payload)

            device = self.devicesDict.get(macAddress)
            if device is not None:
                device.updateData(payload)
            else:
                newObject = self.deviceFactory.createSensor("blindsDevice", payload)
                newObject.lastMessageTime = payloadTimestamp
                self.devicesDict[macAddress] = newObject



        except Exception as e:
            print(f"exception in: processPayload(), {e}")

    def getDevice(self, key: str):
        if key in self.devicesDict:
            return self.devicesDict[key]

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

        

    def getDevice(self, key):
        tempDevice = self.stateManager.getDevice(key)
        command = tempDevice.enableDevice()
        topic = tempDevice.topic
        self.transport.sendMessage(command, topic)

    def setTransportCallback(self, function) -> None:
        self.transport.setCallback(function)

    
    

#   TRANSPORT
class Transport:
    def __init__(self, mqttClient: MqttWrapper):
        self.mqttClient = mqttClient

    def sendMessage(self, command: str, topic: str) -> None:
        self.mqttClient.publish_on_topic(command, topic)

    def setCallback(self, callback) -> None:
        self.mqttClient.setCallback(callback)

    def start(self):
        self.mqttClient.start()

    

    

#TODO: probably needs modifying
# the stateManager should not be here
# orchestrator needs a way to store messages from mqttWrapper and pass them to stateManager
class MqttWrapper:
    def __init__(self, address : str, port=1883, keepAlive=60):   #callback is the function passed from Orchestrator or Transport which processes the inbound messages
        self.address = address
        self.port = port
        self.keepAlive = keepAlive
        # self.isConnected = False      #not sure if needed

        self.mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.on_connect_fail = self.on_connect_fail
        self.mqttClient.on_publish = self.on_publish
        self.mqttClient.on_message = self.on_message
        self.mqttClient.on_subscribe = self.on_subscribe
        self.mqttClient.on_unsubscribe = self.on_unsubscribe
        
        #every message on "devices/report/+" is routed to on_sensor_report 
        self.mqttClient.message_callback_add("devices/report/+", self.on_sensor_report)

        self.callback = None

    def setCallback(self, function):
        self.callback = function

    def start(self) -> None:
        try:
            self.mqttClient.connect(self.address, self.port, self.keepAlive)
            self.mqttClient.loop_start()
            # self.isConnected = True
            print("MQTT client started and connected to broker at {}:{}".format(self.address, self.port))
        except Exception as e:
            # self.isConnected = False
            print(f"MQTT client could NOT connect: {e}")

    def stop(self) -> None:
        try:
            self.mqttClient.loop_stop()
            self.mqttClient.disconnect()
            print("MQTT client stopped.")
            # self.isConnected = False
        except Exception as e:
            print(f"Error during disconnecting: {e}")

    def get_device_state(self) -> None:
        self.publish_on_topic("devices/report", "Request: report", 1)
        print("Requested report from devices.")

    def passPayloadToCallback(self, payload: mqtt.MQTTMessage) -> mqtt.MQTTMessage:   
        print(f"RECIEVED A PAYLOAD: {payload}") 
        self.callback(payload)

    def on_sensor_report(self, client : mqtt.Client , userdata, msg : mqtt.MQTTMessage) -> None:
        print("REPORT REPORT")
        if self.callback != None:
            print("payload passed to StateManager")
            self.passPayloadToCallback(msg)
        else:
            raise Exception("MqttWrapper: callback is None, before starting the client please set the callback")


    def publish_on_topic(self, topic: str, message: str, qos=0) -> None:
        self.mqttClient.publish(topic, message)

    def on_connect(self, client : mqtt.Client, userdata, flags, reason_code, properties) -> None:   #paho.mqtt.reasoncodes.ReasonCode   #paho.mqtt.properties.Properties
        self.subscribe_to_topic("devices/report/+", 1) #subscribes with QoS 1 to the topic "devices/report/+" to receive sensor reports
        print(f"Connected with result code {reason_code}")

    def on_connect_fail(self, client : mqtt.Client, userdata):
        raise ConnectionError(f"Failed to connect to broker! {self.address}:{self.port}")

    def on_publish(self, client : mqtt.Client, userdata, mid : int, reason_code, properties):
        print(f"\nmessage published - mid: {mid}\treason_code:{reason_code}")

    def on_subscribe(self, client : mqtt.Client, userdata, mid : int, granted_qos, properties):
        print(f"subscribed to a topic, MID:{mid}, QoS:{granted_qos}")

    def on_unsubscribe(self, client : mqtt.Client, userdata, mid : int, reason_codes, properties):
        print(f"unsubscribed from a topic, MID:{mid}")

    def on_message(self, client : mqtt.Client, userdata, msg):
        binary_data = msg.payload.decode("utf-8", errors="replace")
        print(f"mid: {msg.mid}\tpayload: {binary_data}\tqos: {msg.qos}\ttimestamp: {msg.timestamp}\ttopic: {msg.topic}")

    def subscribe_to_topic(self, topic: str, qos: int=0):
        self.mqttClient.subscribe(topic, qos)
        
    def loop_forever(self):
        self.mqttClient.loop_forever()
        
    def on_disconnect(self, client : mqtt.Client, userdata, disconnect_flags, reason_code, properties):
        print("disconnected")
        print(f"client: {client}, userdata: {userdata}, disconnect_flags: {disconnect_flags}, reason_code: {reason_code}, properties: {properties}")



    