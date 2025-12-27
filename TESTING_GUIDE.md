# PRIMAX AI - Testing Guide

## 🧪 Test All Features

### 1. Health Check (No Auth)
```bash
curl https://primax-ai.onrender.com/health
```

**Expected:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "watermark": "PRIMAX-AI-BSP-2025"
}
```

### 2. Chat Interface (No Auth)
```bash
curl -X POST https://primax-ai.onrender.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello PRIMAX!"}'
```

**Expected:**
```json
{
  "session_id": "...",
  "response": "I'm PRIMAX AI...",
  "context": {},
  "message_count": 2,
  "watermark": "PRIMAX-AI-BSP-2025"
}
```

### 3. Generate Code with AI (Requires API Key)
```bash
curl -X POST https://primax-ai.onrender.com/api/v1/ai/generate-code \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_PRIMAX_API_KEY" \
  -d '{
    "prompt": "Create a Python function to calculate fibonacci",
    "language": "python"
  }'
```

### 4. Analyze GitHub Repo (Requires API Key)
```bash
curl -X POST https://primax-ai.onrender.com/api/v1/analyze-repo \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_PRIMAX_API_KEY" \
  -d '{"repo_full_name": "Bakery-street-project/PRIMAX-ai"}'
```

### 5. Scan Baker Street Organization (Requires API Key)
```bash
curl -X POST https://primax-ai.onrender.com/api/v1/scan-organization \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_PRIMAX_API_KEY" \
  -d '{
    "org_name": "Bakery-street-project",
    "limit": 10
  }'
```

## 📊 Interactive API Docs

Visit: https://primax-ai.onrender.com/api/docs

- Try all 17 endpoints
- See request/response schemas
- No code needed!

## 🔑 Your API Keys

### PRIMAX_API_KEY (Generated)
```
rD6HdwqD6vKci4KV-k7CMw3j6GySGE6ky9mtFQW3f08
```

Set in Render: https://dashboard.render.com/web/srv-d57qsi3e5dus73dhbj1g

### GROQ_API_KEY (You Added)
Check your vault or Render environment variables.

## ✅ Feature Checklist

- [ ] Chat works without API key
- [ ] AI code generation works (needs GROQ_API_KEY)
- [ ] GitHub scanner works (needs gh CLI auth in production)
- [ ] Health check responds
- [ ] API docs accessible

## 🐛 Troubleshooting

**"Chat module not available"**
- Modules still deploying (wait 3-4 minutes)
- Check deployment logs in Render

**"LLM not available"**
- Set GROQ_API_KEY in Render environment

**"GitHub Scanner not available"**
- gh CLI needs auth token in production
- Or modules still loading

**503 errors**
- Service just woke up (cold start)
- Try again in 30 seconds

---

**Watermark:** PRIMAX-AI-BSP-2025
