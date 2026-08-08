import subprocess
import os
from crewai.tools import tool

@tool("Execute Shell Command")
def shell_tool(command: str) -> str:
    """
    Executes a shell command in the local workspace and returns its stdout and stderr.
    Use this tool to run system commands, build tasks, install packages, or check systems.
    
    Args:
        command (str): The shell command to run.
    """
    try:
        # Run command using system default shell, in the current working directory
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,  # 1 minute timeout to prevent hanging commands
            cwd=os.getcwd()
        )
        
        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
            
        if not output:
            return f"Command executed successfully with exit code {result.returncode} (No output)."
            
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
