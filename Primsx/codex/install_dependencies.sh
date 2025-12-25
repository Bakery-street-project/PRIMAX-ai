#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - INSTALL_DEPENDENCIES.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e

echo "=== Installing System Dependencies ==="
sudo apt update
sudo apt install -y python3-pip python3-venv git jq curl wget

echo "=== Installing Python Packages ==="
pip3 install --user numpy sympy requests matplotlib

echo "=== Installing Google Cloud SDK ==="
if ! command -v gcloud &> /dev/null; then
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL
fi

echo "=== Installing Terraform ==="
if ! command -v terraform &> /dev/null; then
    wget https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_linux_amd64.zip
    unzip terraform_1.6.6_linux_amd64.zip
    sudo mv terraform /usr/local/bin/
    rm terraform_1.6.6_linux_amd64.zip
fi

echo "=== Installing Go (if needed) ==="
if ! command -v go &> /dev/null; then
    wget https://go.dev/dl/go1.23.0.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.23.0.linux-amd64.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    export PATH=$PATH:/usr/local/go/bin
fi

echo "=== All dependencies installed! ==="
