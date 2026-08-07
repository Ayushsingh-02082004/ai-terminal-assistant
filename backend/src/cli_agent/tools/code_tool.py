import os
import py_compile
from crewai.tools import tool

@tool("Code Editor and Syntax Checker")
def code_tool(action: str, path: str, target: str = "", replacement: str = "") -> str:
    """
    Analyzes, edits, or checks the syntax of code files.
    
    Args:
        action (str): The code operation. Must be one of: 'search', 'edit', 'check_syntax'.
        path (str): The path to the code file.
        target (str, optional): The substring/code pattern to search for, or the exact code block to be replaced when editing. Defaults to "".
        replacement (str, optional): The new code block to replace the target block. Defaults to "".
    """
    action = action.lower().strip()
    target_path = os.path.abspath(path)
    
    if not os.path.exists(target_path):
        return f"Error: Code file '{path}' does not exist."
        
    if action == "search":
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            matches = []
            for idx, line in enumerate(lines):
                if target in line:
                    matches.append(f"Line {idx+1}: {line.strip()}")
            if not matches:
                return f"No matches found for '{target}' in file '{path}'."
            return f"Found {len(matches)} match(es):\n" + "\n".join(matches)
        except Exception as e:
            return f"Error searching code: {str(e)}"
            
    elif action == "edit":
        if not target:
            return "Error: You must specify a target string/code block to replace."
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if target not in content:
                return f"Error: Target code block to replace was not found exactly in '{path}'."
                
            new_content = content.replace(target, replacement, 1) # Replace the first occurrence
            
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            return f"Successfully updated code in '{path}'."
        except Exception as e:
            return f"Error editing code: {str(e)}"
            
    elif action == "check_syntax":
        if not path.endswith(".py"):
            return f"Syntax check is only supported for Python (.py) files. '{path}' is not a Python file."
        try:
            py_compile.compile(target_path, doraise=True)
            return f"Syntax check passed: '{path}' is syntactically valid Python."
        except py_compile.PyCompileError as e:
            return f"Syntax Error in '{path}':\n{str(e)}"
        except Exception as e:
            return f"Error checking syntax: {str(e)}"
            
    else:
        return f"Error: Unknown action '{action}'. Supported actions are: 'search', 'edit', 'check_syntax'."
