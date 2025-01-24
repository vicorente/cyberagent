# sudo apt install mosquitto-dev

from AgentPro import AgentPro
from Publisher import MQTTPublisher
from Colors import Colors

if __name__ == "__main__":
    agent = AgentPro()

    publisher = MQTTPublisher(topic="commands")
    publisher.connect()

    try:
        # Publish messages every 2 seconds
        while True:
            response = agent.recon('https://www.orevestvip.com')
            publisher.publish(response)            
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Stopping publisher...{Colors.ENDC}")
        publisher.client.disconnect()        
        print(f"{Colors.OKGREEN}Publisher stopped.{Colors.ENDC}")
