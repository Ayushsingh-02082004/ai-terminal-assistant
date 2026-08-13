import subprocess
import os
from crewai.tools import tool

IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist", ".idea", ".vscode"}

def filter_shell_output(output_text: str) -> str:
    """Filters out dependency directory lines (venv, __pycache__, node_modules) and caps output size."""
    if not output_text:
        return ""
    lines = output_text.splitlines()
    clean_lines = []
    for line in lines:
        line_parts = set(os.path.normpath(line).lower().split(os.sep))
        if not any(ignored.lower() in line_parts for ignored in IGNORE_DIRS):
            clean_lines.append(line)
    
    if len(clean_lines) > 500:
        clean_lines = clean_lines[:500]
        clean_lines.append("\n[... Command output capped to top 500 lines to prevent prompt context window overload ...]")
    return "\n".join(clean_lines)

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
            filtered_stdout = filter_shell_output(result.stdout)
            if filtered_stdout:
                output.append(f"STDOUT:\n{filtered_stdout}")
        if result.stderr:
            filtered_stderr = filter_shell_output(result.stderr)
            if filtered_stderr:
                output.append(f"STDERR:\n{filtered_stderr}")
            
        if not output:
            return f"Command executed successfully with exit code {result.returncode} (No relevant output)."
            
        full_output = "\n".join(output)
        max_chars = 20000
        if len(full_output) > max_chars:
            return full_output[:max_chars] + f"\n\n[WARNING: Shell output truncated from {len(full_output)} characters to {max_chars} characters to prevent LLM context limit overflow.]"
            
        return full_output
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
