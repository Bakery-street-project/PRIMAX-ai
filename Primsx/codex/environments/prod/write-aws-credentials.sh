#!/usr/bin/env bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - WRITE-AWS-CREDENTIALS.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

cat <<CRED > ~/.aws/credentials
[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY
CRED

export AWS_REGION=us-west-2
