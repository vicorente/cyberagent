import json
import re
import subprocess
from typing import Union, Dict, Any, List

def clean_json_string(text: str) -> str:
    """Clean and format JSON string by removing markdown code blocks and extra whitespace."""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*|\s*```', '', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text

def parse_json_response(text: str) -> Union[Dict[str, Any], None]:
    """Parse a JSON string and return a dictionary."""
    try:
        cleaned_text = clean_json_string(text)
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def execute_shell_command(command: str, timeout: int = 300) -> tuple[str, str]:
    """Execute a shell command and return stdout and stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return "", f"Error executing command: {str(e)}"

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing illegal characters."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def format_command_output(stdout: str, stderr: str) -> Dict[str, str]:
    """Format command output into a dictionary."""
    return {
        "stdout": stdout.strip() if stdout else "",
        "stderr": stderr.strip() if stderr else "",
        "success": not bool(stderr)
    }

def parse_tool_requirements(command_data: Dict[str, Any]) -> List[str]:
    """Extract tool requirements from command data."""
    requirements = []
    if 'install' in command_data:
        if isinstance(command_data['install'], str):
            requirements.append(command_data['install'])
        elif isinstance(command_data['install'], list):
            requirements.extend(command_data['install'])
    return requirements
