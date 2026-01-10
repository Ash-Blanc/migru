#!/bin/bash
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Ensure uv is in the PATH for the current session if it was just installed
    # This path might vary depending on OS, but typically it's ~/.cargo/bin or ~/.local/bin
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    elif [ -f "$HOME/.local/bin/env" ]; then # Fallback/alternative check
         export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # Verify installation
    if ! command -v uv &> /dev/null; then
        echo "Error: uv installation failed or not found in PATH. Please restart your shell or add uv to your PATH manually."
        exit 1
    fi
else
    echo "uv is already installed."
fi

echo "Installing dependencies..."
uv sync

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please open '.env' and add your API keys before running the app!"
else
    echo ".env file already exists."
fi

echo "Setup complete! You can now run the application with:"
echo "uv run -m app.main"
