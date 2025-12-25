#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - FIX_ALL.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================


# Detect and fix renames if not done
if [ -d "~/Desktop/superbrain-x/integrations/MYTHICNODE-Neuromorphic-Psychedelic-AI" ]; then
  mv ~/Desktop/superbrain-x/integrations/MYTHICNODE-Neuromorphic-Psychedelic-AI ~/Desktop/superbrain-x/integrations/MYTHICNODE_Neuromorphic_Psychedelic_AI
fi
if [ -d "~/Desktop/bakery-neuromorphic-lab" ]; then
  mv ~/Desktop/bakery-neuromorphic-lab ~/Desktop/bakery_neuromorphic_lab
fi

# Sed fixes for imports/syntax
sed -i 's/integrations.MYTHICNODE-Neuromorphic-Psychedelic-AI/integrations.MYTHICNODE_Neuromorphic_Psychedelic_AI/g' ~/Desktop/bakery_neuromorphic_lab/brain_perplexity_research.py
sed -i 's/bakery-neuromorphic-lab/bakery_neuromorphic_lab/g' ~/Desktop/superbrain-x/perplexity_drift.py
sed -i 's/if codex_data:/if codex_data is not None:/g' ~/Desktop/bakery_neuromorphic_lab/brain_perplexity_research.py
sed -i '1a import sys\nsys.path.append("/home/boozelee/Desktop/bakery_neuromorphic_lab")' ~/Desktop/superbrain-x/perplexity_drift.py
sed -i '/echo "New file/a \    if [[ $file == sed* ]]; then continue; fi' ~/Desktop/superbrain-x/monitor_files.sh

# Docker fixes (Ubuntu-specific)
sudo update-alternatives --set iptables /usr/sbin/iptables-legacy
sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy
sudo rm -rf /var/lib/docker
sudo mkdir /var/lib/docker
sudo systemctl daemon-reload
sudo systemctl restart docker
if ! sudo systemctl status docker | grep "active (running)"; then
  echo "Docker failed; running debug"
  sudo dockerd --debug
fi

# Rebuild and run Docker
cd ~/Desktop/superbrain-x
go mod tidy
go build -o server cmd/server/main.go
docker build -t superbrain-x:latest .
docker rm -f superbrain-secure
docker run --network none --name superbrain-secure -v ~/wheels:/wheels superbrain-x:latest

# Run Python scripts
python3 ~/Desktop/bakery_neuromorphic_lab/brain_perplexity_research.py
python3 ~/Desktop/superbrain-x/perplexity_drift.py

# Test endpoints
docker exec superbrain-secure curl localhost:8080/wheel/center
