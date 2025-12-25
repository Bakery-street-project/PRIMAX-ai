#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - RUN_AI.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================


echo "🤖 AI Coding Agent with System Access"
echo "======================================"
echo ""
echo "Starting AI agent with direct access to your system..."
echo "Using local Ollama model: llama3.2:3b"
echo ""
echo "Commands available:"
echo "  read <file_or_folder> - Read file content or all files in folder"
echo "  list <directory> - List directory contents"
echo "  quit/exit - Exit the program"
echo ""
echo "Examples:"
echo "  read fizzbuzz.js"
echo "  read /home/booze/Documents/Blackrockdata"
echo "  list /home/booze/Documents"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama server not running. Starting it now..."
    ollama serve &
    sleep 3
    echo "✅ Ollama server started"
fi

# Run the AI agent
go run read_simple.go
