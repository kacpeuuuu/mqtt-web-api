import paho.mqtt.client as mqtt


class MqttWrapper:
    def __init__(self, address : str, port=1883, keepAlive=60):
        self.address = address
        self.port = port
        self.keepAlive = keepAlive
        self.sensorTopics = set()

        self.mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) 
        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.on_connect_fail = self.on_connect_fail
        self.mqttClient.on_publish = self.on_publish
        self.mqttClient.on_message = self.on_message
        self.mqttClient.on_subscribe = self.on_subscribe
        self.mqttClient.on_unsubscribe = self.on_unsubscribe

        self.mqttClient.message_callback_add("devices/report/+", self.on_sensor_report)
        self.subscribe_to_topic("devices/report/+", 1) #subscribes with QoS 1 to the topic "devices/report/+" to receive sensor reports

    def start(self):
        self.mqttClient.connect(self.address, self.port, self.keepAlive)
        self.mqttClient.loop_start()
        print("MQTT client started and connected to broker at {}:{}".format(self.address, self.port))

    def stop(self):
        self.mqttClient.loop_stop()
        self.mqttClient.disconnect()
        print("MQTT client stopped.")

    def get_report(self):
        self.publish_on_topic("devices/report", "", 1)
        print("Requested report from devices.")

    def on_sensor_report(self, client : mqtt.Client , userdata, msg : mqtt.MQTTMessage):
        print(f"APPENDED SENSOR: \t{msg.topic} to the list")
        string_text = msg.payload.decode('utf-8', errors="ignore")
        self.sensorTopics.add((str(msg.topic), str(string_text)))

    def publish_on_topic(self, topic: str, message: str, qos: int=0):
        self.mqttClient.publish(topic, message)

    def on_connect(self, client : mqtt.Client, userdata, flags, reason_code, properties):   #paho.mqtt.reasoncodes.ReasonCode   #paho.mqtt.properties.Properties
        print(f"Connected with result code {reason_code}")

    def on_connect_fail(self, client : mqtt.Client, userdata):
        print(f"Failed to connect to broker! {self.address}:{self.port}")

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
    