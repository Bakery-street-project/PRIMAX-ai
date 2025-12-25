#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - INTEGRATE_CODEX.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e
echo "🧠 Integrating Codex SuperLab + Repos into superbrain-x"
cp ~/Desktop/bakery-neuromorphic-lab/brain_perplexity_research.py .
# Integrate MYTHICNODE (neuromorphic)
cp integrations/MYTHICNODE-Neuromorphic-Psychedelic-AI/*.py .  # Selective
# Baker-Street orchestration
cp integrations/Baker-Street-Laboratory/research_launcher.py .
# ai-dev envs
cp integrations/ai-development-framework/activate-*.sh .
# Polymorphic agents
cp integrations/Polymorphic-Research-Framework/*.py .  # Agents
cat > codex_boost.sh <<'BOOST'
#!/bin/bash
set -e
echo "🧠 Running Codex SuperLab Analysis..."
python3 brain_perplexity_research.py
python3 research_launcher.py "Chaos in neuromorphic wheel" neuroscience  # Baker-Street
go run cmd/server/main.go & 
curl http://localhost:8080/wheel/chaotic_neuro?nums=6,9,42
kill %1
echo "✅ Analysis complete!"
BOOST
chmod +x codex_boost.sh
echo "✅ Integrated! Run ./codex_boost.sh"
