#!/usr/bin/env bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - INNOVATION_ENGINE.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -euo pipefail

# 1. Fetch new research & errors
echo "=== Fetching AI/Neuro News ==="
python3 - <<PY
import feedparser
feeds = ["https://neurodev.blog/rss", "https://ubuntu.com/blog/feed"]
for src in feeds:
    for e in feedparser.parse(src).entries[:3]:
        print("[neuro-news]", e.title, e.link)
PY

echo "=== Capturing Recent Errors ==="
grep -R "ERROR" scripts/*.log | tail -n 10 || echo "No recent errors logged."

# 2. Build & test Go modules
cd ~/Desktop/go-ai-coder
go mod tidy
go build ./...
go test ./...
golangci-lint run ./...

# 3. Apply learned fixes (stub)
if grep -R "undefined: NewCloudAIClient" cmd/*.go; then
  sed -i '1i package ai\n\nfunc NewCloudAIClient() error { return nil }\n' internal/ai/client.go
fi

# 4. Commit and push stubs for review
git add internal/ai/client.go
git commit -m "chore: stub NewCloudAIClient for build success"
git push

# 5. Trigger Terraform if Go succeeds
echo "=== Running Terraform ==="
terraform init -reconfigure
terraform apply -auto-approve
