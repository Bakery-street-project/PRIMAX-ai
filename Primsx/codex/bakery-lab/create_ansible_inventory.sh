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

IPS=$(terraform output -json | jq -r '.instance_ips.value[]')
cat > ansible/hosts.yml <<HOSTS
all:
  hosts:
HOSTS
i=1
for ip in $IPS; do
  echo "    vm-$i: { ansible_host: $ip }" >> ansible/hosts.yml
  ((i++))
done
