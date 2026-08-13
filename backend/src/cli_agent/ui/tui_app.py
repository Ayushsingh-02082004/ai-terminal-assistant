"""
Module forwarder for backward compatibility with cli_agent.ui.tui_app
"""
from cli_agent.ui.app import CLIAgentApp, run_tui

__all__ = ["CLIAgentApp", "run_tui"]

if __name__ == "__main__":
    run_tui()
