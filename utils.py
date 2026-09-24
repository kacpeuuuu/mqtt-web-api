import json
class Formatter:

    # msg.payload is bytes in paho mqtt
    @staticmethod
    def formatMqttPayloadToString(msg_payload: bytes) -> str:
        return msg_payload.decode("utf-8", errors="ignore")

    @staticmethod
    def formatMqttPayloadToJson(msg_payload: bytes) -> dict:
        if msg_payload == b'':
            raise Exception("recieved payload was None")
        return json.loads(msg_payload.decode("utf-8", errors="ignore"))

    @staticmethod       #this bases on the assumption that i will not change the length of /devices/report/{mac-address}
    def getMacFromTopic(msg_topic: str) -> str:
        try: 
            return str(msg_topic[15:])
        except:
            raise IndexError(f"the topic was shorter than expected: {msg_topic}")
        
    @staticmethod
    def validateRequiredFields(msg_formatted: dict) -> None:
        _requiredFields = ("devicePin", "isRunning", "durationLeft", "pinState") #deleted "topic"

        missingFields = []
        for key in _requiredFields:
            if key not in msg_formatted:
                missingFields.append(key)
            # else:
            #     if (msg_formatted[key] == None) or (msg_formatted[key] == ""):
            #         raise ValueError("")
            
        
        if missingFields != []:
            raise ValueError(f"the payload was missing the required fields: {missingFields}")
       