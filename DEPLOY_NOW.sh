#!/bin/bash
cd ~/claude_enterprise/workspace/PRIMAX-ai
echo "🚀 Deploying PRIMAX-AI..."
echo "Watermark: PRIMAX-AI-BSP-2025"
echo "Owner: Kiliaan Vanvoorden (@BoozeLee)"
fly launch --name primax-neuromorphic --region ord --no-deploy
fly deploy --ha=false
echo "✅ DEPLOYED! https://primax-neuromorphic.fly.dev"
