# Deploy PRIMAX Neuromorphic AI - Complete Guide
## Self-Hosted Intelligence Without API Limits

---

## 🎯 What You're Deploying

**PRIMAX-AI = Your Own Neuromorphic Intelligence**
- 4,736+ lines of research code
- Mathematical brain (graphs, SNN, dynamic systems)
- Continuous learning from arXiv + research feeds
- NO external API dependencies
- FREE to run (self-hosted)

**NOT using:** Groq, OpenAI, Claude APIs  
**Using:** Your own mathematical models + research database

---

## 🚀 Quick Deploy (5 Minutes)

### Option 1: Fly.io (Recommended - Always On)

```bash
# 1. Navigate to PRIMAX
cd ~/claude_enterprise/workspace/PRIMAX-ai

# 2. Install Fly CLI
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"

# 3. Login
fly auth login

# 4. Launch (creates fly.toml automatically)
fly launch --name primax-neuromorphic --region ord

# 5. Deploy
fly deploy

# 6. Get URL
fly status
# Your PRIMAX is now live at: https://primax-neuromorphic.fly.dev
```

**Test it:**
```bash
curl https://primax-neuromorphic.fly.dev/
curl https://primax-neuromorphic.fly.dev/api/v1/brain/neural-activity?size=10
```

---

### Option 2: Local (Termux) + Cloudflare Tunnel

**Run PRIMAX on your phone, expose globally:**

```bash
# 1. Start PRIMAX locally
cd ~/claude_enterprise/workspace/PRIMAX-ai
source ~/claude_enterprise/.venvs/tools_env/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# 2. Install Cloudflare tunnel
pkg install cloudflared

# 3. Create public URL (instant!)
cloudflared tunnel --url http://localhost:8000

# Output: https://random-word-1234.trycloudflare.com
# Your PRIMAX is now accessible globally!
```

**Permanent URL (free):**
```bash
cloudflared tunnel login
cloudflared tunnel create primax
cloudflared tunnel route dns primax primax.yourdomain.com
cloudflared tunnel run primax
```

---

### Option 3: Railway ($5/month credit)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize
cd ~/claude_enterprise/workspace/PRIMAX-ai
railway init

# 4. Deploy
railway up

# 5. Get URL
railway status
```

---

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-primax-url.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "watermark": "PRIMAX-AI-BSP-2025",
  "timestamp": "2025-12-26T..."
}
```

### 2. System Status
```bash
curl https://your-primax-url.com/api/v1/status
```

**Response:**
```json
{
  "primax": "operational",
  "brain_available": true,
  "brain_type": "neuromorphic_mathematical",
  "smoothoperator_integrated": false,
  "vault_available": true,
  "watermark": "PRIMAX-AI-BSP-2025"
}
```

### 3. Graph Analysis (Resilience)
```bash
curl -X POST https://your-primax-url.com/api/v1/brain/analyze-resilience \
  -H "Content-Type: application/json" \
  -d '[[0,1,1],[1,0,1],[1,1,0]]'
```

**Response:**
```json
{
  "eigenvalues": [2.0, -1.0, -1.0],
  "resilience_score": 2.0,
  "method": "graph_theory_eigenvalues",
  "watermark": "PRIMAX-AI-BSP-2025"
}
```

### 4. Neural Activity Simulation
```bash
curl https://your-primax-url.com/api/v1/brain/neural-activity?size=20&tmax=100
```

**Response:**
```json
{
  "activity_pattern": [45, 52, 48, ...],
  "network_size": 20,
  "time_steps": 100,
  "method": "spiking_neural_network",
  "watermark": "PRIMAX-AI-BSP-2025"
}
```

### 5. Scaling Prediction
```bash
curl -X POST https://your-primax-url.com/api/v1/brain/predict-scaling \
  -H "Content-Type: application/json" \
  -d '{"vm_capacity": 100}'
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
# PRIMAX Configuration
ENVIRONMENT=production
PRIMAX_VERSION=1.0.0
LOG_LEVEL=info

# Vault (for secrets storage)
VAULT_PASSWORD=$(openssl rand -base64 32)

# Optional: If you want to integrate external APIs later
# GROQ_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Performance
WORKERS=1
MAX_CONCURRENT_REQUESTS=100
ENABLE_CACHE=true
```

### Fly.io Secrets

```bash
fly secrets set VAULT_PASSWORD="$(openssl rand -base64 32)"
fly secrets set ENVIRONMENT=production
```

---

## 📊 Monitoring

### View Logs
```bash
# Fly.io
fly logs

# Railway
railway logs

# Local (Termux)
tail -f /tmp/primax.log
```

### Check Resource Usage
```bash
# Fly.io
fly status
fly vm status

# Railway
railway status
```

---

## 🔥 Running Superbrain Research Worker

The Superbrain continuously learns from latest AI research:

```bash
# 1. Activate Python environment
source ~/claude_enterprise/.venvs/tools_env/bin/activate

# 2. Run Superbrain
cd ~/claude_enterprise/workspace/PRIMAX-ai
python Primsx/codex/scripts/superbrain.py

# 3. Check research findings
cat superbrain_research.md
```

**Schedule as cron job (daily research):**
```bash
crontab -e

# Add:
0 2 * * * cd ~/claude_enterprise/workspace/PRIMAX-ai && source ~/claude_enterprise/.venvs/tools_env/bin/activate && python Primsx/codex/scripts/superbrain.py
```

---

## 🎓 Integration Examples

### JavaScript/Node.js
```javascript
const PRIMAX_URL = 'https://primax-neuromorphic.fly.dev';

// Analyze infrastructure resilience
async function checkInfrastructureHealth(adjacencyMatrix) {
  const response = await fetch(`${PRIMAX_URL}/api/v1/brain/analyze-resilience`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(adjacencyMatrix)
  });

  const { resilience_score } = await response.json();
  return resilience_score > 1.5 ? 'healthy' : 'at-risk';
}

// Predict scaling needs
async function predictScaling(currentCapacity) {
  const response = await fetch(`${PRIMAX_URL}/api/v1/brain/predict-scaling`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vm_capacity: currentCapacity })
  });

  const { scaling_solution } = await response.json();
  return scaling_solution;
}
```

### Python
```python
import requests

PRIMAX_URL = "https://primax-neuromorphic.fly.dev"

# Get neural activity pattern
def get_neural_activity(size=20, tmax=100):
    response = requests.get(
        f"{PRIMAX_URL}/api/v1/brain/neural-activity",
        params={"size": size, "tmax": tmax}
    )
    return response.json()["activity_pattern"]

# Analyze system connectivity
def analyze_connectivity(adjacency_matrix):
    response = requests.post(
        f"{PRIMAX_URL}/api/v1/brain/analyze-resilience",
        json=adjacency_matrix
    )
    return response.json()
```

### Bash/curl
```bash
#!/bin/bash
PRIMAX_URL="https://primax-neuromorphic.fly.dev"

# Check PRIMAX health
check_health() {
    curl -s "$PRIMAX_URL/health" | jq '.status'
}

# Get system status
get_status() {
    curl -s "$PRIMAX_URL/api/v1/status" | jq .
}

# Run infrastructure analysis
analyze_infra() {
    curl -X POST "$PRIMAX_URL/api/v1/brain/analyze-resilience" \
        -H "Content-Type: application/json" \
        -d "$1" | jq '.resilience_score'
}

# Usage
check_health
analyze_infra '[[0,1,1],[1,0,1],[1,1,0]]'
```

---

## 💰 Cost Comparison

### Fly.io Free Tier
```
3x VMs (256MB each)       = $0/month
3GB persistent storage    = $0/month
160GB bandwidth           = $0/month
PRIMAX requests           = ♾️ Unlimited
────────────────────────────────────
Total:                      $0/month
```

### Fly.io Production
```
3x VMs (1GB each)         = $10/month
10GB persistent storage   = $0.15/month
500GB bandwidth           = $0/month
PRIMAX requests           = ♾️ Unlimited
────────────────────────────────────
Total:                      $10.15/month
```

### vs. LLM APIs (for comparison)
```
Groq API                  = $0 (but 14,400/day limit)
Claude API                = $5 credit, then $$$
OpenAI API                = $5 credit, then $$$
At scale (100K req/mo)    = $50-200/month
────────────────────────────────────
PRIMAX is FREE unlimited
```

---

## 🔒 Security Checklist

- [ ] Set strong `VAULT_PASSWORD` (32+ characters)
- [ ] Use HTTPS (auto-configured by Fly.io/Railway)
- [ ] Enable CORS only for your domains (edit `src/main.py`)
- [ ] Add rate limiting (optional, see below)
- [ ] Keep watermark headers (prevents unauthorized use)

**Add Rate Limiting (Optional):**
```bash
pip install slowapi
```

```python
# In src/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=lambda: request.client.host)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/status")
@limiter.limit("60/minute")
async def get_status():
    ...
```

---

## 🐛 Troubleshooting

### Issue: "Brain module not available"

**Cause:** `src/brain/neuromorphic_core.py` not in path

**Fix:**
```bash
# Ensure brain module is importable
export PYTHONPATH="/data/data/com.termux/files/home/claude_enterprise/workspace/PRIMAX-ai/src:$PYTHONPATH"
```

### Issue: Deployment fails

**Check logs:**
```bash
fly logs --app primax-neuromorphic
```

**Common fixes:**
- Ensure `requirements.txt` has all dependencies
- Check Python version (3.9+ required)
- Verify Dockerfile builds locally: `docker build -t primax-test .`

### Issue: Slow responses

**Optimize:**
- Enable caching (`ENABLE_CACHE=true`)
- Scale VMs: `fly scale count 3`
- Add Redis: `fly redis create`

---

## 📈 Scaling Guide

### Stage 1: Free Tier (Now)
```
Fly.io: 3x 256MB VMs
Capacity: ~10,000 requests/month
Cost: $0/month
```

### Stage 2: Production ($10/month)
```
Fly.io: 3x 1GB VMs
PostgreSQL: Calculation cache
Redis: Real-time results
Capacity: ~100,000 requests/month
Cost: $10/month
```

### Stage 3: Enterprise
```
Kubernetes cluster
Multi-region deployment
Dedicated PostgreSQL
Capacity: Unlimited
Cost: Custom
```

---

## 🎉 You're Done!

Your PRIMAX Neuromorphic AI is now:
- ✅ Deployed and accessible
- ✅ Running mathematical intelligence (no APIs)
- ✅ Continuously learning from research
- ✅ Watermarked and protected
- ✅ Free (or $10/month for production)

**API Documentation:** https://your-primax-url.com/api/docs

**Next Steps:**
1. Integrate PRIMAX into your apps
2. Run Superbrain research worker
3. Build on top of neuromorphic intelligence

🚀 **Welcome to self-hosted AI!**
