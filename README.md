# PRIMAX-AI

🔒 Self-learning neuromorphic intelligence — local-first, $0/month, multi-agent.

> Watermark: `PRIMAX-AI-BSP-2025` · License: Proprietary (Bakery Street Project)

## 🌟 Support This Project

**[💙 Become a Sponsor](https://github.com/sponsors/kilisan)** — Get premium features, priority support, and more!

| Free | Supporter $5 | Advocate $15 | Pro $50 | Enterprise $250+ |
|------|:---:|:---:|:---:|:---:|
| Core AI | ✅ | ✅ | ✅ | ✅ | ✅ |
| Basic analysis | ✅ | ✅ | ✅ | ✅ | ✅ |
| Early access | — | ✅ | ✅ | ✅ | ✅ |
| Advanced insights | — | — | ✅ | ✅ | ✅ |
| Consulting | — | — | — | 2h/mo | 4h/mo |
| Enterprise SLA | — | — | — | — | ✅ |

👉 **[See all features →](PREMIUM.md)** | **[Browse sponsors →](SPONSORS.md)**

## What it does

| Component | Role |
|-----------|------|
| **FastAPI server** (`src/main.py`) | HTTP API — `/health`, `/api/v1/chat`, `/api/v1/automate`, `/api/v1/analyze-repo`, `/api/v1/ollama/query` |
| **TUI** (`src/tui/app.py`, Textual) | Interactive shell — `/dragon`, `/code`, `/repo`, `/scan`, `/nexus`, `/brain`, `/clear` |
| **MCP server** (`src/mcp_server/primax_mcp_server.py`) | Exposes 4 tools to Claude Code: `primax_chat`, `primax_analyze_repo`, `primax_brain_analysis`, `primax_code_scan` |
| **Neuromorphic core** (`src/brain/neuromorphic_core.py`) | Graph-eigenvalue, SNN, dynamic-systems analysis (NumPy/SymPy, no ML) |
| **GitHub scanner** (`src/github_scanner/scanner.py`) | Repo + organization analysis via `gh` CLI |
| **Vault** (`src/vault_manager.py`) | AES-256-GCM secret store + `~/my-app-vault/secrets/.env` loader |
| **Supabase client** (`src/db/supabase_client.py`) | Async pgvector for embeddings + query logs |
| **Nexus adapter** (`src/nexus_adapter.py`) | In-process multi-agent orchestrator (5 agents) — **no external CLI** |
| **Nexus CLI** (`src/nexus_cli.py`) | Thin local command wrapper around the in-process adapter — `nexus agents`, `nexus task`, `nexus run` |

## Quick start

```bash
# 1. Start Ollama (local LLM daemon)
systemctl --user start ollama

# 2. Generate + store API key on first run
mkdir -p ~/my-app-vault/secrets
python3 -c "import secrets; print(f'PRIMAX_API_KEY={secrets.token_urlsafe(32)}')" \
  > ~/my-app-vault/secrets/.env
chmod 600 ~/my-app-vault/secrets/.env

# 3. Launch
primax-tui                              # interactive TUI
# or
nexus agents                            # list local Nexus agents
# or
nexus run /home/kilisan/dev/pauliens_sky/sentinel-team.yaml
# or
uvicorn src.main:app --port 8000        # HTTP API
# or
docker run -p 8000:8000 \
  -e PRIMAX_API_KEY=$KEY primax-ai:latest
```

## Configuration

| Env var | Default | Purpose |
|---------|---------|---------|
| `PRIMAX_API_KEY` | (must be set) | HTTP `X-API-Key` auth. Auto-loaded from `~/my-app-vault/secrets/.env` |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Where Ollama daemon listens |
| `OLLAMA_GENERATION_TIMEOUT` | `300` | Seconds before giving up on a generation. Bump if Optimus on CPU is slow. |
| `GH_AUTH_TIMEOUT` | `5` | Quick `gh auth status` budget |
| `GH_COMMAND_TIMEOUT` | `30` | Per-`gh` invocation budget |
| `GROQ_API_KEY` | _unset_ | Optional cloud LLM fallback. If unset, Ollama serves all traffic. |
| `NIM_API_KEY` | _unset_ | NVIDIA NIM cloud fallback (free tier). |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | _unset_ | Optional — enables embeddings + query logs |

All env vars override the corresponding entries in `model_router.json`.

## Models

`model_router.json` resolves intents → models:

```json
{
  "models": {
    "optimus_prime": { "model": "optimus-prime-local:latest", "fallback": "qwen2.5-coder:1.5b" },
    "dragon_wise":   { "model": "primax-dragon-coder:latest", "fallback": "qwen2.5:7b"        }
  },
  "routing_rules": {
    "coding": "optimus_prime",
    "wisdom": "dragon_wise",
    "creative": "dragon_wise",
    "default": "dragon_wise"
  }
}
```

Models live in **local Ollama** (`~/.ollama/models`), never in Supabase. See `database/research_docs.md` § "Storage Tiers" for the rationale.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `PRIMAX_API_KEY not set - API authentication will be disabled` | First run, no vault | Run the Quick Start step 2 |
| `Groq API key not available - LLM features disabled` (DEBUG only now) | No `GROQ_API_KEY` | Ignore — Ollama fallback handles requests. Or sign up at console.groq.com/keys |
| TUI hangs on `/dragon hello` | Old subprocess-based query timed out at 30 s | Already fixed — pull latest, ensure `pip install ollama>=0.3.0` |
| `gh repo view` fails with timeout | Slow network or paged response | Bump `GH_COMMAND_TIMEOUT` env var |
| MCP server "Failed to connect" in `claude mcp list` | Stdio handshake error | Check `python3 src/mcp_server/primax_mcp_server.py < /dev/null` runs cleanly; reinstall `mcp` package if needed |

## MCP integration with Claude Code

Already registered locally:

```bash
claude mcp add primax-ai python3 /home/kilisan/primax-ai/src/mcp_server/primax_mcp_server.py
```

Verify: `claude mcp list | grep primax-ai` → `✓ Connected`. Smoke tests at `tests/mcp_smoke.md`.

## OpenCode integration

PRIMAX-AI is also available as an OpenCode primary agent at `~/.config/opencode/agents/primax-ai.md` (reference copy in `database/PRIMAX_SYSTEM_PROMPT.md`). Invoke with `opencode` (default primary) or `/agent primax-ai` mid-session.

## Architecture

```
       ┌────────┐  HTTP   ┌──────────┐  stdio  ┌──────────────┐
Client ├───────►│ FastAPI ├────────►│ Ollama   │             │ MCP server  │
       │        │ (main)  │         │ (local)  │  pulls from │ (4 tools)   │
       └────────┘         └────┬────┘          └──────┬──────┘
                               │                       │
                               ▼                       ▼
                          ┌─────────┐         ┌──────────────┐
                          │Supabase │         │ Claude Code  │
                          │pgvector │         │   client     │
                          └─────────┘         └──────────────┘
```

## Hardware constraints

- **RAM**: 7.6 GB physical (3.8 GB available) — Optimus 24B (14 GB on disk) is memory-bound on CPU. Use Dragon (986 MB) for chat, Optimus for batch.
- **GPU**: none. CPU-only inference, 4-8 effective threads.
- **Swap**: 23 GB total (degradation past 15 GB used).

For Optimus production work, deploy on RunPod RTX 4090 ($0.34/hr) or Lambda Labs A10 ($1.29/hr).

## License

Proprietary — Bakery Street Project. See `LICENSE_PROPRIETARY.md`.

## Security

See `SECURITY.md`. Vulnerability reports: `kiliaanv2@gmail.com`.
