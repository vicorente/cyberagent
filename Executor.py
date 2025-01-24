# Required pip imports:
# pip install paho-mqtt

import paho.mqtt.client as mqtt
import json
import utils
import subprocess
import logging
import sys
import os
from datetime import datetime

class CommandExecutor:
    def __init__(self, broker="localhost", port=1883, topic="commands"):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.setup_logging()

    def setup_logging(self):
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # Set up logging with file in logs directory
        log_file = os.path.join(log_dir, f'executor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging to file: {log_file}")

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info(f"Connected to MQTT Broker with result code {rc}")
        client.subscribe(self.topic)

    def execute_command(self, command_data):
        try:
            if 'install' in command_data:
                self.logger.info(f"Installing required tool: {command_data['install']}")
                result = subprocess.run(command_data['install'], shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"Installation failed: {result.stderr}")
                    return False

            if 'command' in command_data:
                self.logger.info(f"Executing command: {command_data['command']}")
                result = subprocess.run(command_data['command'], shell=True, capture_output=True, text=True)
                output = {
                    'command': command_data['command'],
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode,
                    'timestamp': datetime.now().isoformat()
                }
                self.logger.info(f"Command output: {output}")
                return output
            return False
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            return False

    def on_message(self, client, userdata, msg):
        try:
            payload = utils.parse_json_response(msg.payload.decode())
            self.logger.info(f"Received command on topic {msg.topic}")
            
            if not payload or 'recon' not in payload:
                self.logger.error("Invalid payload format")
                return

            for command in payload['recon']:
                self.logger.info(f"Processing command: {command}")
                # result = self.execute_command(command)
                # if result:
                #     self.logger.info(f"Command executed successfully: {result}")
                # else:
                #     self.logger.error("Command execution failed")

        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON: {e}")
            self.logger.debug(f"Raw message: {msg.payload.decode()}")

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.logger.info(f"Connecting to broker {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            self.logger.info("Shutting down executor...")
            self.client.disconnect()
        except Exception as e:
            self.logger.error(f"Error in executor: {str(e)}")

if __name__ == "__main__":
    executor = CommandExecutor()
    executor.start()

