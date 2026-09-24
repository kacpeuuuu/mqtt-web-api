from abc import ABC, abstractmethod

class Device(ABC):
    def __init__(self, devicePin: int, isRunning: bool, durationLeft: int, pinState: int, topic: str | None = None, **kwargs): #
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

    @abstractmethod
    def getData(self) -> dict:
        pass
    

class BlindsDevice(Device):
    def __init__(self, devicePin: int, isRunning: bool, durationLeft: int, pinState: int, topic: str | None = None, **kwargs):
        super().__init__(topic, devicePin, isRunning, durationLeft, pinState, **kwargs) 

    def enableDevice(self):
        return '{"duration": 10000}'

    def disableDevice(self):
        pass

    def updateLastMessageTime(self, time):
        self.lastMessageTime = time

    def updateData(self, formattedPayload):
        #self.topic = formattedPayload["topic"]
        self.devicePin = formattedPayload["devicePin"]
        self.isRunning = formattedPayload["isRunning"]
        self.durationLeft = formattedPayload["durationLeft"]
        self.pinState = formattedPayload["pinState"]

    def getData(self) -> dict:
        result = {}
        result["topic"] = self.topic
        result["devicePin"] = self.devicePin
        result["isRunning"] = self.isRunning
        result["durationLeft"] = self.durationLeft
        result["pinState"] = self.pinState
        result["extraConfig"] = self.extraConfig

        return result
 

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