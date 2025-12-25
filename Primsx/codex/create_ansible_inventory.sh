#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - CREATE_ANSIBLE_INVENTORY.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e

if [ ! -f outputs.json ]; then
    echo "Error: outputs.json not found. Run terraform first."
    exit 1
fi

IPS=$(jq -r '.instance_ips.value[]' outputs.json)

mkdir -p ansible

cat > ansible/hosts.yml <<HOSTS
all:
  hosts:
HOSTS

i=1
for ip in $IPS; do
  echo "    vm-$i: { ansible_host: $ip }" >> ansible/hosts.yml
  ((i++))
done

echo "✓ Ansible inventory created at ansible/hosts.yml"
cat ansible/hosts.yml
