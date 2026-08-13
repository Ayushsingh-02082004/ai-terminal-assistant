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
        # Cross-platform dangerous command patterns (Linux/macOS + Windows CMD & PowerShell)
        BLOCKED_PATTERNS = [
            # Linux / macOS
            "rm -rf /", "rm -rf /*", "mkfs", "dd if=", ":(){ :|:& };:", "chmod -r 777 /", "shutdown", "reboot",
            # Windows CMD & PowerShell
            "rmdir /s /q c:", "rmdir /s /q c:\\", "rd /s /q c:", "rd /s /q c:\\",
            "del /f /s /q c:", "del /f /s /q c:\\",
            "format c:", "format d:", "diskpart",
            "stop-computer", "restart-computer", "remove-item -recurse -force c:"
        ]
        cmd_lower = command.lower().replace("\\", "/").strip()
        for pattern in BLOCKED_PATTERNS:
            pattern_norm = pattern.lower().replace("\\", "/")
            if pattern_norm in cmd_lower:
                return f"Error: Shell execution blocked by cross-platform guardrail. Command contains dangerous pattern '{pattern}'."

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
            
        full_output = "\n".join(output)
        max_chars = 20000
        if len(full_output) > max_chars:
            return full_output[:max_chars] + f"\n\n[WARNING: Shell output truncated from {len(full_output)} characters to {max_chars} characters to prevent LLM context limit overflow.]"
            
        return full_output
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
