"""CSS stylesheets for the Textual TUI Application."""

APP_CSS = """
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
    height: auto;
    margin: 0;
    padding: 0;
    border-top: solid $secondary;
    overflow-x: hidden;
}

#debug-log {
    height: 10;
    background: $surface-darken-1;
    overflow-x: hidden;
}
"""
