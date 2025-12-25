#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - INSTALL.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================


# Go AI Coder - Secure Installation Script
# This script safely installs Go AI Coder to your system

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="go-ai-coder"
INSTALL_DIR="/usr/local/bin"
DATA_DIR="$HOME/.go-ai-coder"
DESKTOP_DIR="$HOME/.local/share/applications"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        log_info "Please run as a regular user. The script will use sudo when needed."
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check if Go is installed
    if ! command -v go &> /dev/null; then
        log_error "Go is not installed. Please install Go 1.21+ first."
        log_info "Visit: https://golang.org/doc/install"
        exit 1
    fi
    
    # Check Go version
    GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
    REQUIRED_VERSION="1.21"
    
    if ! printf '%s\n%s\n' "$REQUIRED_VERSION" "$GO_VERSION" | sort -V -C; then
        log_error "Go version $GO_VERSION is too old. Required: $REQUIRED_VERSION+"
        exit 1
    fi
    
    log_success "Go version $GO_VERSION is compatible"
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        log_warning "Ollama is not installed. You'll need to install it for AI features."
        log_info "Visit: https://ollama.ai/download"
    else
        log_success "Ollama is installed"
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed. Please install git first."
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

# Create data directory
create_data_dir() {
    log_info "Creating data directory..."
    mkdir -p "$DATA_DIR"/{config,logs,cache,learning}
    chmod 755 "$DATA_DIR"
    log_success "Data directory created: $DATA_DIR"
}

# Build the application
build_app() {
    log_info "Building $APP_NAME..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    cd "$PROJECT_DIR"
    
    # Install dependencies
    log_info "Installing dependencies..."
    go mod download
    go mod tidy
    
    # Build the application
    log_info "Compiling application..."
    go build -ldflags "-s -w" -o "$APP_NAME" cmd/main.go
    
    if [[ ! -f "$APP_NAME" ]]; then
        log_error "Build failed"
        exit 1
    fi
    
    log_success "Application built successfully"
}

# Install the application
install_app() {
    log_info "Installing $APP_NAME to $INSTALL_DIR..."
    
    # Copy binary
    sudo cp "$APP_NAME" "$INSTALL_DIR/"
    sudo chmod +x "$INSTALL_DIR/$APP_NAME"
    
    # Verify installation
    if command -v "$APP_NAME" &> /dev/null; then
        log_success "Application installed successfully"
    else
        log_error "Installation verification failed"
        exit 1
    fi
}

# Create desktop entry
create_desktop_entry() {
    log_info "Creating desktop entry..."
    
    mkdir -p "$DESKTOP_DIR"
    
    cat > "$DESKTOP_DIR/go-ai-coder.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Go AI Coder
Comment=AI-Powered Coding Assistant for Go Developers
Exec=$APP_NAME
Icon=terminal
Terminal=true
Categories=Development;IDE;TextEditor;
Keywords=AI;Coding;Go;Development;Assistant;
StartupNotify=true
StartupWMClass=go-ai-coder
EOF
    
    chmod +x "$DESKTOP_DIR/go-ai-coder.desktop"
    log_success "Desktop entry created"
}

# Create configuration file
create_config() {
    log_info "Creating default configuration..."
    
    cat > "$DATA_DIR/config.json" << EOF
{
  "model": "llama3.2:3b",
  "max_tokens": 2000,
  "temperature": 0.7,
  "ollama_url": "http://localhost:11434/v1",
  "learning_dir": "$DATA_DIR/learning",
  "cache_enabled": true,
  "auto_save": true,
  "verbose": false,
  "log_level": "info"
}
EOF
    
    chmod 600 "$DATA_DIR/config.json"
    log_success "Configuration file created"
}

# Create environment file template
create_env_template() {
    log_info "Creating environment file template..."
    
    cat > "$DATA_DIR/.env.example" << EOF
# Go AI Coder Environment Configuration
# Copy this file to .env and fill in your values

# AI Configuration
AI_MODEL=llama3.2:3b
AI_MAX_TOKENS=2000
AI_TEMPERATURE=0.7
OLLAMA_URL=http://localhost:11434/v1

# GitHub Integration (Optional)
# Get your token from: https://github.com/settings/tokens
GITHUB_TOKEN=your_github_token_here

# Application Settings
LEARNING_DIR=$DATA_DIR/learning
CACHE_ENABLED=true
AUTO_SAVE=true
VERBOSE=false
LOG_LEVEL=info
EOF
    
    chmod 600 "$DATA_DIR/.env.example"
    log_success "Environment template created"
}

# Setup shell completion
setup_completion() {
    log_info "Setting up shell completion..."
    
    # Create completion script
    sudo tee /etc/bash_completion.d/go-ai-coder > /dev/null << 'EOF'
# Go AI Coder bash completion
_go-ai-coder() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="--help --version --model --tokens --temp --ollama --learning --cache --autosave --verbose"
    
    if [[ ${cur} == -* ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

complete -F _go-ai-coder go-ai-coder
EOF
    
    log_success "Shell completion configured"
}

# Cleanup build artifacts
cleanup() {
    log_info "Cleaning up build artifacts..."
    rm -f "$APP_NAME"
    log_success "Cleanup complete"
}

# Main installation function
main() {
    echo "🚀 Go AI Coder Installation Script"
    echo "=================================="
    echo ""
    
    check_root
    check_requirements
    create_data_dir
    build_app
    install_app
    create_desktop_entry
    create_config
    create_env_template
    setup_completion
    cleanup
    
    echo ""
    echo "🎉 Installation Complete!"
    echo "========================"
    echo ""
    echo "Go AI Coder has been successfully installed to your system."
    echo ""
    echo "📁 Data Directory: $DATA_DIR"
    echo "🔧 Configuration: $DATA_DIR/config.json"
    echo "🌍 Environment: $DATA_DIR/.env.example"
    echo "🖥️  Desktop Entry: $DESKTOP_DIR/go-ai-coder.desktop"
    echo ""
    echo "🚀 Quick Start:"
    echo "  1. Copy $DATA_DIR/.env.example to $DATA_DIR/.env"
    echo "  2. Edit $DATA_DIR/.env with your settings"
    echo "  3. Run: $APP_NAME"
    echo ""
    echo "📚 Documentation: https://github.com/booze/go-ai-coder"
    echo "🐛 Issues: https://github.com/booze/go-ai-coder/issues"
    echo ""
    echo "Happy coding! 🎯"
}

# Run main function
main "$@"
