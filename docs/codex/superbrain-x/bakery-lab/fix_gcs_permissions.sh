#!/bin/bash
gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="serviceAccount:api-707@mythicnode.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
terraform init -reconfigure
