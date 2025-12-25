#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - RUN_TERRAFORM.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e

echo "=== Terraform Init ==="
terraform init

echo "=== Terraform Format ==="
terraform fmt

echo "=== Terraform Validate ==="
terraform validate

echo "=== Terraform Plan ==="
terraform plan

echo "=== Terraform Apply ==="
terraform apply -auto-approve

echo "=== Extracting Outputs ==="
terraform output -json > outputs.json
terraform output

echo "=== Terraform deployment complete! ==="
