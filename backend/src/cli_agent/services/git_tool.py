import subprocess
import os
from crewai.tools import tool

@tool("Git Repository operations")
def git_tool(action: str, arguments: str = "") -> str:
    """
    Executes Git commands within the local workspace.
    
    Args:
        action (str): The Git action to run. Must be one of: 'status', 'diff', 'add', 'commit', 'log', 'branch'.
        arguments (str, optional): Arguments for the git command (e.g. file paths for 'add', commit message for 'commit', branch name).
    """
    action = action.lower().strip()
    
    # Map actions to actual git commands
    if action == "status":
        command = ["git", "status"]
    elif action == "diff":
        command = ["git", "diff"]
        if arguments:
            command.extend(arguments.split())
    elif action == "add":
        if not arguments:
            return "Error: You must specify what to add (e.g. '.' or file paths) in the arguments."
        command = ["git", "add"] + arguments.split()
    elif action == "commit":
        if not arguments:
            return "Error: You must specify a commit message in the arguments."
        command = ["git", "commit", "-m", arguments]
    elif action == "log":
        # Keep log short to avoid overloading output
        command = ["git", "log", "-n", "5", "--oneline"]
    elif action == "branch":
        command = ["git", "branch"]
        if arguments:
            command.extend(arguments.split())
    else:
        return f"Error: Unknown action '{action}'. Supported actions are: 'status', 'diff', 'add', 'commit', 'log', 'branch'."
        
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        output = []
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(result.stderr)
            
        if not output:
            return f"Git command executed successfully with exit code {result.returncode}."
            
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out."
    except Exception as e:
        return f"Error running git: {str(e)}"
