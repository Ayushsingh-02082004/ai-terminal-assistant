#!/bin/sh
set -e

REPO="Ayushsingh-02082004/ai-terminal-assistant"
INSTALL_DIR="$HOME/.cli-agent/bin"
EXE_PATH="$INSTALL_DIR/cli-agent"

echo "=== Installing CLI Agent (cli-agent) ==="

# Detect OS and Arch
OS="$(uname -s)"
ARCH="$(uname -m)"

if [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "i386" ]; then
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
    else
        echo "Unsupported Linux architecture: $ARCH"
        exit 1
    fi
else
    echo "Unsupported Operating System: $OS"
    exit 1
fi

mkdir -p "$INSTALL_DIR"

DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/$BINARY_NAME"

echo "Downloading $BINARY_NAME from GitHub Releases..."
curl -fsSL "$DOWNLOAD_URL" -o "$EXE_PATH"
chmod +x "$EXE_PATH"

echo "Successfully downloaded cli-agent to $EXE_PATH"

echo "Verifying executable binary compatibility..."
if "$EXE_PATH" --help >/dev/null 2>&1 || "$EXE_PATH" version >/dev/null 2>&1 || "$EXE_PATH" help >/dev/null 2>&1; then
    echo "Binary verification successful!"
else
    echo "Notice: Standalone binary requires native library fallback on this system."
    echo "Configuring self-healing Python virtual environment..."
    PYTHON_CMD=""
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        echo "Error: Python 3 is required for fallback installation."
        exit 1
    fi

    VENV_DIR="$HOME/.cli-agent/venv"
    REPO_DIR="$HOME/.cli-agent/repo"
    rm -rf "$VENV_DIR" "$REPO_DIR"

    echo "Fetching repository source for native compilation..."
    git clone --depth 1 "https://github.com/$REPO.git" "$REPO_DIR" >/dev/null 2>&1

    "$PYTHON_CMD" -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip "setuptools<70.0.0" wheel >/dev/null 2>&1
    "$VENV_DIR/bin/pip" install -r "$REPO_DIR/backend/requirements.txt" >/dev/null 2>&1

    # Replace binary location with self-healing launcher wrapper
    cat << EOF > "$EXE_PATH"
#!/bin/sh
export PYTHONPATH="$REPO_DIR/backend/src:\$PYTHONPATH"
exec "$VENV_DIR/bin/python" "$REPO_DIR/backend/run.py" "\$@"
EOF
    chmod +x "$EXE_PATH"
    echo "Self-healing Python installation completed successfully!"
fi

# Check if PATH contains install directory
case ":$PATH:" in
    *":$INSTALL_DIR:"*) ;;
    *)
        SHELL_PROFILE=""
        if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
            SHELL_PROFILE="$HOME/.zshrc"
        elif [ -f "$HOME/.bashrc" ]; then
            SHELL_PROFILE="$HOME/.bashrc"
        fi

        if [ -n "$SHELL_PROFILE" ]; then
            echo "Adding $INSTALL_DIR to $SHELL_PROFILE..."
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_PROFILE"
        fi
        ;;
esac

echo ""
echo "=== Installation Complete! ==="
echo "Open any terminal window and type: cli-agent"
