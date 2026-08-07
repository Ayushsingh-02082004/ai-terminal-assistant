import os
from typing import Literal
from crewai.tools import tool

@tool("File Operations")
def file_tool(action: str, path: str, content: str = "") -> str:
    """
    Performs file operations in the local workspace.
    
    Args:
        action (str): The operation to perform. Must be one of: 'read', 'write', 'list', 'append'.
        path (str): The target file or directory path.
        content (str, optional): The content to write or append to the file. Defaults to "".
    """
    action = action.lower().strip()
    target_path = os.path.abspath(path)
    
    if action == "read":
        if not os.path.exists(target_path):
            return f"Error: File '{path}' does not exist."
        if os.path.isdir(target_path):
            return f"Error: '{path}' is a directory, not a file. Use action='list' to view directories."
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
            
    elif action == "write":
        try:
            # Create directories if they do not exist
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to file '{path}'."
        except Exception as e:
            return f"Error writing file: {str(e)}"
            
    elif action == "append":
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "a", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully appended content to file '{path}'."
        except Exception as e:
            return f"Error appending to file: {str(e)}"
            
    elif action == "list":
        if not os.path.exists(target_path):
            return f"Error: Directory '{path}' does not exist."
        if not os.path.isdir(target_path):
            return f"Error: '{path}' is a file, not a directory. Use action='read' to view file contents."
        try:
            items = os.listdir(target_path)
            result = []
            for item in items:
                item_path = os.path.join(target_path, item)
                is_dir = os.path.isdir(item_path)
                item_type = "DIR " if is_dir else "FILE"
                size = os.path.getsize(item_path) if not is_dir else "-"
                result.append(f"[{item_type}] {item:<30} (Size: {size})")
            if not result:
                return f"Directory '{path}' is empty."
            return "\n".join(result)
        except Exception as e:
            return f"Error listing directory: {str(e)}"
            
    else:
        return f"Error: Unknown action '{action}'. Supported actions are: 'read', 'write', 'list', 'append'."
