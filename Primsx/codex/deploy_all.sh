#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - DEPLOY_ALL.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e

echo "=== Running Neuromorphic Brain Analysis ==="
python3 brain_perplexity_research.py

echo -e "\n=== Deploying Terraform Infrastructure ==="
./run_terraform.sh

echo -e "\n=== Creating Ansible Inventory ==="
./create_ansible_inventory.sh

echo -e "\n=== All systems deployed! ==="
echo "Next steps:"
echo "  - Check brain_research_results.txt for analysis"
echo "  - Review ansible/hosts.yml for VM IPs"
echo "  - Run 'ansible-playbook -i ansible/hosts.yml ansible/site.yml' to configure VMs"
