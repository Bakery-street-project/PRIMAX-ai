#!/usr/bin/env python3
"""
Upgrade PRIMAX to use uncensored coding model
"""

import subprocess
import os

def upgrade_model():
    """Upgrade from qwen2.5-coder:0.5b to more powerful model"""
    
    print("🚀 Upgrading PRIMAX to use more powerful coding model...")
    
    # Available powerful models
    models = {
        "qwen2.5-coder:7b": "4.7GB - Excellent coding, more context",
        "codellama:7b": "3.8GB - Meta's Code Llama (if available)", 
        "deepseek-coder:6.7b": "4.1GB - DeepSeek coding model",
        "llama3.1:8b": "4.7GB - Latest Llama with coding capabilities"
    }
    
    print("Available powerful models:")
    for model, desc in models.items():
        print(f"  • {model}: {desc}")
    
    # Recommend best for coding
    recommended = "qwen2.5-coder:7b"
    
    print(f"\n🎯 Recommended: {recommended}")
    print("   - 7B parameters for better code understanding")
    print("   - Specialized for coding tasks")
    print("   - Good balance of performance vs size")
    
    # Pull the model
    print(f"\n📥 Pulling {recommended}...")
    result = subprocess.run(["ollama", "pull", recommended], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Successfully pulled {recommended}")
        
        # Update PRIMAX configuration
        config_file = "src/llm/groq_client.py"
        if os.path.exists(config_file):
            print(f"🔧 To use this model in PRIMAX, update {config_file}")
            print("   Change: self.model = 'llama3-groq-70b-8192-tool-use-preview'")
            print(f"   To:     self.model = '{recommended}'")
        
        return True
    else:
        print(f"❌ Failed to pull {recommended}: {result.stderr}")
        return False

def show_cloud_deployment_options():
    """Show cloud deployment options for PRIMAX"""
    
    print("\n☁️  Cloud Deployment Options for PRIMAX:")
    print("=" * 50)
    
    options = {
        "Fly.io": {
            "cost": "$0-10/month",
            "specs": "3x VMs (256MB-1GB each)",
            "best_for": "Always-on, persistent storage",
            "model_support": "Full Ollama support"
        },
        "Railway": {
            "cost": "$5 credit/month",
            "specs": "1GB RAM, persistent disk",
            "best_for": "PostgreSQL included, easy scaling",
            "model_support": "Docker containers"
        },
        "Render": {
            "cost": "$7-25/month",
            "specs": "512MB-2GB RAM, persistent disk",
            "best_for": "Web services, auto-scaling",
            "model_support": "Docker deployment"
        },
        "VPS (Hetzner/Contabo)": {
            "cost": "$5-20/month",
            "specs": "2-8GB RAM, full control",
            "best_for": "Maximum performance, custom models",
            "model_support": "Run any model locally"
        }
    }
    
    for platform, details in options.items():
        print(f"\n{platform}:")
        print(f"  💰 Cost: {details['cost']}")
        print(f"  ⚙️  Specs: {details['specs']}")
        print(f"  🎯 Best for: {details['best_for']}")
        print(f"  🤖 Models: {details['model_support']}")

if __name__ == "__main__":
    # Upgrade model
    success = upgrade_model()
    
    # Show deployment options
    show_cloud_deployment_options()
    
    if success:
        print("\n✅ PRIMAX upgraded! Ready for cloud deployment with powerful coding model.")
    else:
        print("\n⚠️  Model upgrade failed, but PRIMAX still works with current model.")
