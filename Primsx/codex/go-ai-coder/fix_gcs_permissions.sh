#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - FIX_GCS_PERMISSIONS.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

# Grant storage.objects.* permissions to your service account
gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="serviceAccount:api-707@mythicnode.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Re-initialize Terraform
terraform init -reconfigure
