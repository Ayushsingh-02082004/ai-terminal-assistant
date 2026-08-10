import sys
import os
import io
import asyncio
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Header, Footer, Input, Static, LoadingIndicator, Collapsible, Log, Label
from textual.binding import Binding
from textual import work
from textual.worker import Worker, WorkerState

from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from cli_agent.crew import CLIAgentCrew


class StreamRedirector(io.StringIO):
    """Interceptors stdout/stderr and routes them to the Textual Log widget."""
    def __init__(self, log_widget: Log, original_stream):
        super().__init__()
        self.log_widget = log_widget
        self.original_stream = original_stream

    def write(self, s: str) -> int:
        if s and s.strip():
            # Schedule log write safely on the UI thread
            try:
                self.log_widget.write_line(s.rstrip())
            except Exception:
                pass
        return len(s)

    def flush(self):
        pass


class UserMessage(Static):
    """Widget for displaying User Prompts."""
    def __init__(self, message: str):
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
        panel = Panel(
            Markdown(routing_output if routing_output else "Direct routing completed."),
            title="[bold magenta]>> Router Agent: Intent & Pathing Decision[/bold magenta]",
            title_align="left",
            border_style="magenta"
        )
        super().__init__(panel)


class ExecutionCard(Static):
    """Widget for displaying Executor Agent output."""
    def __init__(self, execution_output: str):
        panel = Panel(
            Markdown(execution_output if execution_output else "Task executed successfully."),
            title="[bold green]>> Executor Agent: Tool Execution Output[/bold green]",
            title_align="left",
            border_style="green"
        )
        super().__init__(panel)



class CLIAgentApp(App):
    """A modern, full-screen Terminal User Interface (TUI) for the CLI Agent."""

    TITLE = "AI Command Line Agent"
    SUB_TITLE = "CrewAI Powered Shell, File, Code & Git Automation"

    CSS = """
    Screen {
        background: $surface;
        layout: vertical;
    }

    #header-info {
        height: 3;
        background: $primary-background;
        color: $text;
        content-align: center middle;
        border-bottom: heavy $accent;
    }

    #chat-container {
        height: 1fr;
        padding: 1 2;
    }

    #spinner-container {
        height: 3;
        align: center middle;
        display: none;
    }

    #input-container {
        height: 3;
        padding: 0 1;
        margin: 0;
    }

    #cmd-input {
        border: tall $accent;
        margin: 0;
    }

    #debug-drawer {
        height: 10;
        margin: 0;
        padding: 0;
        border-top: solid $secondary;
    }
    Log {
        height: 100%;
        background: $surface-darken-1;
    }
    """

    BINDINGS = [
        Binding("ctrl+d", "toggle_debug", "Toggle Debug Logs", show=True),
        Binding("ctrl+c", "quit", "Exit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.agent_crew: Optional[CLIAgentCrew] = None
        self.model_name = os.getenv("OLLAMA_MODEL_NAME", "qwen3.5:cloud")
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label(f"[bold cyan]AI COMMAND LINE AGENT[/bold cyan]  |  [dim]Model: {self.model_name}[/dim]  |  [bold green]Status: Ready[/bold green]", id="header-info")
        
        with ScrollableContainer(id="chat-container"):
            yield Static("[dim]Type your command in plain English below (e.g. 'check git status' or 'list files in backend'). Press Ctrl+D for Debug Logs.[/dim]")
            
        with Container(id="spinner-container"):
            yield LoadingIndicator()

        with Collapsible(title="Debug & Trace Logs (Ctrl+D)", collapsed=True, id="debug-drawer"):
            yield Log(id="debug-log")

        with Container(id="input-container"):
            yield Input(placeholder="User command > Enter your instruction here...", id="cmd-input")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize background dependencies and redirect streams."""
        log_widget = self.query_one("#debug-log", Log)
        sys.stdout = StreamRedirector(log_widget, self.orig_stdout)
        sys.stderr = StreamRedirector(log_widget, self.orig_stderr)

        try:
            self.agent_crew = CLIAgentCrew()
            log_widget.write_line("[SYSTEM] CrewAI Agent system initialized successfully.")
        except Exception as e:
            log_widget.write_line(f"[ERROR] Failed to initialize CrewAI Agent system: {str(e)}")

    def on_unmount(self) -> None:
        """Restore stdout and stderr on exit."""
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr

    def action_toggle_debug(self) -> None:
        """Toggle the collapsible debug log drawer."""
        drawer = self.query_one("#debug-drawer", Collapsible)
        drawer.collapsed = not drawer.collapsed

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission from the Input widget."""
        user_text = event.value.strip()
        if not user_text:
            return

        input_widget = self.query_one("#cmd-input", Input)
        input_widget.value = ""

        if user_text.lower() in ["exit", "quit", "q"]:
            self.exit()
            return

        chat_container = self.query_one("#chat-container", ScrollableContainer)
        header_info = self.query_one("#header-info", Label)
        spinner = self.query_one("#spinner-container", Container)

        # 1. Add User Message Card
        await chat_container.mount(UserMessage(user_text))
        chat_container.scroll_end(animate=False)

        # 2. Set UI status to Thinking
        header_info.update(f"[bold cyan]AI COMMAND LINE AGENT[/bold cyan]  |  [dim]Model: {self.model_name}[/dim]  |  [bold yellow]Status: Processing...[/bold yellow]")
        spinner.styles.display = "block"

        # 3. Launch async background worker for CrewAI kickoff
        self.process_agent_task(user_text)

    @work(thread=True)
    def process_agent_task(self, user_request: str) -> dict:
        """Executes the CrewAI task in a background worker thread."""
        if not self.agent_crew:
            return {"routing": "", "execution": "Error: Agent system not initialized."}

        try:
            result = self.agent_crew.crew().kickoff(inputs={"user_request": user_request})
            
            routing_out = ""
            execution_out = ""

            if hasattr(result, "tasks_output") and len(result.tasks_output) >= 2:
                routing_out = result.tasks_output[0].raw
                execution_out = result.tasks_output[1].raw
            else:
                execution_out = result.raw if hasattr(result, "raw") else str(result)
                routing_out = "Direct routing completed."

            return {"routing": routing_out, "execution": execution_out}
        except Exception as e:
            return {"routing": "Routing error encountered.", "execution": f"Error executing task: {str(e)}"}

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Callback when the background worker thread completes."""
        if event.state == WorkerState.SUCCESS:
            data = event.worker.result
            chat_container = self.query_one("#chat-container", ScrollableContainer)
            header_info = self.query_one("#header-info", Label)
            spinner = self.query_one("#spinner-container", Container)

            # Hide spinner
            spinner.styles.display = "none"
            header_info.update(f"[bold cyan]AI COMMAND LINE AGENT[/bold cyan]  |  [dim]Model: {self.model_name}[/dim]  |  [bold green]Status: Ready[/bold green]")

            # Mount Router and Execution output cards
            if data.get("routing"):
                chat_container.mount(RouterCard(data["routing"]))
            if data.get("execution"):
                chat_container.mount(ExecutionCard(data["execution"]))

            chat_container.scroll_end(animate=True)


def run_tui():
    app = CLIAgentApp()
    app.run()


if __name__ == "__main__":
    run_tui()
