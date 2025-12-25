#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - MONITOR_FILES.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e
TARGET_DIR=~/Desktop/superbrain-x
mkdir -p $TARGET_DIR/{cmd/server,codex,codex_v2,codex_wheel,deploy/terraform,flutter,internal/ai,openhands,web,integrations}
touch $TARGET_DIR/cmd/server/{main.go,validator.go}
touch $TARGET_DIR/codex/{aspects.go,energy.go,modules.go,nil.go,victory.go,theory.go}
touch $TARGET_DIR/codex_v2/{aspects.go,dynamics.go,modules.go,symbols.go,trios.go,victory.go}
touch $TARGET_DIR/codex_wheel/{energy.go,modules.go,wheel.go}
touch $TARGET_DIR/deploy/terraform/main.tf
touch $TARGET_DIR/flutter/README.md
touch $TARGET_DIR/internal/ai/stub.go
touch $TARGET_DIR/openhands/README.md
touch $TARGET_DIR/web/index.html
inotifywait -m $TARGET_DIR -e create -e moved_to |
    while read path action file; do
        echo "New file $file created in $path at $(date)"
    if [[ $file == sed* ]]; then continue; fi
    if [[ $file == sed* ]]; then continue; fi
        mkdir -p ~/backup-superbrain-x-$(date +%Y%m%d)
        cp $path/$file ~/backup-superbrain-x-$(date +%Y%m%d)/
    done &
