#!/bin/sh
set -e

REPO="Ayushsingh-02082004/ai-terminal-assistant"
INSTALL_DIR="$HOME/.cli-agent/bin"
EXE_PATH="$INSTALL_DIR/cli-agent"
FORCE_FALLBACK=0

echo "=== Installing CLI Agent (cli-agent) ==="

# Detect OS and Arch
OS="$(uname -s)"
ARCH="$(uname -m)"

if [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "x86_64" ]; then
        BINARY_NAME="cli-agent-darwin-amd64"
    elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
        BINARY_NAME="cli-agent-darwin-arm64"
    else
        echo "Unsupported Mac architecture: $ARCH"
        exit 1
    fi
elif [ "$OS" = "Linux" ]; then
    if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then
        BINARY_NAME="cli-agent-linux-amd64"
    elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
        echo "Notice: Linux ARM64 detected. Switching to self-healing Python installation."
        FORCE_FALLBACK=1
    else
        echo "Unsupported Linux architecture: $ARCH"
        exit 1
    fi
else
    echo "Unsupported Operating System: $OS"
    exit 1
fi

mkdir -p "$INSTALL_DIR"

if [ "$FORCE_FALLBACK" = "0" ]; then
    DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/$BINARY_NAME"

    echo "Downloading $BINARY_NAME from GitHub Releases..."
    if curl -fsSL "$DOWNLOAD_URL" -o "$EXE_PATH"; then
        chmod +x "$EXE_PATH"
        echo "Successfully downloaded cli-agent to $EXE_PATH"
    else
        echo "Notice: Could not download pre-built binary. Switching to Python installation..."
        FORCE_FALLBACK=1
    fi
fi

# Verify binary compatibility or run fallback
BINARY_OK=0
if [ "$FORCE_FALLBACK" = "0" ] && [ -x "$EXE_PATH" ]; then
    echo "Verifying executable binary compatibility..."
    if "$EXE_PATH" --help >/dev/null 2>&1 || "$EXE_PATH" version >/dev/null 2>&1 || "$EXE_PATH" help >/dev/null 2>&1; then
        echo "Binary verification successful!"
        BINARY_OK=1
    fi
fi

if [ "$BINARY_OK" = "0" ]; then
    echo "Configuring self-healing Python virtual environment..."

    if ! command -v git >/dev/null 2>&1; then
        echo "Error: 'git' is required for fallback installation."
        exit 1
    fi

    PYTHON_CMD=""
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        echo "Error: Python 3.10+ is required for fallback installation."
        exit 1
    fi

    if ! "$PYTHON_CMD" -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >/dev/null 2>&1; then
        echo "Error: Python 3.10 or higher is required for fallback installation."
        echo "Found version: $($PYTHON_CMD --version 2>&1)"
        exit 1
    fi

    VENV_DIR="$HOME/.cli-agent/venv"
    REPO_DIR="$HOME/.cli-agent/repo"
    rm -rf "$VENV_DIR" "$REPO_DIR"

    echo "Fetching repository source for native compilation..."
    if ! git clone --depth 1 "https://github.com/$REPO.git" "$REPO_DIR"; then
        echo "Error: Failed to clone repository source from GitHub."
        exit 1
    fi

    echo "Creating virtual environment..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    
    echo "Installing backend dependencies..."
    "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
    if ! "$VENV_DIR/bin/pip" install -r "$REPO_DIR/backend/requirements.txt"; then
        echo "Error: Failed to install Python dependencies."
        exit 1
    fi

    # Replace binary location with self-healing launcher wrapper
    cat << EOF > "$EXE_PATH"
#!/bin/sh
export PYTHONPATH="$REPO_DIR/backend/src:\$PYTHONPATH"
exec "$VENV_DIR/bin/python" "$REPO_DIR/backend/run.py" "\$@"
EOF
    chmod +x "$EXE_PATH"
    echo "Self-healing Python installation completed successfully!"
fi

# Detect and configure shell profile
SHELL_PROFILE=""
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_PROFILE="$HOME/.bash_profile"
elif [ -f "$HOME/.profile" ]; then
    SHELL_PROFILE="$HOME/.profile"
fi

case ":$PATH:" in
    *":$INSTALL_DIR:"*) ;;
    *)
        if [ -n "$SHELL_PROFILE" ]; then
            if ! grep -qs "$INSTALL_DIR" "$SHELL_PROFILE"; then
                echo "Adding $INSTALL_DIR to $SHELL_PROFILE..."
                echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_PROFILE"
            fi
        fi

        if [ -f "$HOME/.config/fish/config.fish" ]; then
            if command -v fish >/dev/null 2>&1; then
                fish -c "fish_add_path $INSTALL_DIR" 2>/dev/null || true
            fi
        fi
        ;;
esac

echo ""
echo "=== Installation Complete! ==="
echo "Open any terminal window and type: cli-agent"
