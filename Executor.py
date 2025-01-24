# Required pip imports:
# pip install paho-mqtt

import paho.mqtt.client as mqtt

class MQTTListener:
    def __init__(self, broker="localhost", port=1883, topic="test/topic"):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT Broker with result code {rc}")
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()

