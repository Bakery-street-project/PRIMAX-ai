#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - SETUP-CLOUD-ENVIRONMENT.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================


# Setup Cloud AI Environment for Go AI Coder
# This script sets up the complete environment for cloud AI deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLOUD_PROVIDER=${CLOUD_PROVIDER:-"aws"}
REGION=${REGION:-"us-west-2"}
GITHUB_TOKEN=${GITHUB_TOKEN:-""}

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running on supported OS
check_os() {
    log "Checking operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        error "Unsupported operating system: $OSTYPE"
    fi
    
    log "Operating system: $OS"
}

# Install required tools
install_tools() {
    log "Installing required tools..."
    
    # Check if tools are already installed
    command -v python3 >/dev/null 2>&1 || {
        log "Installing Python 3..."
        if [[ "$OS" == "linux" ]]; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif [[ "$OS" == "macos" ]]; then
            if command -v brew >/dev/null 2>&1; then
                brew install python3
            else
                error "Homebrew not found. Please install Python 3 manually."
            fi
        fi
    }
    
    command -v docker >/dev/null 2>&1 || {
        log "Installing Docker..."
        if [[ "$OS" == "linux" ]]; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
        elif [[ "$OS" == "macos" ]]; then
            if command -v brew >/dev/null 2>&1; then
                brew install --cask docker
            else
                error "Homebrew not found. Please install Docker manually."
            fi
        fi
    }
    
    command -v kubectl >/dev/null 2>&1 || {
        log "Installing kubectl..."
        if [[ "$OS" == "linux" ]]; then
            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
            sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
        elif [[ "$OS" == "macos" ]]; then
            if command -v brew >/dev/null 2>&1; then
                brew install kubectl
            else
                error "Homebrew not found. Please install kubectl manually."
            fi
        fi
    }
    
    command -v helm >/dev/null 2>&1 || {
        log "Installing Helm..."
        if [[ "$OS" == "linux" ]]; then
            curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
        elif [[ "$OS" == "macos" ]]; then
            if command -v brew >/dev/null 2>&1; then
                brew install helm
            else
                error "Homebrew not found. Please install Helm manually."
            fi
        fi
    }
    
    log "All required tools installed successfully"
}

# Install cloud provider CLI
install_cloud_cli() {
    log "Installing cloud provider CLI..."
    
    case $CLOUD_PROVIDER in
        "aws")
            command -v aws >/dev/null 2>&1 || {
                log "Installing AWS CLI..."
                if [[ "$OS" == "linux" ]]; then
                    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                    unzip awscliv2.zip
                    sudo ./aws/install
                    rm -rf aws awscliv2.zip
                elif [[ "$OS" == "macos" ]]; then
                    if command -v brew >/dev/null 2>&1; then
                        brew install awscli
                    else
                        error "Homebrew not found. Please install AWS CLI manually."
                    fi
                fi
            }
            
            command -v eksctl >/dev/null 2>&1 || {
                log "Installing eksctl..."
                if [[ "$OS" == "linux" ]]; then
                    curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
                    sudo mv /tmp/eksctl /usr/local/bin
                elif [[ "$OS" == "macos" ]]; then
                    if command -v brew >/dev/null 2>&1; then
                        brew install eksctl
                    else
                        error "Homebrew not found. Please install eksctl manually."
                    fi
                fi
            }
            ;;
        "gcp")
            command -v gcloud >/dev/null 2>&1 || {
                log "Installing gcloud CLI..."
                if [[ "$OS" == "linux" ]]; then
                    curl https://sdk.cloud.google.com | bash
                    exec -l $SHELL
                elif [[ "$OS" == "macos" ]]; then
                    if command -v brew >/dev/null 2>&1; then
                        brew install --cask google-cloud-sdk
                    else
                        error "Homebrew not found. Please install gcloud CLI manually."
                    fi
                fi
            }
            ;;
        "azure")
            command -v az >/dev/null 2>&1 || {
                log "Installing Azure CLI..."
                if [[ "$OS" == "linux" ]]; then
                    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
                elif [[ "$OS" == "macos" ]]; then
                    if command -v brew >/dev/null 2>&1; then
                        brew install azure-cli
                    else
                        error "Homebrew not found. Please install Azure CLI manually."
                    fi
                fi
            }
            ;;
    esac
    
    log "Cloud provider CLI installed successfully"
}

# Create Python virtual environment
setup_python_env() {
    log "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv go-ai-env
    source go-ai-env/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    cat > requirements.txt << 'EOF'
torch>=1.12.0
transformers>=4.21.0
datasets>=2.0.0
accelerate>=0.20.0
requests>=2.28.0
numpy>=1.21.0
scikit-learn>=1.1.0
tqdm>=4.64.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
redis>=4.3.0
flask>=2.2.0
gunicorn>=20.1.0
EOF
    
    pip install -r requirements.txt
    
    log "Python environment setup completed"
}

# Create environment configuration
create_env_config() {
    log "Creating environment configuration..."
    
    cat > .env << EOF
# Cloud AI Configuration
CLOUD_PROVIDER=$CLOUD_PROVIDER
REGION=$REGION
GITHUB_TOKEN=$GITHUB_TOKEN

# Model Configuration
MODEL_NAME=go-ai-model
BASE_MODEL=microsoft/DialoGPT-medium
OUTPUT_DIR=./go-ai-model
MAX_LENGTH=512
BATCH_SIZE=4
NUM_EPOCHS=3
LEARNING_RATE=5e-5

# API Configuration
API_KEY=$(openssl rand -hex 32)
PORT=8080

# Redis Configuration
REDIS_URL=localhost:6379
CACHE_TTL=300
RATE_LIMIT_WINDOW=60
MAX_REQUESTS=100

# Ollama Configuration
OLLAMA_URL=http://localhost:11434/v1
EOF
    
    log "Environment configuration created"
}

# Create project structure
create_project_structure() {
    log "Creating project structure..."
    
    mkdir -p {go-ai-model,data,logs,configs,scripts}
    
    # Create data directories
    mkdir -p data/{github,docs,examples,training}
    
    # Create config directories
    mkdir -p configs/{training,deployment,monitoring}
    
    # Create script directories
    mkdir -p scripts/{setup,deploy,monitor}
    
    log "Project structure created"
}

# Setup GitHub token
setup_github_token() {
    if [ -z "$GITHUB_TOKEN" ]; then
        warn "GitHub token not provided"
        echo "To get a GitHub token:"
        echo "1. Go to https://github.com/settings/tokens"
        echo "2. Click 'Generate new token'"
        echo "3. Select 'repo' scope"
        echo "4. Copy the token and run:"
        echo "   export GITHUB_TOKEN='your_token_here'"
        echo "   ./setup-cloud-environment.sh"
        return 1
    fi
    
    log "GitHub token configured"
}

# Test environment
test_environment() {
    log "Testing environment..."
    
    # Test Python
    python3 --version
    
    # Test Docker
    docker --version
    
    # Test kubectl
    kubectl version --client
    
    # Test Helm
    helm version
    
    # Test cloud CLI
    case $CLOUD_PROVIDER in
        "aws")
            aws --version
            ;;
        "gcp")
            gcloud --version
            ;;
        "azure")
            az --version
            ;;
    esac
    
    log "Environment test completed successfully"
}

# Main setup function
main() {
    log "Starting Go AI Cloud environment setup..."
    
    # Check OS
    check_os
    
    # Install tools
    install_tools
    
    # Install cloud CLI
    install_cloud_cli
    
    # Setup Python environment
    setup_python_env
    
    # Create project structure
    create_project_structure
    
    # Create environment configuration
    create_env_config
    
    # Setup GitHub token
    setup_github_token || {
        warn "Please set GITHUB_TOKEN and run the script again"
        exit 1
    }
    
    # Test environment
    test_environment
    
    log "Environment setup completed successfully!"
    
    # Print next steps
    echo ""
    echo "=========================================="
    echo "🚀 Go AI Cloud Environment Setup Complete"
    echo "=========================================="
    echo "Cloud Provider: $CLOUD_PROVIDER"
    echo "Region: $REGION"
    echo "Python Environment: go-ai-env"
    echo "Project Structure: Created"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Activate Python environment: source go-ai-env/bin/activate"
    echo "2. Train your custom model: python go-ai-model-trainer.py"
    echo "3. Deploy to cloud: ./deploy-cloud-ai.sh"
    echo "4. Update your client configuration"
    echo ""
}

# Run main function
main "$@"
