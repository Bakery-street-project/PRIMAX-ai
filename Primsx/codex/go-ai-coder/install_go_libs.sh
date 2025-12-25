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

echo "Installing Go libraries..."
go install github.com/gin-gonic/gin@latest
go install github.com/gofiber/fiber/v2@latest
go install github.com/spf13/cobra@latest
go install github.com/spf13/viper@latest
go install gorm.io/gorm@latest
go install github.com/stretchr/testify@latest
go install github.com/prometheus/client_golang/prometheus@latest
go install google.golang.org/grpc@latest
go install cloud.google.com/go/storage@latest

echo "Go libraries installed!"
