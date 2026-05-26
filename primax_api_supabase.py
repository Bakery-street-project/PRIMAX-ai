from fastapi import FastAPI, HTTPException, Request
import json
import subprocess
import time

app = FastAPI(title="PRIMAX AI - Transformers & Dragons")

# Load model router
with open("model_router.json") as f:
    router = json.load(f)


def route_query(query: str) -> dict:
    """Route query to appropriate model"""

    query_lower = query.lower()

    if any(
        word in query_lower for word in ["code", "programming", "function", "algorithm"]
    ):
        model_key = "coding"
    elif any(
        word in query_lower
        for word in ["wise", "wisdom", "dragon", "ancient", "mysterious"]
    ):
        model_key = "wisdom"
    else:
        model_key = "default"

    return router["models"][router["routing_rules"].get(model_key, "dragon_wise")]


def check_model_available(model_name: str) -> bool:
    """Check if a model is available in Ollama"""
    try:
        import subprocess

        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        return model_name in result.stdout
    except:
        return False


def query_ollama(model: str, prompt: str, timeout: int = 30) -> str:
    """Query Ollama model"""

    try:
        cmd = ["ollama", "run", model]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        full_prompt = (
            f"System: You are a helpful AI assistant.\nUser: {prompt}\nAssistant:"
        )
        stdout, stderr = process.communicate(input=full_prompt, timeout=timeout)

        if process.returncode == 0:
            return stdout.strip()
        else:
            # Try fallback model
            fallback = router["models"][model]["fallback"]
            print(f"⚠️  Model {model} failed, trying {fallback}")

            cmd = ["ollama", "run", fallback]
            process = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
            )
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
        "watermark": "PRIMAX-AI-BSP-2025",
    }


# Supabase Integration (Optional)
import os

try:
    from supabase import create_client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_ENABLED = True
else:
    supabase = None
    SUPABASE_ENABLED = False


def log_to_supabase(model_name, query, response, response_time, request=None):
    """Log usage to Supabase (if available)"""
    if not SUPABASE_ENABLED:
        print(
            f"📊 Local log: {model_name} - {len(query)} chars query, {response_time}ms"
        )
        return

    try:
        supabase.rpc(
            "log_model_usage",
            {
                "p_model_name": model_name,
                "p_query": query,
                "p_response_length": len(response),
                "p_response_time": response_time,
                "p_ip_address": request.client.host if request else None,
                "p_user_agent": request.headers.get("user-agent") if request else None,
            },
        )
        print(f"✅ Supabase log: {model_name}")
    except Exception as e:
        print(f"⚠️ Supabase logging error: {e}")


@app.post("/query")
async def query_primax(request: dict, req: Request = None):
    """Query PRIMAX with intelligent routing"""

    user_query = request.get("query", "")
    if not user_query:
        raise HTTPException(400, "Query required")

    model_config = route_query(user_query)
    model_name = model_config["model"]

    print(f"🎯 Routing to {model_name}: {model_config['personality']}")

    start_time = time.time()
    response = query_ollama(model_name, user_query)
    response_time = time.time() - start_time

    return {
        "query": user_query,
        "model": model_name,
        "personality": model_config["personality"],
        "response": response,
        "response_time": round(response_time, 2),
        "watermark": "PRIMAX-AI-BSP-2025",
    }


@app.get("/models")
async def list_models():
    """List available models"""

    return {
        "models": router["models"],
        "routing_rules": router["routing_rules"],
        "status": "active",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
