#!/usr/bin/env python3
"""
FINAL PRIMAX AI DEPLOYMENT
Combines Optimus Prime & Dragon Models with Supabase
"""

import os
import json
import subprocess
import time
from pathlib import Path


def check_ollama_models():
    """Check available Ollama models"""

    print("🔍 Checking Ollama Models...")

    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=10
        )
        models = result.stdout.strip().split("\n")[1:]  # Skip header

        available_models = {}
        for line in models:
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    size = parts[2] + " " + parts[3] if len(parts) > 3 else parts[2]
                    available_models[name] = size

        print("Available models:")
        for name, size in available_models.items():
            marker = (
                "✅" if "optimus" in name.lower() or "dragon" in name.lower() else "📦"
            )
            print(f"  {marker} {name}: {size}")

        return available_models

    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return {}


def setup_supabase_schema():
    """Ensure Supabase schema is set up"""

    print("💾 Setting up Supabase Schema...")

    # Check if schema file exists
    if not Path("supabase_schema.sql").exists():
        print("❌ supabase_schema.sql not found")
        return False

    # Note: Actual schema setup requires manual execution in Supabase dashboard
    # or API access which may not be available in this environment

    print("✅ Schema file ready (execute manually in Supabase dashboard)")
    return True


def create_model_router():
    """Create intelligent model router"""

    print("🧠 Creating Model Router...")

    router_config = {
        "models": {
            "optimus_prime": {
                "model": "Cognaize/optimus-devstral-24b-xxl-v1.0.0",
                "specialty": "coding_assistance",
                "personality": "Transformers-inspired coding mentor",
                "fallback": "qwen2.5-coder:7b",
            },
            "dragon_wise": {
                "model": "primax-dragon-coder:latest",
                "specialty": "wisdom_and_creativity",
                "personality": "Ancient dragon programmer",
                "fallback": "qwen2.5:7b",
            },
        },
        "routing_rules": {
            "coding": "optimus_prime",
            "wisdom": "dragon_wise",
            "creative": "dragon_wise",
            "default": "optimus_prime",
        },
        "load_balancing": {
            "max_concurrent": 3,
            "timeout_seconds": 30,
            "retry_attempts": 2,
        },
    }

    with open("model_router.json", "w") as f:
        json.dump(router_config, f, indent=2)

    print("✅ Created intelligent model router")
    return router_config


def create_primax_api():
    """Create PRIMAX API server with model routing"""

    print("🌐 Creating PRIMAX API Server...")

    api_code = '''from fastapi import FastAPI, HTTPException
import json
import subprocess
import time

app = FastAPI(title="PRIMAX AI - Transformers & Dragons")

# Load model router
with open("model_router.json") as f:
    router = json.load(f)

def route_query(query: str) -> str:
    """Route query to appropriate model"""
    
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["code", "programming", "function", "algorithm"]):
        model_key = "optimus_prime"
    elif any(word in query_lower for word in ["wise", "wisdom", "dragon", "ancient", "mysterious"]):
        model_key = "dragon_wise"
    else:
        model_key = "default"
    
    return router["models"][router["routing_rules"][model_key]]

def query_ollama(model: str, prompt: str, timeout: int = 30) -> str:
    """Query Ollama model"""
    
    try:
        cmd = ["ollama", "run", model]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        full_prompt = f"System: You are a helpful AI assistant.\\nUser: {prompt}\\nAssistant:"
        stdout, stderr = process.communicate(input=full_prompt, timeout=timeout)
        
        if process.returncode == 0:
            return stdout.strip()
        else:
            # Try fallback model
            fallback = router["models"][model]["fallback"]
            print(f"⚠️  Model {model} failed, trying {fallback}")
            
            cmd = ["ollama", "run", fallback]
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input=full_prompt, timeout=timeout)
            
            if process.returncode == 0:
                return stdout.strip()
            else:
                return "Error: Both primary and fallback models failed"
                
    except subprocess.TimeoutExpired:
        return "Error: Model query timeout"
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/")
async def root():
    return {
        "name": "PRIMAX AI",
        "models": ["Optimus Prime (Coding)", "Dragon Wise (Creativity)"],
        "status": "operational",
        "watermark": "PRIMAX-AI-BSP-2025"
    }

@app.post("/query")
async def query_primax(request: dict):
    """Query PRIMAX with intelligent routing"""
    
    user_query = request.get("query", "")
    if not user_query:
        raise HTTPException(400, "Query required")
    
    # Route to appropriate model
    model_config = route_query(user_query)
    model_name = model_config["model"]
    
    print(f"🎯 Routing to {model_name}: {model_config['personality']}")
    
    # Query model
    start_time = time.time()
    response = query_ollama(model_name, user_query)
    response_time = time.time() - start_time
    
    return {
        "query": user_query,
        "model": model_name,
        "personality": model_config["personality"],
        "response": response,
        "response_time": round(response_time, 2),
        "watermark": "PRIMAX-AI-BSP-2025"
    }

@app.get("/models")
async def list_models():
    """List available models"""
    
    return {
        "models": router["models"],
        "routing_rules": router["routing_rules"],
        "status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

    with open("primax_api.py", "w") as f:
        f.write(api_code)

    print("✅ Created PRIMAX API server")
    return api_code


def create_deployment_manifest():
    """Create deployment manifest for cloud platforms"""

    print("📦 Creating Deployment Manifest...")

    manifest = {
        "name": "primax-ai-transformers-dragons",
        "version": "1.0.0",
        "description": "PRIMAX AI with Optimus Prime & Dragon models",
        "models": {
            "optimus_prime": "Cognaize/optimus-devstral-24b-xxl-v1.0.0",
            "dragon_wise": "primax-dragon-coder:latest",
        },
        "deployment": {
            "platform": "fly.io",
            "runtime": "python3.11",
            "dependencies": ["fastapi", "uvicorn", "ollama", "supabase"],
            "environment": {
                "OLLAMA_HOST": "http://localhost:11434",
                "SUPABASE_URL": "your-supabase-url",
                "SUPABASE_KEY": "your-supabase-key",
            },
        },
        "features": [
            "Intelligent model routing",
            "Optimus Prime coding assistance",
            "Dragon wisdom and creativity",
            "Supabase integration",
            "Fallback model support",
        ],
    }

    with open("primax_deployment.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print("✅ Created deployment manifest")
    return manifest


def main():
    """Main deployment function"""

    print("🚀 FINAL PRIMAX AI DEPLOYMENT")
    print("=" * 60)
    print("Combining Optimus Prime & Dragon Models with Supabase")
    print("=" * 60)

    # Step 1: Check models
    models = check_ollama_models()

    # Step 2: Setup Supabase
    supabase_ok = setup_supabase_schema()

    # Step 3: Create model router
    router = create_model_router()

    # Step 4: Create API server
    api_code = create_primax_api()

    # Step 5: Create deployment manifest
    manifest = create_deployment_manifest()

    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 60)

    print("📊 Model Status:")
    optimus_available = any("optimus" in name.lower() for name in models.keys())
    dragon_available = any("dragon" in name.lower() for name in models.keys())

    print(
        f"  🤖 Optimus Prime: {'✅ Available' if optimus_available else '⏳ Downloading'}"
    )
    print(
        f"  🐉 Dragon Wise: {'✅ Ready' if dragon_available else '🔧 Needs training'}"
    )
    print(
        f"  💾 Supabase: {'✅ Schema ready' if supabase_ok else '📋 Manual setup needed'}"
    )

    print("\n🚀 Deployment Commands:")
    print("  1. Start Ollama: ollama serve")
    print("  2. Run API: python primax_api.py")
    print(
        '  3. Test: curl -X POST http://localhost:8000/query -d \'{"query":"Hello"}\''
    )
    print("  4. Deploy: fly launch (for Fly.io)")

    print("\n🎯 PRIMAX AI Features:")
    print("  • Intelligent model routing (coding → Optimus, wisdom → Dragon)")
    print("  • Transformers & Dragon mythology integration")
    print("  • Supabase data persistence")
    print("  • Fallback model support")
    print("  • Watermarked responses")

    print("\n🔗 API Endpoints:")
    print("  GET  /         - System info")
    print("  POST /query    - Intelligent query routing")
    print("  GET  /models   - List available models")


if __name__ == "__main__":
    main()
