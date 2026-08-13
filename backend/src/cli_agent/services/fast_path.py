import re
import shlex
from typing import Optional, Tuple
from cli_agent.services.shell_tool import shell_tool

# Direct CLI executable prefixes
DIRECT_COMMAND_PREFIXES = (
    "git ", "ls", "ls ", "pwd", "dir", "cat ", "grep ", "find ",
    "python ", "python3 ", "pip ", "pip3 ", "npm ", "node ", "npx ",
    "cargo ", "docker ", "mkdir ", "touch ", "cp ", "mv ", "echo ",
    "which ", "where ", "curl ", "wget ", "df", "du", "free", "uptime",
    "whoami", "env", "uname", "systemctl ", "service "
)

def try_fast_path_execution(user_request: str) -> Optional[Tuple[str, str]]:
    """
    Analyzes user_request to see if it is a direct terminal/CLI command.
    If so, executes it directly in < 50ms without invoking the LLM pipeline.
    
    Returns:
        Tuple[routing_output, execution_output] if executed via fast-path.
        None if the query requires LLM reasoning.
    """
    req_trimmed = user_request.strip()
    if not req_trimmed:
        return None

    # Check if request starts with a known direct CLI command prefix or syntax
    is_direct_command = False
    
    # Check prefixes
    for prefix in DIRECT_COMMAND_PREFIXES:
        if req_trimmed == prefix.strip() or req_trimmed.startswith(prefix):
            is_direct_command = True
            break

    # If it starts with standard flags or pipe operators (e.g. `ls -la`, `git status --short`)
    if not is_direct_command and re.match(r'^[a-zA-Z0-9_\-.]+(\s+-[a-zA-Z0-9_\-.]+)+', req_trimmed):
        is_direct_command = True

    if is_direct_command:
        routing_out = f"**[Fast-Path Routing]** Direct CLI command detected: `{req_trimmed}`. Bypassed LLM inference for 0ms routing latency."
        if hasattr(shell_tool, "func") and callable(getattr(shell_tool, "func")):
            execution_out = shell_tool.func(req_trimmed)
        elif hasattr(shell_tool, "run") and callable(getattr(shell_tool, "run")):
            execution_out = shell_tool.run(req_trimmed)
        elif callable(shell_tool):
            execution_out = shell_tool(req_trimmed)
        else:
            execution_out = f"Error executing tool: {req_trimmed}"
        return (routing_out, execution_out)

    return None
