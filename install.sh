#!/usr/bin/env bash
# PRIMAX-AI — One-command setup
set -euo pipefail

echo "🧠 PRIMAX-AI — Installer"
echo "========================"

if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

# Prefer uv if available (much faster), otherwise fall back to pip + venv
if command -v uv &>/dev/null; then
    echo "→ Using uv (fast mode)"
    uv venv .venv --python 3.11
    # shellcheck disable=SC1091
    source .venv/bin/activate
    uv pip install -e ".[dev]"
else
    echo "→ Using standard venv + pip"
    python3 -m venv .venv
    # shellcheck disable=SC1091
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -e ".[dev]"
fi

echo ""
echo "✅ Environment ready."
echo ""
echo "Next steps:"
echo "  1. Copy .env.example → .env and fill in keys (especially NIM_API_KEY and Ollama)"
echo "  2. Start Ollama: ollama serve"
echo "  3. Launch options:"
echo "       python -m src.tui.app          # Textual TUI"
echo "       python src/main.py             # FastAPI server"
echo "       python src/nexus_cli.py agents # List local agents"
echo "       python -m src.mcp_server.primax_mcp_server   # MCP server for Claude Code"
echo ""
echo "🧠 Welcome to PRIMAX-AI"