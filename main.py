# sudo apt install mosquitto-dev

from AgentPro import AgentPro
from Executor import MQTTListener
from Manager import MQTTPublisher
from Colors import Colors
import threading
import time

if __name__ == "__main__":
    agent = AgentPro()
    agent.run("test")
    listener = MQTTListener(topic="commands")
    listener_thread = threading.Thread(target=listener.start)
    listener_thread.start()

    publisher = MQTTPublisher(topic="commands")
    publisher.connect()

    try:
        # Publish messages every 2 seconds
        while True:
            message = input(f"{Colors.OKBLUE}Enter a message to publish: {Colors.ENDC}")  # Use input for custom messages
            publisher.publish(message)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Stopping publisher and listener...{Colors.ENDC}")
        publisher.client.disconnect()
        listener.client.disconnect()
        listener.client.loop_stop()
        listener_thread.join()
        print(f"{Colors.OKGREEN}Publisher and listener stopped.{Colors.ENDC}")
