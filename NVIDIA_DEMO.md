# NVIDIA Demo Guide – PRIMAX-AI

This guide lets you quickly evaluate **PRIMAX-AI**, the self-learning neuromorphic intelligence system.

## One-Command Setup

```bash
git clone https://github.com/Bakery-street-project/PRIMAX-ai.git
cd PRIMAX-ai

bash install.sh
cp .env.example .env
# Edit .env and set at minimum:
# OLLAMA_HOST=http://127.0.0.1:11434
# (Optional but recommended) NIM_API_KEY=your_key
```

## Launch Options

### Interactive TUI (recommended)
```bash
python -m src.tui.app
```

### FastAPI Server
```bash
python src/main.py
# Then visit http://localhost:8000/docs
```

### List Local Agents
```bash
python src/nexus_cli.py agents
```

### MCP Server (for Claude Code / Cursor)
```bash
python -m src.mcp_server.primax_mcp_server
```

## Key Features for NVIDIA

- Leaky Integrate-and-Fire (LIF) spiking neural network core
- Explicit NVIDIA NIM fallback support (`NIM_API_KEY`)
- Multi-agent orchestration via Nexus
- Local-first with optional cloud acceleration
- MCP server for seamless integration with agentic coding tools

This system is designed to move from pure CPU inference to full NVIDIA-accelerated neuromorphic workloads.
