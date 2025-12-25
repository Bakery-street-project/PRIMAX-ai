#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - RUN_ALL.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -euo pipefail

bash scripts/setup_go_ai_coder.sh

cd ~/Desktop/go-ai-coder
make all

python3 scripts/scout_agent.py

if command -v godot &>/dev/null; then cd ~/my-godot-project && godot --path . & fi
if command -v flutter &>/dev/null; then cd ~/my-flutter-app && flutter run & fi
if command -v gnome-builder &>/dev/null; then gnome-builder ~/Desktop/go-ai-coder & fi
