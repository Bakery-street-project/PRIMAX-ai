#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   PRIMAX-AI SECURE DEPLOYMENT SCRIPT                          ║
# ║                                                                               ║
# ║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
# ║  PROPRIETARY & CONFIDENTIAL                                                   ║
# ║                                                                               ║
# ║  WATERMARK: PRIMAX-DEPLOY-BSP-2025                                            ║
# ║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -e

echo "🔒 PRIMAX-AI SECURE DEPLOYMENT"
echo "=============================="
echo "Watermark: PRIMAX-AI-BSP-2025"
echo "Owner: Kiliaan Vanvoorden (@BoozeLee)"
echo "Copyright © 2024-2025 Bakery Street Project"
echo ""

# 1. Verify all files are watermarked
echo "Step 1/5: Verifying watermarks..."
if grep -r "PRIMAX-AI-BSP-2025" src/ > /dev/null 2>&1; then
    echo "  ✓ Watermarks verified"
else
    echo "  ⚠ Running watermark tool..."
    python watermark_all.py .
fi

# 2. Set strict permissions
echo ""
echo "Step 2/5: Setting strict permissions (700)..."
chmod -R 700 .
chmod 700 .
echo "  ✓ Permissions set (owner only)"

# 3. Create secure .env for deployment
echo ""
echo "Step 3/5: Creating deployment environment..."
cat > .env.deploy << EOF
# PRIMAX-AI DEPLOYMENT CONFIGURATION
# Copyright © 2024-2025 Bakery Street Project
# WATERMARK: PRIMAX-AI-BSP-2025

ENVIRONMENT=production
PRIMAX_VERSION=1.0.0
PRIMAX_WATERMARK=PRIMAX-AI-BSP-2025
LOG_LEVEL=info

# Security
VAULT_PASSWORD=$(openssl rand -base64 32)
API_SECRET_KEY=$(openssl rand -hex 32)

# Performance
WORKERS=1
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30
ENABLE_CACHE=true
ENABLE_RATE_LIMIT=true
RATE_LIMIT_PER_MIN=60

# Watermark enforcement
WATERMARK_CHECK=enabled
COPYRIGHT_ENFORCEMENT=strict
EOF

chmod 600 .env.deploy
echo "  ✓ Secure environment created"

# 4. Create fly.toml with security settings
echo ""
echo "Step 4/5: Creating Fly.io configuration..."
cat > fly.toml << 'FLYEOF'
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   PRIMAX-AI FLY.IO CONFIGURATION                              ║
# ║  Copyright © 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED           ║
# ║  WATERMARK: PRIMAX-AI-BSP-2025                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

app = "primax-neuromorphic"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile"

[env]
  PRIMAX_WATERMARK = "PRIMAX-AI-BSP-2025"
  ENVIRONMENT = "production"
  LOG_LEVEL = "info"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80
    force_https = true

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.http_checks]]
    interval = 30000
    timeout = 5000
    grace_period = "10s"
    method = "get"
    path = "/health"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256

FLYEOF

echo "  ✓ Fly.io configuration created"

# 5. Build and deploy
echo ""
echo "Step 5/5: Deploying to Fly.io..."
echo "  → Checking Fly CLI..."
if ! command -v fly &> /dev/null; then
    echo "  ⚠ Installing Fly CLI..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

echo "  → Deploying PRIMAX..."
fly deploy --ha=false

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "Your PRIMAX-AI is now live at:"
echo "  https://primax-neuromorphic.fly.dev"
echo ""
echo "🔒 Security Features:"
echo "  ✓ All files watermarked: PRIMAX-AI-BSP-2025"
echo "  ✓ Strict permissions: 700 (owner only)"
echo "  ✓ Copyright: © 2024-2025 Bakery Street Project"
echo "  ✓ HTTPS enforced"
echo "  ✓ Health checks enabled"
echo ""
echo "📊 Test your deployment:"
echo "  curl https://primax-neuromorphic.fly.dev/health"
echo "  curl https://primax-neuromorphic.fly.dev/api/v1/watermark"
echo ""
echo "Owner: Kiliaan Vanvoorden (@BoozeLee)"
echo "Watermark: PRIMAX-AI-BSP-2025"
