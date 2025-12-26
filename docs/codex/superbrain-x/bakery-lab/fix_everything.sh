#!/bin/bash
set -e
bash install_go_libs.sh
bash setup_gcp.sh
terraform init -reconfigure
AGENT_REPO="agentic-experiments"
sudo mkdir -p /opt/$AGENT_REPO
sudo bash install_go_libs.sh
docker build -f Dockerfile.superbrain -t superbrain:latest .
echo "All fixes done!"
