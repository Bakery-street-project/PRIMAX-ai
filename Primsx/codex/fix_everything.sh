#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - FIX_EVERYTHING.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e
bash install_go_libs.sh
bash setup_gcp.sh
terraform init -reconfigure
AGENT_REPO="agentic-experiments"
sudo mkdir -p /opt/$AGENT_REPO
sudo bash install_go_libs.sh
docker build -f Dockerfile.superbrain -t superbrain:latest .
echo "All fixes done!"
