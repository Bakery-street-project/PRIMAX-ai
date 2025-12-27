#!/bin/zsh
# Deploy PRIMAX with Supabase pgvector backend
#
# © 2025 Bakery Street Project
# WATERMARK: PRIMAX-AI-BSP-2025

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "${GREEN}========================================${NC}"
echo "${GREEN}PRIMAX + Supabase Deployment${NC}"
echo "${GREEN}========================================${NC}"
echo ""

cd ~/claude_enterprise/workspace/PRIMAX-ai

# 1. Activate venv
echo "${YELLOW}1. Activating Python environment...${NC}"
source ~/claude_enterprise/.venvs/tools_env/bin/activate

# 2. Install dependencies
echo "${YELLOW}2. Installing dependencies...${NC}"
# Install core dependencies first
pip install -q fastapi uvicorn asyncpg numpy python-dotenv

# Try to install sentence-transformers (may fail on Termux)
echo "${YELLOW}   Installing sentence-transformers (optional)...${NC}"
if pip install -q sentence-transformers 2>/dev/null; then
    echo "${GREEN}   ✅ sentence-transformers installed${NC}"
else
    echo "${YELLOW}   ⚠️  sentence-transformers skipped (will use mock embeddings)${NC}"
    echo "${YELLOW}   This is OK for testing - production should use cloud deployment${NC}"
fi

# 3. Check for environment variables
echo "${YELLOW}3. Checking environment variables...${NC}"

if [ -z "$SUPABASE_URL" ]; then
    echo "${YELLOW}⚠️  SUPABASE_URL not set${NC}"
    echo "   Get it from: https://supabase.com/dashboard → Settings → API"
    echo "   Set with: export SUPABASE_URL=https://your-project.supabase.co"
    echo ""
fi

if [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "${YELLOW}⚠️  SUPABASE_SERVICE_KEY not set${NC}"
    echo "   Get it from: https://supabase.com/dashboard → Settings → API"
    echo "   Set with: export SUPABASE_SERVICE_KEY=eyJhbG..."
    echo ""
fi

# 4. Test Supabase connection (if keys set)
if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_SERVICE_KEY" ]; then
    echo "${YELLOW}4. Testing Supabase connection...${NC}"
    python -c "
import asyncio
import os
os.environ['SUPABASE_URL'] = '$SUPABASE_URL'
os.environ['SUPABASE_SERVICE_KEY'] = '$SUPABASE_SERVICE_KEY'

from src.db.supabase_client import get_client

async def test():
    try:
        client = get_client()
        await client.connect()
        print('${GREEN}✅ Supabase connected${NC}')
        await client.close()
    except Exception as e:
        print(f'${RED}❌ Connection failed: {e}${NC}')
        raise

asyncio.run(test())
" || echo "${RED}❌ Supabase connection failed - check credentials${NC}"
else
    echo "${YELLOW}⚠️  Skipping connection test (keys not set)${NC}"
fi

# 5. Create requirements.txt
echo "${YELLOW}5. Creating requirements.txt...${NC}"
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
asyncpg==0.29.0
sentence-transformers==2.2.2
numpy==1.24.3
pydantic==2.5.0
python-dotenv==1.0.0
EOF
echo "${GREEN}✅ requirements.txt created${NC}"

# 6. Create/update render.yaml
echo "${YELLOW}6. Creating Render deployment config...${NC}"
cat > render.yaml << 'EOF'
services:
  - type: web
    name: primax-ai-supabase
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
    autoDeploy: true
    healthCheckPath: /health
EOF
echo "${GREEN}✅ render.yaml created${NC}"

# 7. Test locally (if keys set)
if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_SERVICE_KEY" ]; then
    echo "${YELLOW}7. Testing PRIMAX locally...${NC}"
    uvicorn src.main:app --host 0.0.0.0 --port 8000 &
    UVICORN_PID=$!
    sleep 5

    if curl -s http://localhost:8000/health | grep -q "supabase"; then
        echo "${GREEN}✅ Health check passed${NC}"
    else
        echo "${RED}❌ Health check failed${NC}"
    fi

    kill $UVICORN_PID 2>/dev/null || true
else
    echo "${YELLOW}⚠️  Skipping local test (keys not set)${NC}"
fi

# 8. Git status
echo "${YELLOW}8. Git status...${NC}"
git status --short

# 9. Ready to commit
echo ""
echo "${GREEN}========================================${NC}"
echo "${GREEN}✅ PRIMAX ready for deployment!${NC}"
echo "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. ${YELLOW}Configure Supabase:${NC}"
echo "   • Go to: https://supabase.com/dashboard"
echo "   • Run SQL schema from: DEPLOYMENT_SUPABASE.md"
echo "   • Get credentials from: Settings → API"
echo ""
echo "2. ${YELLOW}Set environment variables:${NC}"
echo "   export SUPABASE_URL=https://your-project.supabase.co"
echo "   export SUPABASE_SERVICE_KEY=eyJhbG..."
echo ""
echo "3. ${YELLOW}Commit and push:${NC}"
echo "   git add -A"
echo '   git commit -m "Add Supabase backend"'
echo "   git push origin main"
echo ""
echo "4. ${YELLOW}Deploy to Render:${NC}"
echo "   • Go to: https://dashboard.render.com"
echo "   • Connect GitHub repo"
echo "   • Add environment variables"
echo "   • Deploy!"
echo ""
echo "${GREEN}Documentation:${NC} ~/claude_enterprise/workspace/PRIMAX-ai/DEPLOYMENT_SUPABASE.md"
echo ""
