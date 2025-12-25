#!/usr/bin/env bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - SETUP_GO_AI_CODER.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -euo pipefail

# 1. Install or upgrade Go to latest 1.21.x
echo "Installing Go 1.21..."
GO_VERSION="1.21.7"
ARCH="amd64"
OS="linux"
wget -q https://golang.org/dl/go\${GO_VERSION}.\${OS}-\${ARCH}.tar.gz -O /tmp/go.tgz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf /tmp/go.tgz
rm /tmp/go.tgz
export PATH="/usr/local/go/bin:\$PATH"
echo "Go version: \$(go version)"

# 2. Install popular Go libraries & frameworks
echo "Installing popular Go packages..."
go install github.com/gin-gonic/gin@latest        # Web framework
go install github.com/labstack/echo/v4@latest     # Alternative web
go install github.com/gofiber/fiber/v2@latest     # Fast web
go install github.com/spf13/cobra@latest          # CLI apps
go install github.com/spf13/viper@latest          # Config
go install gorm.io/gorm@latest                    # ORM
go install github.com/stretchr/testify@latest     # Testing
go install github.com/prometheus/client_golang/prometheus@latest  # Monitoring

# 3. Clone the go-ai-coder repository on desktop
DESKTOP_DIR="\$HOME/Desktop"
REPO_URL="https://github.com/Bakery-street-project/go-ai-coder.git"
TARGET="\${DESKTOP_DIR}/go-ai-coder"
echo "Cloning repo to \${TARGET}..."
rm -rf "\${TARGET}"
git clone "\${REPO_URL}" "\${TARGET}"

# 4. Build and test the project
cd "\${TARGET}"
echo "Tidying modules..."
go mod tidy
echo "Building project..."
go build -o go-ai-coder cmd/main.go
echo "Running tests..."
go test ./...
echo "Project built and tested successfully."

