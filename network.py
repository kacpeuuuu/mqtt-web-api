import paho.mqtt.client as mqtt


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

    def _emulateMessage(self, message: str):
        tempMsg = mqtt.MQTTMessage(mid=9494, topic=bytes("devices/report/test-test", "utf-8"))
        tempMsg.payload = bytes(message, "utf-8")
        self.on_sensor_report(self.mqttClient, None, msg=tempMsg)

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



    