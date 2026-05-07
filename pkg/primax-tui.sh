#!/bin/bash
# PRIMAX AI TUI Launcher
# WATERMARK: PRIMAX-AI-LAUNCHER-BSP-2025

set -e

echo "🚀 Starting PRIMAX AI TUI..."
echo "   Watermark: PRIMAX-AI-TUI-BSP-2025"
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.9+"
    exit 1
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. LLM features will be limited."
    echo "   Install from: https://ollama.com"
else
    echo "✅ Ollama found"
fi

# Check if PRIMAX-AI directory exists
PRIMAX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Run TUI
cd "$PRIMAX_DIR"
exec python -m src.tui.app "$@"