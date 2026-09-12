from abc import ABC, abstractmethod
import json

class Formatter:

    # msg.payload is bytes in paho mqtt
    @staticmethod
    def formatMqttPayloadToString(msg_payload: bytes) -> str:
        return msg_payload.decode("utf-8", errors="ignore")

    @staticmethod
    def formatMqttPayloadToJson(msg_payload: bytes) -> dict:
        return json.loads(msg_payload.decode("utf-8", errors="ignore"))

    @staticmethod
    def getMacFromTopic(msg_topic: bytes) -> str:
        try: 
            return str(msg_topic[15:].decode("utf-8", errors="ignore"))
        except:
            raise IndexError(f"the topic was shorter than expected: {msg_topic.decode("utf-8", errors="ignore")}")
        
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
        self.showDevice = True     # if false sensor will not appear on the website
        self.lastMessageTime = 0      

        self.extraConfig = kwargs

    @abstractmethod
    def enableDevice(self):
        pass

    @abstractmethod
    def disableDevice(self):
        pass
    

class BlindsDevice(Device):
    def __init__(self, topic: str, devicePin: int, isRunning: bool, durationLeft: int, pinState: int, **kwargs):
        super().__init__(topic, devicePin, isRunning, durationLeft, pinState, **kwargs) 

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
            json_payload = Formatter.formatMqttPayloadToJson(payload)
            Formatter.validateRequiredFields(json_payload)                #  json dict
            return deviceObject(**json_payload)
  
        else:
            raise KeyError



class StateManager:
    # is responsible for coupling Device type object with last message sent by it
    # if timed out, it should be hidden from display
    # state manager calls the factory to creare an unseen device


class Transport:
    