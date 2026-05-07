from fastapi import FastAPI, HTTPException
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
    
    if any(word in query_lower for word in ["code", "programming", "function", "algorithm"]):
        model_key = "coding"
    elif any(word in query_lower for word in ["wise", "wisdom", "dragon", "ancient", "mysterious"]):
        model_key = "wisdom"
    else:
        model_key = "default"
    
    return router["models"][router["routing_rules"].get(model_key, "dragon_wise")]

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
        
        full_prompt = f"System: You are a helpful AI assistant.\nUser: {prompt}\nAssistant:"
        stdout, stderr = process.communicate(input=full_prompt, timeout=timeout)
        
        if process.returncode == 0:
            return stdout.strip()
        else:
            return f"Error: Model {model} failed with return code {process.returncode}"
            
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
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
