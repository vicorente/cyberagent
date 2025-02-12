# Required pip imports:
# pip install ollama requests

from ollama import chat
from ollama import ChatResponse
import subprocess
import tempfile
import re
import importlib
import sys
import os
import requests
from typing import List
from pydantic import BaseModel
from ollama import Client

class Command(BaseModel):
    name: str
    description: str
    command: str


class AnalyzedCommand(BaseModel):
    name: str
    errors: str
    suggestions: List[str]
    
class Recon(BaseModel):
    description: str
    commands: List[Command]


class Agent:
    client = Client(
        host='http://172.16.5.180:11434'
    )
    
    def recon(self, target):
        # self.client.pull('deepseek-r1:8b')
        response: ChatResponse = self.client.chat(
            # model="hf.co/bartowski/WhiteRabbitNeo-2.5-Qwen-2.5-Coder-7B-GGUF:latest",
            model="deepseek-r1:70b",
            # model="jimscard/whiterabbit-neo:13b", 
            # model="hf.co/bartowski/Llama-3.1-WhiteRabbitNeo-2-70B-GGUF:latest",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an expert system specialized in offensive cybersecurity, designed to assist with conducting thorough and ethical security audits on computer systems, networks, and applications. 
                    Your objective is to identify vulnerabilities, recommend appropriate mitigation strategies, and adhere to attack frameworks like OWASP, CAPEC, and MITRE ATT&CK.""",
                },
                {
                    "role": "user",
                    "content": f"""

                        You are a pentester and your role is to make a reconnaissance phase of an audit of a TARGET with ip 192.168.1.0/24.
                        
                        You will plan a penetration testing in a task list as a description of the reconnaissance phase for the target, including the tools and commands you will use to find hidden vulnerabilities and misconfigurations in the target. 
                        In the description, you must include the purpose of each tool or command and how it will help you to achieve the objective, and show how the commands are related to each other. 
                        Do not include commands literals in the description, only the purpose and how it will help you to achieve the objective.
                        You should not use fully automated scanners such as Nessus or OpenVAS. You should use manual penetration testing tools such as nmap, nikto, gobuster, etc. Do not repeate commands.
                        Every tool must be only executable from the terminal in Kali Linux and must be fully automatic with no manual intervention required. Do no use tools with graphical interfaces like burpsuite that require manual interaction.
                        Use only tools present in Kali Linux by default, do not use custom tools or scripts.
                        The description must be detailed, at least 300 words long, do not include vague and general information, it must be written in a professional and technical style and set the order in which the tools and commands will be executed and why.
                        Do not provide install commands.
                                                
                        Recommend specific tools, scripts and linux commands, and how to use them effectively for this purpose. At least include 5 different tools or commands.
                                            
                        Use the commands with unusual options, remember that the objective is to find hidden vulnerabilities and misconfigurations, be creative.
                        
                        Include detailed commands for the tools, and be sure all commands work. Include the TARGET for every command with the target URL supplied in the prompt.
                        Prioritize a combinations of tools that use the outputs of one tool as the input to another tool using pipes or other methods. 
                        Do not repeat the same type of tool, try to use different types of tools for different purposes.                        

                        """,
                },
            ],
            format=Recon.model_json_schema(),
            options={"temperature": 0.7},
        )
        print(response["message"]["content"])
        return response.message.content

    def analyze_command(self, command):
        response: ChatResponse = self.client.chat(
            model="hf.co/bartowski/Llama-3.1-WhiteRabbitNeo-2-70B-GGUF:latest",
            # model="deepseek-r1:8b",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an expert in offensive cybersecurity, You have to test attack tools and scripts to verify their execution may be correct.""",
                },
                {
                    "role": "user",
                    "content": f""" 
                        You are part of a cybersecurity team and receive commands from other members. Your role is to analyze these commands in Kali Linux syntax to determine their validity and generate corrected scripts if necessary.
                        Analyze a given command string in Kali Linux, check its validity, suggest possible improvements and provide a new command usage, and provide an approval or correction with the appropriate script.
                        Analyze only the the command itself, not the name or description of the tool or any other aspect.
                        
                        Analyze the command {command} and check its validity and show errors if any, suggest possible improvements and provide a new complete command usage, and provide an approval or correction with the appropriate script. 
                        Be creative and provide more than one possible command if necessary.
                        
                        It is important to provide a complete command with all the necessary options and arguments, and the target for the command.
                        
                        All commands must be ready to execute without errors, include the target for every command, if it does not exist just make it up.
                        Do no answer with any other format because the response will be parsed by an automated system. Do not include any additional information or comments.
                        """,                    
                },
            ],
            format=AnalyzedCommand.model_json_schema(),
            options={"temperature": 0.7},
        )
        return response["message"]["content"]

    def install_libraries(self, code):
        libraries = re.findall(r"#\s*pip install\s+([\w-]+)", code)
        if libraries:
            print("Installing required libraries...")
            for lib in libraries:
                try:
                    importlib.import_module(lib.replace("-", "_"))
                    print(f"{lib} is already installed.")
                except ImportError:
                    print(f"Installing {lib}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print("Libraries installed successfully.")

    def execute_code(self, code):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(
                ["python", temp_file_path], capture_output=True, text=True, timeout=30
            )
            output = result.stdout
            error = result.stderr
        except subprocess.TimeoutExpired:
            output = ""
            error = "Execution timed out after 30 seconds."
        finally:
            os.unlink(temp_file_path)

        return output, error

    def find_endpoints(js_url: str) -> List[str]:
        """Finds API endpoints in JavaScript code."""
        print("Searching for endpoints in JavaScript code...")
        try:
            response = requests.get(js_url)
            js_content = response.text

            patterns = [
                r'["\']/(api/[^"\']*)["\']',
                r':\s*["\']/(api/[^"\']*)["\']',
                r'fetch\(["\']/(api/[^"\']*)["\']',
            ]

            endpoints = []
            for pattern in patterns:
                matches = re.findall(pattern, js_content)
                endpoints.extend(matches)

            unique_endpoints = list(set(endpoints))
            print(
                f"Found {len(unique_endpoints)} unique endpoints: {', '.join(unique_endpoints)}"
            )
            return unique_endpoints
        except Exception as e:
            print(f"❌ Error finding endpoints: {str(e)}")
            return []

    def run(self, prompt):
        print(f"Generating code for: {prompt}")
        # code = self.generate_code(prompt)
        # print("Generated code:")
        # print(code)
        # print("\nInstalling libraries...")
        # self.install_libraries(code)

        # print("\nExecuting code...")
        # output, error = self.execute_code(code)

        # if output:
        #     print("Output:")
        #     print(output)
        # if error:
        #     print("Error:")
        #     print(error)
