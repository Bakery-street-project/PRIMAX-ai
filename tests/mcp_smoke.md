# PRIMAX MCP smoke test

Server: `python3 /home/kilisan/primax-ai/src/mcp_server/primax_mcp_server.py`
Registered to Claude Code via: `claude mcp add primax-ai python3 /home/kilisan/primax-ai/src/mcp_server/primax_mcp_server.py`

Verify with: `claude mcp list | grep primax-ai`
Expected: `primax-ai: ... - ✓ Connected`

## Tools exposed

| Name | Input | Behavior |
|------|-------|----------|
| `primax_chat` | `message`, `model` (`dragon` or `coding`) | Streams response from local Ollama via the official `ollama` Python client |
| `primax_analyze_repo` | `repo` (`owner/name`) | Calls `gh repo view --json …` (30 s timeout) |
| `primax_brain_analysis` | `analysis_type` (`graph`, `snn`, `dynamic`) | Static placeholder for the neuromorphic core wiring |
| `primax_code_scan` | `path` (default `.`) | Local AST scan entry point |

## Manual tests (run from a Claude Code session)

```
> use primax_chat to ask "what is your watermark?"
expected: response mentioning PRIMAX-AI-BSP-2025

> use primax_analyze_repo for ensdomains/ens-metadata-service
expected: JSON with name, description, stargazerCount, forkCount

> use primax_brain_analysis with analysis_type="graph"
expected: "Brain graph analysis: Neural network active"

> use primax_code_scan with path=/home/kilisan/primax-ai/src
expected: scan summary
```

## Known issues

- **First call cold-start** — Ollama loads the 14 GB Optimus model on first `primax_chat coding` request, taking ~60-120 s. Use `primax_chat dragon` (986 MB) for fast queries.
- **No anthropic credentials in OpenCode** — the agent at `~/.config/opencode/agents/primax-ai.md` defaults to `openai/gpt-4o`; switch via the `model:` field if preferred.
