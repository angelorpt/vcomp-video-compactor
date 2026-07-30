#!/usr/bin/env bash
set -euo pipefail

echo "==> vcomp install script"
echo ""

# Check prerequisites
if ! command -v ffmpeg &>/dev/null; then
    echo "[ERROR] ffmpeg not found. Install it first:"
    echo "  sudo apt install ffmpeg   # Ubuntu/Debian"
    echo "  sudo dnf install ffmpeg   # Fedora"
    exit 1
fi

if ! ffmpeg -version 2>&1 | grep -q libx265; then
    echo "[ERROR] ffmpeg lacks libx265 support. Install a build with libx265."
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 not found."
    exit 1
fi

# Install Python dependencies
echo "==> Installing Python dependencies (typer, rich)..."
python3 -m pip install --user typer rich 2>&1 || {
    echo "[ERROR] Failed to install Python packages."
    exit 1
}

# Install the package
echo "==> Installing vcomp..."
python3 -m pip install --user -e "$(dirname "$0")" 2>&1 || {
    echo "[ERROR] pip install failed."
    exit 1
}

BIN_DIR="${HOME}/.local/bin"
if ! echo "$PATH" | grep -q "${BIN_DIR}"; then
    echo ""
    echo "NOTE: Add ${BIN_DIR} to your PATH if not already:"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
fi

echo ""
echo "==> vcomp installed successfully!"
echo "  Run: vcomp --help"
