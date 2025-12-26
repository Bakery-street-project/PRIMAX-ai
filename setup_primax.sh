#!/bin/bash
# PRIMAX AI Setup Script
# Configures PRIMAX with your API keys and prepares for deployment

set -e

echo "🚀 PRIMAX AI Setup"
echo "=================="

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env already exists. Backing up to .env.backup..."
    cp .env .env.backup
fi

# Copy API keys from enterprise .env
if [ -f ~/claude_enterprise/.env ]; then
    echo "✓ Found enterprise .env, copying API keys..."

    # Load keys
    source ~/claude_enterprise/.env

    # Create PRIMAX .env
    cat > .env << ENVFILE
# PRIMAX AI - Auto-generated from enterprise setup
# $(date)

# AI APIs
GROQ_API_KEY=$GROQ_API_KEY
HUGGINGFACE_API_KEY=$HUGGINGFACE_API_KEY
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
OPENAI_API_KEY=$OPENAI_API_KEY
GITHUB_TOKEN=$GITHUB_TOKEN

# Security
VAULT_PASSWORD=$(openssl rand -base64 32)
API_SECRET_KEY=$(openssl rand -hex 32)

# Config
ENVIRONMENT=production
PRIMAX_VERSION=1.0.0
PRIMAX_WATERMARK=PRIMAX-AI-BSP-2025
LOG_LEVEL=info

# Performance
WORKERS=1
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30
ENABLE_CACHE=true
ENABLE_RATE_LIMIT=true
RATE_LIMIT_PER_MIN=60
ENVFILE

    chmod 600 .env
    echo "✓ Created .env with secure permissions (600)"
else
    echo "❌ Enterprise .env not found at ~/claude_enterprise/.env"
    echo "   Please run the API setup first"
    exit 1
fi

# Initialize vault
echo ""
echo "📦 Initializing encrypted vault..."
if [ -f src/vault_manager.py ]; then
    source ~/claude_enterprise/.venvs/tools_env/bin/activate
    python src/vault_manager.py init
    echo "✓ Vault initialized"
else
    echo "⚠️  vault_manager.py not found, skipping..."
fi

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✓ Python dependencies installed"
fi

if [ -f package.json ]; then
    npm install > /dev/null 2>&1
    echo "✓ Node.js dependencies installed"
fi

echo ""
echo "✅ PRIMAX AI Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Test locally:  uvicorn src.main:app --reload"
echo "2. Deploy:"
echo "   - Fly.io:   fly launch && fly deploy"
echo "   - Railway:  railway up"
echo "   - Render:   git push origin main"
echo ""
echo "📖 See FREE_CLOUD_COMPARISON.md for deployment guides"
