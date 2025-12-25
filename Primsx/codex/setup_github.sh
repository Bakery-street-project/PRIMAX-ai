#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - SETUP_GITHUB.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================


echo "🚀 GitHub Enterprise AI Agent Setup"
echo "==================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🔑 GitHub Enterprise Configuration"
echo "================================="
echo ""
echo "To enable GitHub Enterprise integration, you need to:"
echo ""
echo "1. Create a GitHub Personal Access Token (PAT):"
echo "   - Go to: https://github.com/settings/tokens"
echo "   - Click 'Generate new token (classic)'"
echo "   - Select scopes: repo, read:org, read:user"
echo "   - Copy the token"
echo ""
echo "2. Add the token to your .env file:"
echo "   GITHUB_TOKEN=your_token_here"
echo ""
echo "3. For GitHub Enterprise Server:"
echo "   - Use your enterprise server URL instead of github.com"
echo "   - Update the API endpoints in the code"
echo ""

# Check if GITHUB_TOKEN is set
if grep -q "GITHUB_TOKEN=" .env && ! grep -q "GITHUB_TOKEN=your-api-key-here" .env; then
    echo "✅ GITHUB_TOKEN is configured"
else
    echo "⚠️  GITHUB_TOKEN not configured yet"
    echo "   Please add your GitHub token to .env file"
fi

echo ""
echo "🔧 Additional GitHub Enterprise Features"
echo "======================================="
echo ""
echo "For advanced GitHub Enterprise features, consider:"
echo ""
echo "1. GitHub App Integration:"
echo "   - Create a GitHub App for fine-grained permissions"
echo "   - Enable webhook integration for real-time updates"
echo "   - Access to private repositories and organizations"
echo ""
echo "2. Enterprise Server Integration:"
echo "   - Update API endpoints to use your enterprise server"
echo "   - Configure authentication for enterprise SSO"
echo "   - Enable enterprise-specific features"
echo ""
echo "3. Advanced AI Capabilities:"
echo "   - Code analysis across multiple repositories"
echo "   - Automated issue and PR management"
echo "   - Code quality and security scanning"
echo "   - Automated documentation generation"
echo ""

echo "🎯 Next Steps"
echo "============="
echo ""
echo "1. Set up your GitHub token in .env"
echo "2. Run: go run github_ai_agent.go"
echo "3. Try commands like:"
echo "   - github repos"
echo "   - github search golang ai"
echo "   - github issues microsoft/vscode"
echo ""
echo "4. For enterprise features, modify the API endpoints in github_ai_agent.go"
echo ""

echo "✅ Setup complete! Your AI agent is ready to become a coding god! 🚀"
