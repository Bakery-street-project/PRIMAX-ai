#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - SUPERBRAIN-COMPLETE-SETUP.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

# ============================================================================
# SUPERBRAIN VERTEX AI DEPLOYMENT & GEMINI ANALYZER - COMPLETE SOLUTION
# ============================================================================
# This script provides a comprehensive, production-ready framework for:
# 1. Fixing Python/Gemini import issues
# 2. Deploying superbrain to Vertex AI
# 3. Creating interactive Gemini analysis capabilities
# 4. Full operational readiness checks
#
# Author: System Architect
# Date: October 22, 2025
# Environment: Ubuntu 25.10, Google Cloud Platform
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

log_header() {
    echo ""
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║  $1${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓ SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[⚠ WARN]${NC} $1"; }
log_error() { echo -e "${RED}[✗ ERROR]${NC} $1"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1"; }

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID="mythicnode"
REGION="europe-west1"
IMAGE_URI="europe-west1-docker.pkg.dev/mythicnode/my-repo/superbrain:latest"
ENDPOINT_DISPLAY_NAME="superbrain-endpoint"
MODEL_DISPLAY_NAME="superbrain-model"

# Vertex AI endpoint (already created from your output)
ENDPOINT_ID="758049495677140992"
ENDPOINT_RESOURCE="projects/886468743666/locations/europe-west1/endpoints/${ENDPOINT_ID}"

# ============================================================================
# PHASE 1: PYTHON ENVIRONMENT SETUP & GEMINI FIX
# ============================================================================

setup_python_environment() {
    log_header "PHASE 1: Python Environment Setup & Gemini Fix"
    
    log_step "1.1 - Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 not found! Installing..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    fi
    
    PYTHON_VERSION=$(python3 --version)
    log_success "Python detected: $PYTHON_VERSION"
    
    log_step "1.2 - Checking pip installation..."
    if ! command -v pip3 &> /dev/null; then
        log_warn "pip3 not found. Installing..."
        sudo apt-get install -y python3-pip
    fi
    
    PIP_VERSION=$(pip3 --version)
    log_success "pip detected: $PIP_VERSION"
    
    log_step "1.3 - Verifying Python and pip are aligned..."
    PYTHON_PATH=$(which python3)
    PIP_PATH=$(which pip3)
    log_info "Python path: $PYTHON_PATH"
    log_info "Pip path: $PIP_PATH"
    
    log_step "1.4 - Upgrading pip..."
    python3 -m pip install --upgrade pip --user || log_warn "Pip upgrade had issues (continuing...)"
    
    log_step "1.5 - Installing google-generativeai package..."
    python3 -m pip install --user --upgrade google-generativeai
    
    log_step "1.6 - Verifying installation..."
    if python3 -c "import google.generativeai" 2>/dev/null; then
        GENAI_VERSION=$(python3 -c "import google.generativeai as genai; print(genai.__version__)")
        log_success "google-generativeai installed successfully! Version: $GENAI_VERSION"
    else
        log_error "google-generativeai installation failed!"
        log_info "Trying alternative installation method..."
        
        # Create isolated virtual environment
        python3 -m venv ~/superbrain-env
        source ~/superbrain-env/bin/activate
        pip install --upgrade pip
        pip install google-generativeai
        
        if python3 -c "import google.generativeai" 2>/dev/null; then
            log_success "Installation successful in virtual environment!"
            log_warn "Note: You'll need to activate the venv before running Gemini scripts:"
            log_warn "  source ~/superbrain-env/bin/activate"
        else
            log_error "Installation failed even in virtual environment. Please check manually."
            return 1
        fi
    fi
    
    log_step "1.7 - Installing additional dependencies..."
    python3 -m pip install --user --upgrade jq google-cloud-aiplatform google-cloud-secret-manager
    
    log_success "Python environment setup complete!"
}

# ============================================================================
# PHASE 2: GEMINI API KEY SETUP
# ============================================================================

setup_gemini_api_key() {
    log_header "PHASE 2: Gemini API Key Setup"
    
    log_step "2.1 - Checking for existing API key..."
    
    if [ -n "$GEMINI_API_KEY" ]; then
        log_success "GEMINI_API_KEY already set in environment"
        return 0
    fi
    
    log_step "2.2 - Attempting to fetch from Secret Manager..."
    if gcloud secrets versions access latest --secret=gemini-api-key --project=$PROJECT_ID 2>/dev/null; then
        GEMINI_API_KEY=$(gcloud secrets versions access latest --secret=gemini-api-key --project=$PROJECT_ID)
        export GEMINI_API_KEY
        log_success "API key fetched from Secret Manager"
        
        # Save to bashrc for persistence
        if ! grep -q "export GEMINI_API_KEY" ~/.bashrc; then
            echo "export GEMINI_API_KEY='$GEMINI_API_KEY'" >> ~/.bashrc
            log_success "API key added to ~/.bashrc for future sessions"
        fi
        return 0
    fi
    
    log_warn "Secret not found in Secret Manager"
    log_info ""
    log_info "You need to set up your Gemini API key. Choose one option:"
    log_info ""
    log_info "Option 1: Get API key from Google AI Studio"
    log_info "  1. Visit: https://aistudio.google.com/app/apikey"
    log_info "  2. Create or copy your API key"
    log_info "  3. Run: export GEMINI_API_KEY='your-key-here'"
    log_info ""
    log_info "Option 2: Store in Secret Manager (recommended for production)"
    log_info "  1. Get your key from AI Studio (above)"
    log_info "  2. Run: echo -n 'your-key' | gcloud secrets create gemini-api-key --data-file=-"
    log_info ""
    
    read -p "Do you want to enter your API key now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -sp "Enter your Gemini API key: " GEMINI_API_KEY
        echo
        export GEMINI_API_KEY
        echo "export GEMINI_API_KEY='$GEMINI_API_KEY'" >> ~/.bashrc
        log_success "API key set for this session and saved to ~/.bashrc"
    else
        log_warn "Skipping API key setup. Gemini features will not work until you set it manually."
    fi
}

# ============================================================================
# PHASE 3: VERTEX AI DEPLOYMENT STATUS & MANAGEMENT
# ============================================================================

check_vertex_deployment() {
    log_header "PHASE 3: Vertex AI Deployment Status"
    
    log_step "3.1 - Checking existing endpoint..."
    if gcloud ai endpoints describe $ENDPOINT_ID --region=$REGION --project=$PROJECT_ID &>/dev/null; then
        log_success "Endpoint exists: $ENDPOINT_RESOURCE"
        
        # Get endpoint details
        ENDPOINT_INFO=$(gcloud ai endpoints describe $ENDPOINT_ID --region=$REGION --format=json)
        log_info "Endpoint display name: $(echo $ENDPOINT_INFO | jq -r '.displayName')"
        log_info "Create time: $(echo $ENDPOINT_INFO | jq -r '.createTime')"
    else
        log_warn "Endpoint not found. It may have been deleted."
        log_info "To recreate, run:"
        log_info "  gcloud ai endpoints create --region=$REGION --display-name=$ENDPOINT_DISPLAY_NAME"
    fi
    
    log_step "3.2 - Checking deployed models..."
    MODELS=$(gcloud ai models list --region=$REGION --format=json)
    MODEL_COUNT=$(echo $MODELS | jq '. | length')
    
    if [ "$MODEL_COUNT" -gt 0 ]; then
        log_success "Found $MODEL_COUNT model(s) in $REGION"
        echo $MODELS | jq -r '.[] | "  - \(.displayName) (ID: \(.name | split("/") | .[-1]))"'
    else
        log_warn "No models found in $REGION"
    fi
}

# ============================================================================
# PHASE 4: CREATE GEMINI ANALYZER SCRIPT
# ============================================================================

create_gemini_analyzer() {
    log_header "PHASE 4: Creating Gemini Analyzer Script"
    
    ANALYZER_SCRIPT="$HOME/superbrain_gemini_analyzer.py"
    
    cat > "$ANALYZER_SCRIPT" << 'PYSCRIPT'
#!/usr/bin/env python3
"""
Superbrain Gemini Analyzer - Interactive AI Assistant
Analyzes Docker container metadata and provides expert insights
"""

import os
import sys
import json

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai not installed")
    print("Run: python3 -m pip install --user google-generativeai")
    sys.exit(1)

def main():
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set")
        print("Set it with: export GEMINI_API_KEY='your-key'")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    
    # Read analysis file
    analysis_file = "/tmp/superbrain_analysis.txt"
    try:
        with open(analysis_file, 'r') as f:
            analysis_content = f.read()
    except FileNotFoundError:
        print(f"Warning: Analysis file not found: {analysis_file}")
        print("Continuing without pre-analysis context...")
        analysis_content = "No pre-analysis available."
    
    # Initialize model
    model = genai.GenerativeModel('gemini-1.5-pro')
    chat = model.start_chat(history=[])
    
    # Initial context
    if analysis_content != "No pre-analysis available.":
        initial_prompt = f"""You are an expert AI infrastructure analyst. I have a Docker container called 'superbrain' deployed on Google Cloud Platform Vertex AI.

Here is the technical analysis:

{analysis_content}

Based on this, please provide:
1. What this container does
2. Whether it's self-contained or API-connected
3. How to use it properly
4. Security recommendations
5. Deployment best practices

Be comprehensive but concise."""
        
        print("\n🤖 Analyzing superbrain container with Gemini...")
        print("=" * 70)
        response = chat.send_message(initial_prompt)
        print("\n📊 GEMINI ANALYSIS:\n")
        print(response.text)
        print("\n" + "=" * 70)
    else:
        print("\n🤖 Gemini ready for questions about superbrain deployment")
        print("=" * 70)
    
    # Interactive loop
    print("\n💬 Ask questions about superbrain (type 'exit' to quit)")
    print("   Examples:")
    print("   - How do I send requests to the endpoint?")
    print("   - What are the security considerations?")
    print("   - How do I monitor the deployment?")
    print("   - What's the cost structure?\n")
    
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            response = chat.send_message(user_input)
            print(f"\n🤖 Gemini: {response.text}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session ended.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
PYSCRIPT
    
    chmod +x "$ANALYZER_SCRIPT"
    log_success "Gemini analyzer created: $ANALYZER_SCRIPT"
}

# ============================================================================
# PHASE 5: CREATE OPERATIONAL GUIDE
# ============================================================================

create_operational_guide() {
    log_header "PHASE 5: Creating Operational Guide"
    
    GUIDE_FILE="$HOME/superbrain_operations_guide.md"
    
    cat > "$GUIDE_FILE" << 'GUIDEOF'
# Superbrain Operational Guide

## Quick Reference

### System Status
```bash
# Check Vertex AI endpoint
gcloud ai endpoints describe 758049495677140992 --region=europe-west1

# List all models
gcloud ai models list --region=europe-west1

# Check Docker image
docker images | grep superbrain
```

### Using the Endpoint

**Endpoint URL:**
```
https://europe-west1-aiplatform.googleapis.com/v1/projects/886468743666/locations/europe-west1/endpoints/758049495677140992:predict
```

**Example Prediction Request:**
```bash
# Using gcloud
gcloud ai endpoints predict 758049495677140992 \
  --region=europe-west1 \
  --json-request=request.json

# Using curl with authentication
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  https://europe-west1-aiplatform.googleapis.com/v1/projects/886468743666/locations/europe-west1/endpoints/758049495677140992:predict \
  -d @request.json
```

**Example request.json:**
```json
{
  "instances": [
    {
      "input": "your input data here"
    }
  ]
}
```

### Gemini Analysis

**Run interactive analyzer:**
```bash
python3 ~/superbrain_gemini_analyzer.py
```

**Ask Gemini specific questions:**
- Architecture and design patterns
- Security and access control
- Performance optimization
- Cost management
- Troubleshooting issues

### Monitoring & Logs

```bash
# View endpoint logs
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint AND resource.labels.endpoint_id=758049495677140992" --limit 50

# Monitor predictions
gcloud ai endpoints describe 758049495677140992 --region=europe-west1 --format="value(deployedModels[0].automaticResources)"
```

### Cost Management

```bash
# Check current billing
gcloud billing accounts list
gcloud billing projects describe mythicnode

# Estimate costs
# - Prediction requests: ~$0.0004 per request
# - Deployed model: ~$1.50 per hour
# - Traffic egress: varies by region
```

### Scaling & Performance

```bash
# Update deployment configuration
gcloud ai endpoints update 758049495677140992 \
  --region=europe-west1 \
  --min-replica-count=1 \
  --max-replica-count=10
```

### Security Best Practices

1. **API Key Management:**
   - Store in Secret Manager
   - Rotate regularly
   - Never commit to version control

2. **Access Control:**
   - Use service accounts with minimal permissions
   - Enable VPC Service Controls
   - Audit access logs regularly

3. **Network Security:**
   - Use Private Service Connect if possible
   - Enable Cloud Armor for DDoS protection
   - Implement request rate limiting

### Troubleshooting

**Endpoint not responding:**
```bash
# Check endpoint status
gcloud ai endpoints describe 758049495677140992 --region=europe-west1

# Check model deployment
gcloud ai models list --region=europe-west1 | grep superbrain

# View recent errors
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint AND severity>=ERROR" --limit 20
```

**Python import errors:**
```bash
# Reinstall packages
python3 -m pip install --user --upgrade google-generativeai google-cloud-aiplatform

# Check installation
python3 -c "import google.generativeai; print('OK')"
```

### Next Steps

1. Test the endpoint with sample data
2. Set up monitoring and alerting
3. Implement CI/CD pipeline for updates
4. Configure auto-scaling policies
5. Review and optimize costs

For detailed analysis, use: `python3 ~/superbrain_gemini_analyzer.py`
GUIDEOF
    
    log_success "Operational guide created: $GUIDE_FILE"
}

# ============================================================================
# PHASE 6: FINAL SYSTEM CHECK & SUMMARY
# ============================================================================

final_system_check() {
    log_header "PHASE 6: Final System Check & Summary"
    
    echo ""
    echo "📋 SYSTEM STATUS SUMMARY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Python check
    if python3 -c "import google.generativeai" 2>/dev/null; then
        echo "✅ Python Environment: OK"
    else
        echo "❌ Python Environment: google-generativeai not found"
    fi
    
    # API key check
    if [ -n "$GEMINI_API_KEY" ]; then
        echo "✅ Gemini API Key: Set"
    else
        echo "❌ Gemini API Key: Not set"
    fi
    
    # Docker image check
    if docker images | grep -q "superbrain"; then
        echo "✅ Docker Image: Available locally"
    else
        echo "⚠️  Docker Image: Not found locally (available in registry)"
    fi
    
    # Vertex AI endpoint check
    if gcloud ai endpoints describe $ENDPOINT_ID --region=$REGION &>/dev/null; then
        echo "✅ Vertex AI Endpoint: Active"
    else
        echo "❌ Vertex AI Endpoint: Not found"
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🚀 NEXT ACTIONS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1️⃣  Read the operational guide:"
    echo "   cat ~/superbrain_operations_guide.md"
    echo ""
    echo "2️⃣  Run Gemini analyzer for expert insights:"
    echo "   python3 ~/superbrain_gemini_analyzer.py"
    echo ""
    echo "3️⃣  Test your endpoint:"
    echo "   gcloud ai endpoints predict $ENDPOINT_ID --region=$REGION --json-request=request.json"
    echo ""
    echo "4️⃣  Monitor deployment:"
    echo "   gcloud ai endpoints describe $ENDPOINT_ID --region=$REGION"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    log_success "Setup complete! Your superbrain is ready for production."
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    clear
    log_header "SUPERBRAIN VERTEX AI - COMPLETE DEPLOYMENT FRAMEWORK"
    
    log_info "Starting comprehensive setup and deployment process..."
    log_info "This will configure Python, Gemini, and operational tools."
    echo ""
    
    # Execute all phases
    setup_python_environment
    setup_gemini_api_key
    check_vertex_deployment
    create_gemini_analyzer
    create_operational_guide
    final_system_check
    
    echo ""
    log_success "All phases complete! 🎉"
    echo ""
}

# Run main function
main "$@"
