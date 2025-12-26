# 🚀 PRIMAX DEPLOYMENT STATUS & GUIDE

**Date:** December 26, 2025  
**Status:** ✅ READY FOR CLOUD DEPLOYMENT  
**Watermark:** PRIMAX-AI-BSP-2025  
**Owner:** Kiliaan Vanvoorden (@BoozeLee)  
**Copyright:** © 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED

---

## 📍 QUICK NAVIGATION

**To resume this project, read this file first!**

**Location:**
- **Local:** `~/claude_enterprise/workspace/PRIMAX-ai/DEPLOYMENT_GUIDE/`
- **GitHub:** https://github.com/Bakery-street-project/PRIMAX-ai/tree/master/DEPLOYMENT_GUIDE

---

## ✅ WHAT'S COMPLETED

### 1. **Local PRIMAX Server** ✅
- **Status:** Running on localhost:8000
- **PID:** 17815 (may change after restart)
- **Mode:** Lite (scipy not available locally)
- **Auth:** Blackout Vault integration working
- **Security:** API key rotation complete

**To restart local server:**
```bash
cd ~/claude_enterprise/workspace/PRIMAX-ai
nohup python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000 > primax.log 2>&1 &
tail -f primax.log  # Check if running
```

**To check if running:**
```bash
curl http://localhost:8000/health
```

---

### 2. **Natural Language Interface (NLP)** ✅
- **File:** `primax_nlp_interface.py`
- **CLI:** `~/bin/primax` (wrapper script)
- **Tested:** AI art generator example

**Usage:**
```bash
cd ~/claude_enterprise/workspace/PRIMAX-ai
python3 primax_nlp_interface.py automate <your task description>

# Examples:
python3 primax_nlp_interface.py automate create AI art generator platform
python3 primax_nlp_interface.py automate build REST API with authentication
```

**How it works:**
1. Parses natural language → Task graph
2. Selects agents using graph theory (from AutomationCodex)
3. Generates execution steps
4. Routes to Dream Script Engine (when available)

---

### 3. **Security Implementation** ✅

#### Blackout Vault (API Key Storage)
- **Location:** `~/my-app-vault/secrets/.env`
- **Permissions:** 600 (owner-read only)
- **Contains:** Rotated PRIMAX_API_KEY

**To view (DON'T share this!):**
```bash
cat ~/my-app-vault/secrets/.env
```

**Security Protocol V2:**
- Old API key (5c8f...) → BURNED (compromised)
- New API key → Rotated, vault-stored
- Code loads dynamically from vault (no hardcoding)

#### File Security
- **Watermarked:** 200+ files with PRIMAX-AI-BSP-2025
- **Permissions:** 700 on all directories
- **Copyright:** Every file has header

---

### 4. **GitHub Repository** ✅
- **Repo:** https://github.com/Bakery-street-project/PRIMAX-ai
- **Branch:** master (not main!)
- **Commits:** 
  - `3f20b64` - Main deployment commit (209 files)
  - `9af9983` - Render.yaml branch fix

**Last push:** December 26, 2025

**To pull latest:**
```bash
cd ~/claude_enterprise/workspace/PRIMAX-ai
git pull origin master
```

---

### 5. **System Architecture** ✅
- **Document:** `FULL_SYSTEM_ARCHITECTURE.md`
- **Components integrated:**
  - PRIMAX-AI (Neuromorphic core)
  - Smoothoperator (Dream Script Engine)
  - Terminal221b (PAO + Solana)
  - Baker-Street-Laboratory (Investigation tools)

**Read full architecture:**
```bash
cat ~/claude_enterprise/workspace/PRIMAX-ai/FULL_SYSTEM_ARCHITECTURE.md
```

---

### 6. **Key Files Created**

| File | Purpose |
|------|---------|
| `primax_nlp_interface.py` | Natural language task parser |
| `FULL_SYSTEM_ARCHITECTURE.md` | Complete system documentation |
| `secure_vault.py` | PBKDF2 + AES-256 encryption vault |
| `watermark_all.py` | Copyright enforcement tool |
| `render.yaml` | Render.com deployment config |
| `DEPLOYMENT_GUIDE/` | **THIS FOLDER** - How to resume |

---

## 🚀 NEXT STEP: DEPLOY TO RENDER (FREE CLOUD)

### Why Render?
- ✅ Free tier (750 hours/month)
- ✅ scipy/numpy install properly (unlike Termux)
- ✅ Never sleeps (for web services)
- ✅ Auto-SSL (HTTPS)
- ✅ Auto-deploy on git push

### Deployment Steps:

#### 1. Go to Render Dashboard
**URL:** https://dashboard.render.com/

#### 2. Create New Web Service
- Click: "New +" → "Web Service"
- Connect: GitHub account
- Select: `Bakery-street-project/PRIMAX-ai`

#### 3. Configure Service
```
Name:           primax-neuromorphic
Branch:         master
Runtime:        Docker
Region:         Oregon (or closest to you)
Plan:           Free
```

#### 4. Set Environment Variable (CRITICAL!)
**Get your API key:**
```bash
cat ~/my-app-vault/secrets/.env
```

**In Render dashboard:**
- Go to: Environment → Add Environment Variable
- Key: `PRIMAX_API_KEY`
- Value: `<paste the key from vault>`
- Click: Save

#### 5. Deploy
- Click: "Create Web Service"
- Wait: ~10 minutes (Docker build + scipy installation)

#### 6. Get Your URL
After deployment:
```
https://primax-neuromorphic.onrender.com
```

---

## 🧪 TESTING AFTER DEPLOYMENT

### 1. Health Check
```bash
curl https://primax-neuromorphic.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "watermark": "PRIMAX-AI-BSP-2025",
  "timestamp": "2025-12-26T..."
}
```

### 2. Watermark Verification
```bash
curl https://primax-neuromorphic.onrender.com/api/v1/watermark
```

### 3. Test Brain Functions (NOW WORKING - scipy available!)
```bash
curl -X POST https://primax-neuromorphic.onrender.com/api/v1/brain/analyze-resilience \
  -H "X-API-Key: YOUR_VAULT_KEY" \
  -H "Content-Type: application/json" \
  -d '{"adjacency_matrix": [[0,1,1],[1,0,1],[1,1,0]]}'
```

### 4. Test NLP Automation
```bash
curl -X POST https://primax-neuromorphic.onrender.com/api/v1/automate \
  -H "X-API-Key: YOUR_VAULT_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task": "create an AI art generator with website and prompt injection", "mode": "safe"}'
```

---

## 📂 PROJECT STRUCTURE

```
~/claude_enterprise/workspace/PRIMAX-ai/
├── DEPLOYMENT_GUIDE/          ← YOU ARE HERE!
│   └── README.md              ← This file
├── FULL_SYSTEM_ARCHITECTURE.md
├── primax_nlp_interface.py    ← NLP interface
├── src/
│   ├── main.py                ← FastAPI server (vault-integrated)
│   └── brain/                 ← AutomationCodex mathematical brain
│       ├── graph_theory.py    ← Eigenvalue analysis
│       ├── snn.py             ← Spiking neural networks
│       └── dynamic_systems.py ← Differential equations
├── render.yaml                ← Render deployment config
├── Dockerfile                 ← Docker build
└── requirements.txt           ← Python dependencies (includes scipy)

~/my-app-vault/secrets/
└── .env                       ← PRIMAX_API_KEY (rotated, 600 perms)

~/bin/
└── primax                     ← CLI wrapper (optional)
```

---

## 🔐 SECURITY CHECKLIST

- ✅ API key rotated (old key burned)
- ✅ Vault integration complete (Security Protocol V2)
- ✅ All files watermarked (PRIMAX-AI-BSP-2025)
- ✅ Permissions: 700 directories, 600 secrets
- ✅ CORS restricted (not wide open)
- ✅ Rate limiting (60 req/min)
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ No hardcoded secrets in code

---

## 🧩 INTEGRATED COMPONENTS

### 1. PRIMAX-AI (This repo)
- Neuromorphic intelligence core
- Mathematical brain (not LLM)
- REST API server

### 2. Smoothoperator
- **Location:** `~/claude_enterprise/workspace/Smoothoperator/`
- **GitHub:** https://github.com/Bakery-street-project/Smoothoperator
- **Contains:** Dream Script Engine (neuromorphic code generation)

### 3. Terminal221b
- **Location:** `~/claude_enterprise/workspace/Terminal221b/`
- **GitHub:** https://github.com/Bakery-street-project/Terminal221b
- **Contains:** PAO (Polymathic Autonomous Organization) + Solana integration

### 4. Baker-Street-Laboratory
- **Location:** `~/claude_enterprise/workspace/Baker-Street-Laboratory-1/`
- **Contains:** Investigation and forensics tools

**All components work together as shown in FULL_SYSTEM_ARCHITECTURE.md**

---

## 🎯 RESUMING THIS PROJECT LATER

### Quick Start Commands:

```bash
# 1. Navigate to project
cd ~/claude_enterprise/workspace/PRIMAX-ai

# 2. Pull latest from GitHub
git pull origin master

# 3. Check vault key is still there
cat ~/my-app-vault/secrets/.env

# 4. Start local server
python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000

# 5. Test it works
curl http://localhost:8000/health

# 6. Test NLP interface
python3 primax_nlp_interface.py automate <your task>
```

### If Cloud Deployed:
```bash
# Test cloud instance
curl https://primax-neuromorphic.onrender.com/health
```

---

## 📊 CURRENT STATUS SUMMARY

| Component | Status | Location |
|-----------|--------|----------|
| **Local Server** | ✅ Running (lite mode) | localhost:8000 |
| **GitHub Repo** | ✅ Pushed (209 files) | github.com/Bakery-street-project/PRIMAX-ai |
| **Vault Integration** | ✅ Working | ~/my-app-vault/secrets/.env |
| **NLP Interface** | ✅ Tested | primax_nlp_interface.py |
| **Watermarking** | ✅ Complete (200+ files) | All source files |
| **Documentation** | ✅ Complete | FULL_SYSTEM_ARCHITECTURE.md |
| **Cloud Deployment** | ⏳ Pending | Render.com (ready to deploy) |

---

## 🌐 IMPORTANT URLS

- **GitHub Repo:** https://github.com/Bakery-street-project/PRIMAX-ai
- **Render Dashboard:** https://dashboard.render.com/
- **Future Cloud URL:** https://primax-neuromorphic.onrender.com (after deployment)

---

## 💡 KEY CONCEPTS

### What is PRIMAX?
**NOT an LLM wrapper!**

It's a **neuromorphic intelligence system** using:
- **Graph theory** (eigenvalue analysis for resilience)
- **Spiking neural networks** (biological neuron models)
- **Dynamic systems** (differential equations)
- **MDPs** (Markov Decision Processes for agent routing)

### How does NLP work?
```
User: "primax automate create AI art generator"
  ↓
NLP Parser: Extracts intent + components
  ↓
AutomationCodex Brain: Routes using graph theory
  ↓
Agents Selected: [designer, coder, deployer]
  ↓
Dream Script Engine: Generates code
  ↓
Result: Deployed AI art generator platform
```

---

## 🆘 TROUBLESHOOTING

### Local server won't start:
```bash
# Check if already running
ps aux | grep uvicorn

# Kill old instance
pkill -f uvicorn

# Restart
cd ~/claude_enterprise/workspace/PRIMAX-ai
python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

### Vault key not loading:
```bash
# Verify vault exists
ls -la ~/my-app-vault/secrets/.env

# Should show: -rw------- (600 permissions)

# Check contents (careful - sensitive!)
cat ~/my-app-vault/secrets/.env
```

### Brain functions not working locally:
**This is EXPECTED!** scipy doesn't install on Termux/Android.
→ Deploy to Render cloud to enable full brain functions.

---

## 📞 CONTACTS & OWNERSHIP

**Owner:** Kiliaan Vanvoorden (@BoozeLee)  
**Organization:** Bakery Street Project  
**GitHub:** https://github.com/BoozeLee  
**Organization GitHub:** https://github.com/Bakery-street-project  

**Copyright:** © 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED  
**License:** Proprietary (see LICENSE_PROPRIETARY.md)  
**Watermark:** PRIMAX-AI-BSP-2025

---

## 🔮 FUTURE PHASES

### Phase 1: Current ✅
- NLP interface working
- Local server operational
- GitHub repository ready
- Security hardened

### Phase 2: Next (Deploy to Render)
- Cloud deployment
- Full brain functions enabled (scipy working)
- Public API accessible
- Auto-deploy on git push

### Phase 3: Terminal221b Integration
- Solana blockchain connection
- DAO governance
- Economic generative loop
- Self-funding operations

### Phase 4: Superbrain Activation
- Continuous arXiv scraping
- Automated research synthesis
- Knowledge graph updates
- Hypothesis generation

### Phase 5: Migration to Akashi
- When crypto funding available
- Premium hosting
- Scaled compute resources
- Full production mode

---

## 📝 NOTES FOR FUTURE YOU

1. **Don't lose the vault key!** It's in `~/my-app-vault/secrets/.env`
2. **Branch is "master" not "main"** - important for git operations
3. **Render needs PRIMAX_API_KEY env var** - copy from vault
4. **Local server is lite mode** - brain functions only work on cloud
5. **All commits should preserve watermark** - PRIMAX-AI-BSP-2025
6. **This guide is also on GitHub** - safe even if local copy lost

---

**Last Updated:** December 26, 2025  
**Status:** ✅ READY FOR CLOUD DEPLOYMENT  
**Next Action:** Deploy to Render.com

---

🔒 **Secured. Watermarked. Self-Evolving.**
