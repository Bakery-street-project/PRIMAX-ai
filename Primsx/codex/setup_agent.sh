#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - SETUP_AGENT.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

AGENT_REPO="agentic-experiments"
sudo mkdir -p /opt/$AGENT_REPO

sudo tee /opt/$AGENT_REPO/update_model.py > /dev/null <<PYEOF
#!/usr/bin/env python3
import time
print('Model update started at', time.strftime('%c'))
# TODO: Add retrain/update logic
PYEOF

sudo chmod +x /opt/$AGENT_REPO/update_model.py

sudo tee /etc/systemd/system/${AGENT_REPO}-update.service > /dev/null <<SERVICEEOF
[Unit]
Description=Self-Evolving Model Update for $AGENT_REPO

[Service]
Type=oneshot
ExecStart=/opt/$AGENT_REPO/update_model.py
SERVICEEOF

sudo tee /etc/systemd/system/${AGENT_REPO}-update.timer > /dev/null <<TIMEREOF
[Unit]
Description=Hourly Self-Evolving Model Update Timer for $AGENT_REPO

[Timer]
OnCalendar=hourly
Unit=${AGENT_REPO}-update.service

[Install]
WantedBy=timers.target
TIMEREOF

sudo systemctl daemon-reload
sudo systemctl enable --now ${AGENT_REPO}-update.timer
