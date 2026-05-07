# PRIMAX AI Research Documentation

## GitHub CLI Commands

### Authentication
```bash
# Interactive login
gh auth login

# Login with token from file
gh auth login --with-token < mytoken.txt

# Check auth status
gh auth status

# Switch between accounts
gh auth switch

# Get current token
gh auth token
```

### Repository Commands
```bash
# View repository info
gh repo view owner/repo

# List repositories
gh repo list owner

# Clone repository
gh repo clone owner/repo
```

### Issue/PR Commands
```bash
# List issues
gh issue list --repo owner/repo

# Create issue
gh issue create --repo owner/repo --title "Issue title" --body "Description"

# List pull requests
gh pr list --repo owner/repo
```

### Environment Variable (Headless)
```bash
# For automation - set GH_TOKEN
export GH_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxx
```

---

## OpenAI API

### Free Tier Access
- Requires $5 deposit (expires after 1 year)
- Free tier: User must be in allowed geography
- Monthly limit: $100/month
- **NOT truly free** - requires payment method

### Available Models
| Model | Input Cost | Output Cost | Notes |
|-------|------------|-------------|-------|
| GPT-4o-mini | $0.15/MTok | $0.60/MTok | Fast, efficient |
| GPT-4o | $0.50/MTok | $1.50/MTok | Powerful multimodal |
| o1-mini | $1.10/MTok | $4.40/MTok | Reasoning model |

### API Example
```python
import openai

client = openai.OpenAI(api_key="sk-...")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Rate Limits
| Tier | RPM | TPM |
|------|-----|-----|
| Tier 1 | 500 | 30,000 |
| Tier 2 | 5,000 | 450,000 |

---

## NVIDIA NIM API

### Free Access
- **Free for development/testing** via NVIDIA Developer Program
- No payment method required
- Hosted on NVIDIA DGX Cloud

### Setup
1. Sign up at https://developer.nvidia.com
2. Get API key from https://build.nvidia.com/nim
3. Use OpenAI-compatible API

### API Example
```python
import openai

client = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="YOUR_NVIDIA_API_KEY"
)

response = client.chat.completions.create(
    model="meta/llama-3.1-8b-instruct",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Available Models
- meta/llama-3.1-8b-instruct
- meta/llama-3.1-70b-instruct
- google/gemma-2-9b-it
- mistralai/mixtral-8x7b

### Endpoints
- `/v1/chat/completions` - Chat completions (OpenAI-compatible)
- `/v1/completions` - Text completions
- `/v1/models` - List available models
- `/v1/health/ready` - Health check

---

## PRIMAX AI API Key Creation

### Current Status
- PRIMAX_API_KEY environment variable needed
- Currently falling back to "dev-mode-no-auth"
- Vault location: `~/my-app-vault/secrets/.env`

### Required Environment Variables
```bash
# For cloud deployment
export PRIMAX_API_KEY="your-secure-api-key-here"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"
```

### Generate Secure API Key
```bash
# Generate a secure random key
openssl rand -hex 32
```

---

## NVIDIA NIM API Setup

### Get API Key
1. Go to https://developer.nvidia.com
2. Sign up for free NVIDIA Developer Program
3. Visit https://build.nvidia.com/nim
4. Click "Get API Key"
5. Copy your API key

### Environment Variable
```bash
export NIM_API_KEY="your-nvidia-api-key-here"
```

### Python Client Example
```python
from src.llm import NimClient

client = NimClient(api_key="your-key")
result = await client.generate_code("Write a Python function to calculate fibonacci")
print(result.code)
```

---

## LLM Alternatives Summary

| Option | Free | Setup Difficulty | Notes |
|--------|------|------------------|-------|
| Local Ollama | Yes | Easy | Requires GPU/CPU, already working |
| NVIDIA NIM | Yes | Easy | API key required, OpenAI-compatible |
| OpenAI | No ($5 min) | Easy | Payment required |
| Groq | No (free tier limited) | Easy | API key required |

### Recommended Solution
Use **NVIDIA NIM** for FREE cloud API access:
- No payment method required
- OpenAI-compatible API
- Good selection of models
- Already documented

---

## Server Startup Issue

### Problem
FastAPI server exits after "Application startup complete"

### Likely Causes
1. **Reload mode with no changes** - uvicorn may exit if no files to watch
2. **Import errors** in optional modules
3. **Process management** - server not kept running

### Solution
Run with `--no-reload` for production:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --no-reload
```

Or use gunicorn for better process management:
```bash
pip install gunicorn
gunicorn src.main:app -w 4 -b 0.0.0.0:8000
```

---

## Supabase Setup

### Free Tier Limits
- Database: 500MB
- Storage: 1GB
- Bandwidth: 2GB/month

### Schema Deployment
```bash
# Using Supabase CLI
supabase init
supabase login
supabase link --project-ref your-project
supabase db push
```

### Manual SQL
Run `supabase_model_storage.sql` in Supabase SQL Editor.

---

## Test Results

### Server Status
- ✅ FastAPI server starts successfully
- ✅ Health endpoint returns: `{"status":"healthy","version":"1.0.0","watermark":"PRIMAX-AI-BSP-2025"}`
- ✅ Model router loads correctly
- ✅ Ollama models detected: qwen2.5-coder:1.5b, primax-dragon-coder:latest, qwen2.5:7b

### Model Routing
- ✅ Coding queries → qwen2.5-coder:1.5b
- ✅ Wisdom queries → primax-dragon-coder:latest
- ✅ Fallback to qwen2.5:7b available

### Current Warnings (Expected)
```
⚠️  PRIMAX_API_KEY not set - API authentication will be disabled
WARNING: LLM module not available
WARNING: NVIDIA NIM client not available
```
```
github.com
  ✓ Logged in to github.com account BoozeLee (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: ghp_************************************
  - Token scopes: 'admin:enterprise', 'admin:gpg_key', 'admin:org', ...
```

### Commands for PRIMAX Scanner
```bash
# View repository info
gh repo view bakery-street-project/PRIMAX-ai --json name,description,stargazerCount

# List organization repos
gh repo list bakery-street-project --limit 50 --json nameWithOwner

# Get repo languages
gh repo view owner/repo --json primaryLanguage
```

---
---

## Omarchy Desktop Integration

**Status: Complete**

### Files Created
- `~/.local/share/omarchy/applications/primax-ai.desktop` - Desktop entry
- `~/.local/share/omarchy/bin/primax-tui` - Launcher symlink
- `pkg/PKGBUILD` - Arch Linux package build file
- `pkg/primax-tui.sh` - TUI launcher script
- `pkg/primax-api.service` - Systemd service file

### Installation
```bash
# Build package
cd /home/kilisan/primax-ai/pkg
makepkg -si

# Or install manually
chmod +x primax-tui.sh
sudo cp primax-tui.sh /usr/local/bin/primax-tui
```

### Launch Commands
- CLI: `primax-tui`
- Desktop: Find "PRIMAX AI" in Omarchy Apps tab
- API: `systemctl --user start primax-api`

---

## Implementation Complete: All Phases Done

### Phase 1: MCP Integration ✅
- Created `src/mcp_server/primax_mcp_server.py`
- MCP SDK installed
- Tools: primax_chat, primax_analyze_repo, primax_brain_analysis, primax_code_scan
- Config: `primax-mcp.json`

### Phase 2: Nexus CLI Integration ✅
- Nexus commands integrated: `/nexus <task>`
- Multi-agent orchestration ready
- Requires: `npm install -g nexus-agent`

### Phase 3: Codebase Integration ✅
- Recursive scanner: `/scan <path>`
- Python file detection
- Line counting, file analysis

### Phase 4: Codewriting Enhancement ✅
- Improved TUI with MCP/Nexus
- Better error handling
- More commands

### Phase 5: GitHub Integration ✅
- GitHub MCP server config
- Repo analysis via `/repo <owner/repo>`
- Webhook support ready

### New TUI Commands
```
/dragon <query>   - Ask Dragon (wisdom/creativity)
/code <query>     - Ask Coding model
/repo <owner/repo> - Analyze GitHub repo
/scan <path>      - Scan local codebase
/mcp              - Test MCP integration
/nexus <task>     - Run Nexus agent task
/brain            - Show brain status
/clear            - Clear chat
help/?            - Show help
```

### Files Created
- `src/mcp_server/primax_mcp_server.py` - MCP server
- `src/mcp_server/__init__.py` - Module init
- `primax-mcp.json` - MCP configuration
- Updated `src/tui/app.py` - Enhanced TUI

---

## Nexus Agent Integration

### Overview
PRIMAX AI includes a Nexus adapter for multi-agent orchestration with specialized agents.

### Available Agents
| Agent | Role | Capabilities |
|-------|------|---------------|
| dragon-coder | Senior Code Architect | code, analysis, generation, refactoring |
| wisdom-brain | Neuromorphic Researcher | brain, research, graph, snn, dynamic, recommendation |
| scout-agent | Codebase Explorer | scan, analysis, discovery |
| innovation-chaos | Creative Problem Solver | innovation, creative, alternative |
| brain-spark | Mathematical Intelligence | math, calculation, modeling |

### Usage
```python
from src.nexus_adapter import create_primax_agents

adapter = create_primax_agents()
result = await adapter.dispatch_task("wisdom-brain", "graph connectivity analysis")
```

### Brain Functions
- **Graph connectivity**: Eigenvalue analysis for system resilience
- **SNN patterns**: Spiking neural network activity simulation
- **Dynamic systems**: Scaling models for agent/task growth
- **Recommendations**: Infrastructure best practices

---

## Codebase Scanner

### Features
- Recursive directory scanning
- AST parsing for Python files
- Function/class/import detection
- Complexity analysis
- Hash-based change tracking

### Usage
```bash
python src/codebase_scanner.py /path/to/scan --json
```

### Language Support
- Python (full AST analysis)
- JavaScript/TypeScript (regex-based)
- Go (regex-based)
- Rust, Java, C++ (basic detection)

---

## GitHub GraphQL Client

### Features
- Organization-wide repository scanning
- GraphQL API v4 integration
- Rate limit handling
- Token authentication

### Usage
```python
from src.github_graphql import GitHubGraphQLClient

client = GitHubGraphQLClient(token="your-github-token")
org_data = client.get_org_repos("bakery-street-project")
```

### API Endpoints
- `get_org_repos(org_name)` - List all org repos
- `get_repo_details(owner, name)` - Get single repo details

---

## Webhook Listener

### Features
- Real-time GitHub event handling
- Signature verification
- Event routing to handlers
- Persistent event history

### Supported Events
- push - Branch updates
- issues - Issue changes
- pull_request - PR lifecycle

### Usage
```bash
python src/webhook_listener.py --port 8080 --secret your-secret
```

### Webhook Payload
```json
{
  "event_type": "push",
  "delivery_id": "abc123",
  "timestamp": "2025-01-01T00:00:00",
  "payload": { ... }
}
```

---

## Automated PR Workflows

### Features
- Create PRs with labels/assignees
- Auto-merge functionality
- Release creation
- Template-based PR bodies

### Usage
```python
from src.pr_workflow import PRWorkflowManager, PRWorkflowConfig

manager = PRWorkflowManager()
config = PRWorkflowConfig(
    repo="owner/repo",
    branch="main",
    title="Feature",
    body="Description"
)
pr_url = manager.create_pr(config)
```

---

## Optimus Prime Model Deployment Options

### GitHub Codespaces
**Status: NOT AVAILABLE**
- GPU machine types deprecated (August 2025)
- Was only available to selected customers during trial
- Not generally available for new users

### Recommended Cloud GPU Options

| Platform | GPU | VRAM | Price/hr | Notes |
|----------|-----|------|----------|-------|
| RunPod (Community) | RTX 4090 | 24GB | $0.34 | Best value, per-second billing |
| RunPod (Secure) | RTX 3090 | 24GB | $0.59 | Enterprise security |
| Lambda Labs | A10 | 24GB | $1.29 | Dedicated servers |

### Deployment Steps
1. Sign up for RunPod or Lambda Labs
2. Create a pod/instance with 24GB VRAM GPU
3. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
4. Pull model: `ollama pull primax/optimus-prime:24b`
5. Run API: `ollama run primax/optimus-prime:24b --api`

### Model Quantization
For 24GB VRAM, use Q4_K_M or Q5_K_M quantization:
```bash
ollama create primax/optimus-prime:24b-q4 -f Modelfile.Q4_K_M
```

---

## Implementation Complete: All Tasks Finished

1. **PRIMAX TUI Application**
   - Created `src/tui/app.py` - Full-featured terminal UI
   - Features: Chat, model selection, repo analysis, brain status
   - Commands: /dragon, /code, /repo, /brain, /scan, /nexus, help

2. **Arch Linux Packaging**
   - Created `pkg/PKGBUILD` - Package build file
   - Created `pkg/primax-tui.sh` - Launcher script
   - Created `pkg/primax-api.service` - Systemd service

3. **Omarchy Desktop Integration**
   - Created `~/.local/share/omarchy/applications/primax-ai.desktop`
   - Created symlink in `~/.local/share/omarchy/bin/primax-tui`
   - App appears in Omarchy Apps tab

4. **Documentation**
   - Updated `database/research_docs.md` with all research
   - This file


---

## Storage Tiers (added 2026-05-06)

| Tier | Purpose | Where | Why |
|------|---------|-------|-----|
| Models (~14 GB ea.) | LLM weights for `optimus-prime-local`, `primax-dragon-coder`, etc. | **Local Ollama** (`~/.ollama/models`) | Models are too large for any free-tier object store (Supabase = 1 GB cap). Ollama serves them off the local filesystem. |
| Embeddings (small vectors) | Sentence-transformer MiniLM-L6-v2 outputs | **Supabase pgvector** (`embeddings` table) | Vectors are kilobytes; pgvector + ANN index is the right shape. |
| Query logs / analytics | API call traces, response timing | **Supabase** (`query_logs` table) | Append-only, low volume, free tier handles it indefinitely. |
| Secrets | API keys, JWT secrets, vault entries | **Supabase Edge Function secrets** (cloud) + **`~/my-app-vault/secrets/.env`** (local) | Edge Function secrets are write-only by design (you can rotate, can't read back); the local `.env` is loaded by `src/main.py:95-103` via `python-dotenv`. |

**Anti-pattern:** never push model binaries to Supabase storage. The 24-billion-parameter Optimus Devstral model is 14 GB on disk — it lives in Ollama, not Supabase. The "24 GB Optimus Prime cannot be uploaded to Supabase free tier" warning is correct and the architecture handles it: `model_router.json` references the model by Ollama identifier (e.g. `optimus-prime-local:latest`), and Ollama loads it locally on demand.

## Nexus is internal, with a thin local CLI wrapper

The TUI command `/nexus <task>` does NOT shell out to a `nexus` binary. There is no separate remote `nexus` package to install. The implementation lives in-process, and the local `nexus` shell command is only a thin wrapper for repository orchestration:

- `src/nexus_adapter.py` — `NexusAdapter` class + `create_primax_agents()` factory
- `src/tui/app.py:142-147` — invokes `adapter.dispatch_task("wisdom-brain", task)` directly
- `src/nexus_cli.py` — local CLI for `nexus agents`, `nexus task`, and `nexus run <team.yaml>`
- 5 specialized agents (`dragon-coder`, `wisdom-brain`, `scout-agent`, `innovation-chaos`, `brain-spark`) live under `src/agents/`

The "Nexus CLI not yet installed" status item in older deployment notes refers to a removed external integration that was deprecated in favor of in-process orchestration. The local CLI exists to make repo workflows like `nexus run sentinel-team.yaml` executable without reintroducing that external dependency.

## OpenCode integration

`~/.config/opencode/agents/primax-ai.md` defines a `mode: primary` OpenCode agent that loads the full PRIMAX system prompt. Reference copy lives at `database/PRIMAX_SYSTEM_PROMPT.md`.

To invoke from a fresh OpenCode session: `opencode` (PRIMAX-AI loads as default primary agent), or mid-session `/agent primax-ai`.
