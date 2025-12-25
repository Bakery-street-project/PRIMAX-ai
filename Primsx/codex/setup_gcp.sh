#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - SETUP_GCP.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
gcloud config set project <YOUR_PROJECT_ID>
gcloud auth application-default login
gcloud services enable compute.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable cloudbuild.googleapis.com
