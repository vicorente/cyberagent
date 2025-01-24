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

class AgentPro:

    def generate_code(self, prompt):
        response: ChatResponse = chat(
            model="qwen2.5-coder:7b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Python code generator. Respond only with executable Python code, no explanations or comments except for required pip installations at the top.",
                },
                {
                    "role": "user",
                    "content": f"Generate Python code to ${prompt}. If you need to use any external libraries, include a comment at the top of the code listing the required pip installations. Do not include any explanations in the code.",
                },
            ],
        )
        code = re.sub(
            r"^```python\n|^```\n|```$",
            "",
            response['message']['content'],
            flags=re.MULTILINE,
        )
        code_lines = code.split("\n")
        while code_lines and not (
            code_lines[0].startswith("import")
            or code_lines[0].startswith("from")
            or code_lines[0].startswith("#")
        ):
            code_lines.pop(0)

        return "\n".join(code_lines)

    def generic_response(self, prompt):
        response: ChatResponse = chat(
            model="qwen2.5-coder:7b",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert system specializing in offensive cybersecurity, designed to assist with conducting thorough and ethical security audits on computer systems, networks, and applications. Your objective is to identify vulnerabilities, recommend appropriate mitigation strategies, and adhere to ethical hacking principles and frameworks like OWASP, PTES, and MITRE ATT&CK.",
                },
                {
                    "role": "user",
                    "content": 
                        """I am conducting a security audit of a Linux-based web server running Apache, PHP, and MySQL. The server is accessible via SSH and has several open ports (22, 80, 443).
                        Identify potential vulnerabilities in this configuration and suggest penetration testing techniques to validate them. 
                        Focus on privilege escalation, web application security, and database security. 
                        Recommend specific tools and how to use them effectively. Every tool must be executable from the terminal in Kali Linux.
                        The response must be in json format with several items representing the tool name, description, usage and command used to run the tool.
                        """
                    ,
                },
            ],
        )

        return  response['message']['content']

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
            print(f"Found {len(unique_endpoints)} unique endpoints: {', '.join(unique_endpoints)}")
            return unique_endpoints
        except Exception as e:
            print(f"❌ Error finding endpoints: {str(e)}")
            return []
    
    def run(self, prompt):
        # print(f"Generating code for: {prompt}")
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
        response = self.generic_response(prompt)
        print(response)
