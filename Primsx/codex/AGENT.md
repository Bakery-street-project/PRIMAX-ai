# Coding Agent Workshop Environment

This directory contains the Coding Agent Workshop - a step-by-step guide to building your own AI coding assistant.

## Project Structure

```
coding-agent-workshop/
├── chat.go              # Version 1: Basic chat with Claude
├── read.go              # Version 2: Add file reading
├── list_files.go        # Version 3: Add directory listing
├── bash_tool.go         # Version 4: Add command execution
├── edit_tool.go         # Version 5: Add file editing
├── code_search_tool.go  # Version 6: Add code search
├── fizzbuzz.js          # Sample file for testing
├── riddle.txt           # Sample text file
├── AGENT.md             # This file
├── devenv.nix           # Development environment
└── env.example          # Environment variables template
```

## Environment Setup

### Option 1: Using devenv (Recommended)
```bash
devenv shell  # Loads Go, ripgrep, and other dependencies
```

### Option 2: Manual Setup
```bash
# Ensure Go 1.24+ is installed
go mod tidy
```

## API Key Setup

1. Sign up for a free AIMLAPI account at https://aimlapi.com/app/sign-up/
2. Copy `env.example` to `.env`
3. Add your API key: `AIMLAPI_API_KEY=your-key-here`

## Workshop Progression

Start with `chat.go` and work through each version to understand how tools are added incrementally.

Each version builds upon the previous one, adding new capabilities to the AI agent.
