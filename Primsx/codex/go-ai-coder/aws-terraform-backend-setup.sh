#!/usr/bin/env bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - AWS-TERRAFORM-BACKEND-SETUP.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e

# Replace these variables with your values
BUCKET="my-tf-state-bucket"
REGION="us-west-2"
TABLE="tf-state-lock"

# Create bucket
aws s3api create-bucket --bucket $BUCKET --region $REGION --create-bucket-configuration LocationConstraint=$REGION

# Enable encryption
aws s3api put-bucket-encryption --bucket $BUCKET --server-side-encryption-configuration '{
  "Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]
}'

# Create DynamoDB table
aws dynamodb create-table   --table-name $TABLE   --attribute-definitions AttributeName=LockID,AttributeType=S   --key-schema AttributeName=LockID,KeyType=HASH   --billing-mode PAY_PER_REQUEST

echo "AWS S3 bucket and DynamoDB table created for Terraform backend state/locking."
