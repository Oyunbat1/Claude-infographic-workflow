#!/bin/bash
# Mac/Linux — run infographic generator
# Usage: ./run.sh "Your prompt here"

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Check Python ──────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "Python3 not found. Installing via Homebrew..."
    if ! command -v brew &>/dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python3
fi

# ── Check replicate package ───────────────────────────────────
if ! python3 -c "import replicate" &>/dev/null; then
    echo "Installing replicate package..."
    python3 -m pip install replicate --break-system-packages --quiet
fi

if ! python3 -c "import PIL" &>/dev/null; then
    echo "Installing Pillow package..."
    python3 -m pip install Pillow --break-system-packages --quiet
fi

# ── Load .env ─────────────────────────────────────────────────
if [ -f "$DIR/.env" ]; then
    export $(grep -v '^#' "$DIR/.env" | xargs)
else
    echo "ERROR: .env file not found. Create it with: REPLICATE_API_TOKEN=your_token"
    exit 1
fi

# ── Run ───────────────────────────────────────────────────────
if [ -z "$1" ]; then
    python3 "$DIR/run.py" "${@}"
else
    python3 "$DIR/run.py" --prompt "$1" "${@:2}"
fi
