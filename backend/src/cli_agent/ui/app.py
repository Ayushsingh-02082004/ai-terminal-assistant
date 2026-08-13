import sys
import os
import re
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Input, Static, LoadingIndicator, Collapsible, Log, Label
from textual.binding import Binding
from textual import work
from textual.worker import Worker, WorkerState

from cli_agent.crew import CLIAgentCrew
from cli_agent.services import (
    try_fast_path_execution, session_memory,
    get_system_info, get_env_context_string, history_manager
)
from cli_agent.ui.stream import StreamRedirector
from cli_agent.ui.styles import APP_CSS
from cli_agent.ui.components import UserMessage, RouterCard, ExecutionCard


class CLIAgentApp(App):
    """A modern, modular full-screen Terminal User Interface (TUI) for the CLI Agent."""

    TITLE = "AI Command Line Agent"
    SUB_TITLE = "CrewAI Powered Shell, File, Code & Git Automation"
    CSS = APP_CSS

    BINDINGS = [
        Binding("ctrl+d", "toggle_debug", "Toggle Debug Logs", show=True),
        Binding("ctrl+c", "quit", "Exit", show=True),
    ]

    def __init__(self):
        super().__init__()
        os.environ["CREWAI_TRACING_ENABLED"] = "false"
        os.environ["OTEL_SDK_DISABLED"] = "true"
        os.environ["LITELLM_LOG"] = "ERROR"
        
        self.agent_crew: Optional[CLIAgentCrew] = None
        self.model_name = os.getenv("OLLAMA_MODEL_NAME", "gemma4:31b-cloud")
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        self.sys_info = get_system_info()
        self.history_index = -1

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        env_banner = f"[bold cyan]AI COMMAND LINE AGENT[/bold cyan]  |  [dim]OS: {self.sys_info['os']}  |  Branch: {self.sys_info['git_branch']}[/dim]  |  [bold green]Status: Ready[/bold green]"
        yield Label(env_banner, id="header-info")
        
        with ScrollableContainer(id="chat-container"):
            yield Static(f"[dim]Auto-detected Environment: {get_env_context_string()}\nType commands in plain English below or press Up/Down for command history. Press Ctrl+D for Debug Logs.[/dim]")
            
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
            log_widget.write_line(f"[SYSTEM] CrewAI Agent system initialized. Env: {get_env_context_string()}")
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

    def on_key(self, event) -> None:
        """Handle Up/Down arrow key navigation for command history."""
        input_widget = self.query_one("#cmd-input", Input)
        if not input_widget.has_focus:
            return

        entries = history_manager.get_entries()
        if not entries:
            return

        if event.key == "up":
            if self.history_index == -1:
                self.history_index = len(entries) - 1
            elif self.history_index > 0:
                self.history_index -= 1
            input_widget.value = entries[self.history_index]
            input_widget.cursor_position = len(input_widget.value)
        elif event.key == "down":
            if self.history_index != -1:
                if self.history_index < len(entries) - 1:
                    self.history_index += 1
                    input_widget.value = entries[self.history_index]
                else:
                    self.history_index = -1
                    input_widget.value = ""
                input_widget.cursor_position = len(input_widget.value)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission from the Input widget."""
        user_text = event.value.strip()
        if not user_text:
            return

        history_manager.add(user_text)
        self.history_index = -1

        input_widget = self.query_one("#cmd-input", Input)
        input_widget.value = ""

        if user_text.lower() in ["exit", "quit", "q"]:
            self.exit()
            return

        chat_container = self.query_one("#chat-container", ScrollableContainer)
        header_info = self.query_one("#header-info", Label)
        spinner = self.query_one("#spinner-container", Container)

        await chat_container.mount(UserMessage(user_text))
        chat_container.scroll_end(animate=False)

        header_info.update(f"[bold cyan]AI COMMAND LINE AGENT[/bold cyan]  |  [dim]Branch: {self.sys_info['git_branch']}[/dim]  |  [bold yellow]Status: Processing...[/bold yellow]")
        spinner.styles.display = "block"

        self.process_agent_task(user_text)

    @work(thread=True)
    def process_agent_task(self, user_request: str) -> dict:
        """Executes the CrewAI task in a background worker thread with managed session memory."""
        req_clean = user_request.strip()
        if req_clean.lower() in ["clear", "/clear", "reset"]:
            session_memory.clear()
            return {"routing": "**[Memory System]** Session memory cleared.", "execution": "Conversation context has been reset."}

        try:
            fast_res = try_fast_path_execution(req_clean)
            if fast_res:
                session_memory.add_turn(req_clean, "Fast-Path", fast_res[1])
                return {"routing": fast_res[0], "execution": fast_res[1]}

            agent_crew = CLIAgentCrew()
            history_ctx = session_memory.get_formatted_context()
            env_ctx = get_env_context_string()
            result = agent_crew.crew().kickoff(inputs={
                "user_request": req_clean,
                "conversation_history": history_ctx,
                "system_env_context": env_ctx
            })
            
            routing_out = ""
            execution_out = ""

            if hasattr(result, "tasks_output") and len(result.tasks_output) >= 2:
                routing_out = result.tasks_output[0].raw
                execution_out = result.tasks_output[1].raw
            else:
                execution_out = result.raw if hasattr(result, "raw") else str(result)
                routing_out = "Direct routing completed."

            session_memory.add_turn(req_clean, "Agent", execution_out)
            return {"routing": routing_out, "execution": execution_out}
        except Exception as e:
            err_msg = str(e)
            if "execution timed out" in err_msg:
                err_msg = "Task execution timed out while waiting for model generation. Consider breaking down your prompt."
            elif "Task '" in err_msg:
                err_msg = re.sub(r"Task '.*?' ", "", err_msg)
            return {"routing": "Routing error encountered.", "execution": f"Error executing task: {err_msg}"}

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Callback when the background worker thread completes."""
        if event.state == WorkerState.SUCCESS:
            data = event.worker.result
            chat_container = self.query_one("#chat-container", ScrollableContainer)
            header_info = self.query_one("#header-info", Label)
            spinner = self.query_one("#spinner-container", Container)

            spinner.styles.display = "none"
            header_info.update(f"[bold cyan]AI COMMAND LINE AGENT[/bold cyan]  |  [dim]Model: {self.model_name}[/dim]  |  [bold green]Status: Ready[/bold green]")

            if data.get("routing"):
                chat_container.mount(RouterCard(data["routing"]))
            if data.get("execution"):
                chat_container.mount(ExecutionCard(data["execution"]))

            chat_container.scroll_end(animate=True)


def run_tui():
    app = CLIAgentApp()
    app.run()
