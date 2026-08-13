from textual.widgets import Static
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

class UserMessage(Static):
    """Widget for displaying User Prompts."""
    def __init__(self, message: str):
        if isinstance(message, bytes):
            message = message.decode('utf-8', errors='replace')
        panel = Panel(
            Text(f"User > {message}", style="bold cyan"),
            border_style="cyan",
            title="[bold]Instruction[/bold]",
            title_align="left"
        )
        super().__init__(panel)


class RouterCard(Static):
    """Widget for displaying Router Agent decision output."""
    def __init__(self, routing_output: str):
        if isinstance(routing_output, bytes):
            routing_output = routing_output.decode('utf-8', errors='replace')
        routing_str = str(routing_output) if routing_output else "Direct routing completed."
        panel = Panel(
            Markdown(routing_str),
            title="[bold magenta]>> Router Agent: Intent & Pathing Decision[/bold magenta]",
            title_align="left",
            border_style="magenta"
        )
        super().__init__(panel)


class ExecutionCard(Static):
    """Widget for displaying Executor Agent output."""
    def __init__(self, execution_output: str):
        if isinstance(execution_output, bytes):
            execution_output = execution_output.decode('utf-8', errors='replace')
        execution_str = str(execution_output) if execution_output else "Task executed successfully."
        panel = Panel(
            Markdown(execution_str),
            title="[bold green]>> Executor Agent: Tool Execution Output[/bold green]",
            title_align="left",
            border_style="green"
        )
        super().__init__(panel)
