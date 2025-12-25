#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - SETUP_GCP_PERMISSIONS.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e

PROJECT_ID="mythicnode"  # Your actual project ID
SERVICE_ACCOUNT="api-707@mythicnode.iam.gserviceaccount.com"

echo "=== Setting GCP Project ==="
gcloud config set project $PROJECT_ID

echo "=== Granting Compute Admin Role ==="
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/compute.admin"

echo "=== Granting Storage Admin Role (for Terraform state) ==="
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.admin"

echo "=== Enabling Required APIs ==="
gcloud services enable compute.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

echo "=== GCP setup complete! ==="
