# Required pip imports:
# pip install paho-mqtt

import paho.mqtt.client as mqtt
import json
import utils

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
        try:
            payload = utils.parse_json_response(msg.payload.decode())
            #print(f"Received message on topic {msg.topic}")
            #print(f"JSON payload: {payload}")

            print(f"JSON payload: {payload['recon']}")
            return payload
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw message: {msg.payload.decode()}")
            return None

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()

