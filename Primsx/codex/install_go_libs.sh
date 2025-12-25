#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - INSTALL_GO_LIBS.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

export PATH="$HOME/.local/go/bin:$PATH"
for pkg in \
  github.com/gin-gonic/gin \
  github.com/gofiber/fiber/v2 \
  github.com/spf13/cobra \
  github.com/spf13/viper \
  gorm.io/gorm \
  github.com/prometheus/client_golang/prometheus \
  google.golang.org/grpc \
  cloud.google.com/go/storage; do
    go install $pkg@latest || echo "Skipping $pkg"
done
