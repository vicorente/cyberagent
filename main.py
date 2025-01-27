# sudo apt install mosquitto-dev

from Agent import Agent
from Publisher import MQTTPublisher
from Colors import Colors
import utils

if __name__ == "__main__":
    agent = Agent()

    publisher = MQTTPublisher(topic="commands")
    publisher.connect()

    try:
        # Publish messages every 2 seconds
        # while True:
        # agent.example()
        response = agent.recon("www.orevestvip.com")
        # payload = utils.parse_json_response(response)
        #  print(response)
        # for command in payload["recon"]:
        #     analyzed_command = agent.analyze_command(command["command"] )
        #     print(f"Analyzed command: {analyzed_command}")                    
        publisher.publish(response)                    

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Stopping publisher...{Colors.ENDC}")
        publisher.client.disconnect()        
        print(f"{Colors.OKGREEN}Publisher stopped.{Colors.ENDC}")
