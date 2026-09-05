import paho.mqtt.client as mqtt
import time

#TODO
#MAKE HEARTBEAT 
class MqttWrapper:
    def __init__(self, address : str, port=1883, keepAlive=60):
        self.address = address
        self.port = port
        self.keepAlive = keepAlive
        self.sensorMac = {   #DUMMY DATA
            "12:A1:E6:FC:D7:CD": '{"deviceIdentifier":0,"deviceTypeId":1,"devicePin":0}',
            "34:B2:F7:FC:D7:CD": '{"deviceIdentifier":0,"deviceTypeId":1,"devicePin":0}',
            "56:C3:G8:FC:D7:CD": '{"deviceIdentifier":0,"deviceTypeId":1,"devicePin":0}',
            "78:D4:H8:FC:D7:CD": '{"deviceIdentifier":0,"deviceTypeId":1,"devicePin":0}',
        }
        self.isConnected = False

        self.mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) 


        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.on_connect_fail = self.on_connect_fail
        self.mqttClient.on_publish = self.on_publish
        self.mqttClient.on_message = self.on_message
        self.mqttClient.on_subscribe = self.on_subscribe
        self.mqttClient.on_unsubscribe = self.on_unsubscribe
        
        self.mqttClient.message_callback_add("devices/report/+", self.on_sensor_report)

    def start(self):
        try:
            self.mqttClient.connect(self.address, self.port, self.keepAlive)
            self.mqttClient.loop_start()
            self.isConnected = True
            print("MQTT client started and connected to broker at {}:{}".format(self.address, self.port))
        except Exception as e:
            self.isConnected = False
            print(f"MQTT client could NOT connect: {e}")

    def stop(self):
        try:
            self.mqttClient.loop_stop()
            self.mqttClient.disconnect()
            print("MQTT client stopped.")
            self.isConnected = False
        except Exception as e:
            print(f"Error during disconnecting: {e}")

    def get_report(self):
        self.publish_on_topic("devices/report", "Request: report", 1)
        print("Requested report from devices.")
        
    def _get_report(self):
        print("report_ready")

    def on_sensor_report(self, client : mqtt.Client , userdata, msg : mqtt.MQTTMessage):
        print(f"APPENDED SENSOR: \t{msg.topic} to the list")
        sensor_mac_addr = str(msg.topic[15:])
        string_text = msg.payload.decode('utf-8', errors="ignore")
        self.sensorMac[sensor_mac_addr] = str(string_text)
        self._get_report()


    def publish_on_topic(self, topic: str, message: str, qos: int):
        self.mqttClient.publish(topic, message)

    def on_connect(self, client : mqtt.Client, userdata, flags, reason_code, properties):   #paho.mqtt.reasoncodes.ReasonCode   #paho.mqtt.properties.Properties
        self.subscribe_to_topic("devices/report/+", 1) #subscribes with QoS 1 to the topic "devices/report/+" to receive sensor reports
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
        
    def on_disconnect(self, client : mqtt.Client, userdata, disconnect_flags, reason_code, properties):
        print("disconnected")
        print(f"client: {client}, userdata: {userdata}, disconnect_flags: {disconnect_flags}, reason_code: {reason_code}, properties: {properties}")



    