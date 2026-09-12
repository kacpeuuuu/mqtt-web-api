from abc import ABC, abstractmethod
import json

class Formatter:

    # msg.payload is bytes in paho mqtt
    @staticmethod
    def formatMqttPayload(msg_payload: bytes) -> str:
        return msg_payload.decode("utf-8", errors="ignore")

    @staticmethod
    def getMacFromTopic(msg_topic: bytes) -> str:
        try: 
            return str(msg_topic[15:].decode("utf-8", errors="ignore"))
        except:
            raise IndexError(f"the topic was shorter than expected: {}")
        
    @staticmethod
    def validateRequiredFields(msg_formatted: dict) -> bool:
        _requiredFields = ("topic", "devicePin", "isRunning", "durationLeft", "pinState")

        missing_fields = []
        for i in _requiredFields:
            if i not in msg_formatted:
                missing_fields.append(i)

        if missing_fields != []:
            raise ValueError(f"the payload was missing the required fields: {missing_fields}")
       
        
        
# ConcreteCreators 



# Products

class Device(ABC):
    def __init__(self, topic: str, devicePin: int, isRunning: bool, durationLeft: int, pinState: int): #regular arguments
        self.topic = topic
        self.devicePin = devicePin
        self.isRunning = isRunning
        self.durationLeft = durationLeft
        self.pinState = pinState
        self.showDevice = True     # if false sensor will not appear on the website
        self.lastMessageTime = 0      

    @abstractmethod
    def enableDevice(self):
        pass

    @abstractmethod
    def disableDevice(self):
        pass
    

class BlindsDevice(Device):
    def __init__(self, topic, devicePin, isRunning, durationLeft, pinState):
        super().__init__(topic, devicePin, isRunning, durationLeft, pinState) #regular arguments

    def enableDevice(self):
        #włączanie 
        pass

    def disableDevice(self):
        pass

 

class DeviceFactory:
    # provides easy to use interface in creating and modifying Devices
    def createSensor(self, type: str, payload: bytes):
        _deviceTypes = {
            "blindsdevice": BlindsDevice
        }

        if type.lower() in _deviceTypes:
            deviceObject = _deviceTypes[type.lower()]
            str_payload = Formatter.formatMqttPayload(payload)
            Formatter.hasRequiredFields(str_payload)    # it's a json in a str format
            return deviceObject(**dict(str_payload))    # so to unpack it we need to convert it to dict
        else:
            raise KeyError



class StateManager:
    # is responsible for coupling Device type object with last message sent by it
    # if timed out, it should be hidden from display
    # state manager calls the factory to creare an unseen device