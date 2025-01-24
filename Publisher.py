import paho.mqtt.client as mqtt
import time

class MQTTPublisher:
    def __init__(self, broker="localhost", port=1883, topic="test/topic"):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()

    def connect(self):
        self.client.connect(self.broker, self.port, 60)

    def publish(self, message):
        self.client.publish(self.topic, message)

   

