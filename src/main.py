#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          PRIMAX AI - Main Application                         ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-MAIN-BSP-2025                                           ║
║  LICENSE: See LICENSE_PROPRIETARY.md                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import sys
import os
from pathlib import Path
from datetime import datetime
import logging
from collections import defaultdict
import time
import json
import subprocess

# Setup logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("primax-ai")

# Add Smoothoperator to path if available
sys.path.append(str(Path(__file__).parent.parent.parent / "Smoothoperator" / "src"))

# Import AutomationCodex Brain
try:
    from brain import (
        graph_connectivity,
        snn_activity_pattern,
        dynamic_systems_think,
    )

    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False
    logger.warning("AutomationCodex Brain not available - running in lite mode")

# Import Chat Manager
try:
    from chat import ChatManager

    CHAT_AVAILABLE = True
except ImportError:
    CHAT_AVAILABLE = False
    logger.warning("Chat module not available")

# Import GitHub Scanner
try:
    from github_scanner import GitHubScanner

    SCANNER_AVAILABLE = True
except ImportError:
    SCANNER_AVAILABLE = False
    logger.warning("GitHub Scanner not available")

# Import Groq LLM Client
try:
    from llm import GroqClient

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LLM module not available")

# Import NVIDIA NIM Client
try:
    from llm import NimClient

    NIM_AVAILABLE = True
except ImportError:
    NIM_AVAILABLE = False
    logger.warning("NVIDIA NIM client not available")

# ═══════════════════════════════════════════════════════════════════════════════
# Constants & Configuration
# ═══════════════════════════════════════════════════════════════════════════════

WATERMARK = "PRIMAX-AI-BSP-2025"
VERSION = "1.0.0"
COPYRIGHT = "Copyright © 2024-2025 Bakery Street Project"

# Security Configuration - PROTOCOL V2
# Load from Blackout Vault (local) or Environment Variables (cloud)
vault_path = os.path.expanduser("~/my-app-vault/secrets/.env")
if os.path.exists(vault_path):
    # Local deployment - load from vault
    from dotenv import load_dotenv

    load_dotenv(vault_path)
    API_KEY = os.getenv("PRIMAX_API_KEY")
    if not API_KEY:
        raise ValueError("CRITICAL: Vault found but PRIMAX_API_KEY missing")
    logger.info("✅ SECURE: Rotated key loaded from Blackout Vault")
else:
    # Cloud deployment - load from environment variables
    API_KEY = os.getenv("PRIMAX_API_KEY")
    if not API_KEY:
        logger.warning(
            "⚠️  PRIMAX_API_KEY not set - API authentication will be disabled"
        )
        API_KEY = "dev-mode-no-auth"  # Fallback for development
    else:
        logger.info("✅ SECURE: API key loaded from environment variables (cloud mode)")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Supabase Integration (Optional)
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


# Load model router
try:
    # Try multiple possible locations for model_router.json
    router_paths = [
        "model_router.json",  # Current directory
        "../model_router.json",  # Parent directory (from src/)
        os.path.join(
            os.path.dirname(__file__), "..", "model_router.json"
        ),  # Absolute path
    ]

    router_file = None
    for path in router_paths:
        if os.path.exists(path):
            router_file = path
            break

    if router_file:
        with open(router_file) as f:
            router = json.load(f)
        MODEL_ROUTER_AVAILABLE = True
        logger.info(f"✅ Model router loaded from {router_file}")
    else:
        raise FileNotFoundError("model_router.json not found in any expected location")
except (FileNotFoundError, json.JSONDecodeError) as e:
    router = None
    MODEL_ROUTER_AVAILABLE = False
    logger.warning(
        f"model_router.json not found or invalid - Ollama routing disabled: {e}"
    )


def route_query(query: str) -> dict:
    """Route query to appropriate model"""
    if not MODEL_ROUTER_AVAILABLE:
        return {"model": "qwen2.5:7b", "personality": "AI Assistant"}

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
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        return model_name in result.stdout
    except Exception:
        return False


def query_ollama(model: str, prompt: str, timeout: int = None) -> str:
    """
    Query Ollama via the streaming HTTP API instead of `ollama run` subprocess.
    Streaming avoids the wall-clock timeout that bites 1.5B+ models on CPU.

    Timeout falls back to OLLAMA_GENERATION_TIMEOUT (default 300s).
    """
    # Load OLLAMA settings from package or fallback to module-level defaults
    try:
        from src.config import OLLAMA_HOST, OLLAMA_GENERATION_TIMEOUT
    except ImportError:
        try:
            from config import OLLAMA_HOST, OLLAMA_GENERATION_TIMEOUT
        except ImportError:
            OLLAMA_HOST = "http://127.0.0.1:11434"
            OLLAMA_GENERATION_TIMEOUT = 300

    timeout = timeout if timeout is not None else OLLAMA_GENERATION_TIMEOUT

    try:
        import ollama

        client = ollama.Client(host=OLLAMA_HOST, timeout=timeout)
        chunks = []
        for chunk in client.chat(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        ):
            piece = (chunk.get("message") or {}).get("content", "")
            if piece:
                chunks.append(piece)
        return (
            "".join(chunks).strip() or f"Error: model {model} returned empty response"
        )
    except ImportError:
        # Fall back to subprocess if `ollama` package is missing
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
        try:
            stdout, _ = process.communicate(input=full_prompt, timeout=timeout)
            return (
                stdout.strip()
                if process.returncode == 0
                else f"Error: Model {model} failed (rc={process.returncode})"
            )
        except subprocess.TimeoutExpired:
            process.kill()
            return f"Error: model query timed out after {timeout}s"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


# Rate limiting
rate_limit_store: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW = 60  # seconds

# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════════


class HealthResponse(BaseModel):
    status: str
    version: str
    watermark: str
    timestamp: str


class AutomationRequest(BaseModel):
    task: str = Field(..., description="Automation task description")
    mode: str = Field(default="safe", description="Execution mode: safe, experimental")
    parameters: Optional[Dict[str, Any]] = None


class AutomationResponse(BaseModel):
    success: bool
    task_id: str
    result: Optional[Any] = None
    message: str
    watermark: str = WATERMARK


class CodeGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Code generation prompt")
    language: str = Field(default="python", description="Target language")
    framework: Optional[str] = None


class CodeGenerationResponse(BaseModel):
    code: str
    language: str
    watermark: str = WATERMARK
    license_header: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(
        None, description="Session ID (optional, creates new if not provided)"
    )
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    session_id: str
    response: str
    context: Dict[str, Any]
    message_count: int
    watermark: str = WATERMARK


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    created_at: str
    last_active: str
    watermark: str = WATERMARK


class RepoAnalysisRequest(BaseModel):
    repo_full_name: str = Field(..., description="Full repository name (owner/repo)")


class OrgScanRequest(BaseModel):
    org_name: str = Field(..., description="Organization name")
    limit: Optional[int] = Field(100, description="Maximum repositories to scan")


class RepoSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: Optional[int] = Field(20, description="Maximum results")


class OllamaQueryRequest(BaseModel):
    query: str = Field(..., description="Query to send to Ollama model")
    model: Optional[str] = Field(
        None, description="Specific model to use (auto-routed if not provided)"
    )


class CodeGenerationRequestV2(BaseModel):
    prompt: str = Field(..., description="What code to generate")
    language: Optional[str] = Field("python", description="Programming language")
    context: Optional[str] = Field(None, description="Additional context")


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Context Manager
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info(f"🚀 PRIMAX AI v{VERSION} starting...")
    logger.info(f"   Watermark: {WATERMARK}")
    logger.info(f"   {COPYRIGHT}")

    yield

    # Shutdown
    logger.info("🛑 PRIMAX AI shutting down...")


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="PRIMAX AI",
    description="Autonomous DevOps Agent on Decentralized Cloud",
    version=VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS middleware - RESTRICTED
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://primax-neuromorphic.fly.dev"],  # Only self
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

# Initialize Chat Manager, GitHub Scanner, and LLM Client
chat_manager = ChatManager() if CHAT_AVAILABLE else None
github_scanner = GitHubScanner() if SCANNER_AVAILABLE else None
groq_client = GroqClient() if LLM_AVAILABLE else None
nim_client = NimClient() if NIM_AVAILABLE else None

# ═══════════════════════════════════════════════════════════════════════════════
# Middleware
# ═══════════════════════════════════════════════════════════════════════════════


def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key authentication"""
    if api_key is None or api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key


def rate_limit_check(request: Request):
    """Check rate limiting"""
    client_ip = request.client.host
    now = time.time()

    # Clean old requests
    rate_limit_store[client_ip] = [
        req_time
        for req_time in rate_limit_store[client_ip]
        if now - req_time < RATE_LIMIT_WINDOW
    ]

    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    rate_limit_store[client_ip].append(now)
    return True


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security + watermark middleware"""
    # Skip auth for health check
    if request.url.path != "/health":
        rate_limit_check(request)

    response = await call_next(request)
    response.headers["X-Primax-Watermark"] = WATERMARK
    response.headers["X-Primax-Version"] = VERSION
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/")
async def root():
    """Root endpoint with watermark"""
    return {
        "name": "PRIMAX AI",
        "version": VERSION,
        "watermark": WATERMARK,
        "copyright": COPYRIGHT,
        "status": "operational",
        "docs": "/api/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=VERSION,
        watermark=WATERMARK,
        timestamp=datetime.now().isoformat(),
    )


@app.get("/api/v1/watermark")
async def get_watermark():
    """Get watermark information"""
    return {
        "watermark": WATERMARK,
        "version": VERSION,
        "copyright": COPYRIGHT,
        "license": "Proprietary - See LICENSE_PROPRIETARY.md",
    }


@app.post("/api/v1/automate", response_model=AutomationResponse)
async def run_automation(
    request: AutomationRequest, api_key: str = Depends(verify_api_key)
):
    """
    Run automation task using Dream Script Engine

    This endpoint integrates with Smoothoperator's Dream Script Engine
    """
    try:
        # Try to import Dream Script Engine
        try:
            from dream_script_engine import DreamScriptEngineSingularity

            # Initialize engine
            _engine = DreamScriptEngineSingularity()

            # Process task (simplified for MVP)
            result = {
                "processed": True,
                "task": request.task,
                "mode": request.mode,
                "parameters": request.parameters,
            }

            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            return AutomationResponse(
                success=True,
                task_id=task_id,
                result=result,
                message="Automation task queued successfully",
            )

        except ImportError:
            # Fallback if Smoothoperator not available
            logger.warning("Dream Script Engine not available, using fallback")
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            return AutomationResponse(
                success=True,
                task_id=task_id,
                result={"simulated": True},
                message="Automation simulated (Dream Engine not loaded)",
            )

    except Exception as e:
        logger.error(f"Automation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate-code", response_model=CodeGenerationResponse)
async def generate_code(
    request: CodeGenerationRequest, api_key: str = Depends(verify_api_key)
):
    """
    Generate code with watermark and license
    """
    try:
        # Generate license header
        license_header = f'''"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     Generated by PRIMAX AI - BSP 2025                         ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: {WATERMARK}                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
'''

        # Simple code generation (placeholder for LLM integration)
        code_template = f'''
# Task: {request.prompt}
# Language: {request.language}
# Generated: {datetime.now().isoformat()}

def generated_function():
    """
    Generated function based on prompt: {request.prompt}
    """
    # TODO: Implement functionality
    pass

if __name__ == "__main__":
    generated_function()
'''

        full_code = license_header + code_template

        return CodeGenerationResponse(
            code=full_code, language=request.language, license_header=license_header
        )

    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/status")
async def get_status():
    """Get system status"""
    return {
        "primax": "operational",
        "brain_available": BRAIN_AVAILABLE,
        "brain_type": "neuromorphic_mathematical" if BRAIN_AVAILABLE else "none",
        "smoothoperator_integrated": os.path.exists("../Smoothoperator"),
        "vault_available": os.path.exists("./vault"),
        "watermark": WATERMARK,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/v1/brain/analyze-resilience")
async def analyze_system_resilience(
    adjacency_matrix: List[List[int]], api_key: str = Depends(verify_api_key)
):
    """
    Analyze system resilience using graph theory (eigenvalues)

    The AutomationCodex brain uses eigenvalue analysis, not LLMs!
    """
    if not BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain module not available")

    try:
        import numpy as np

        adjacency = np.array(adjacency_matrix)
        eigenvalues = graph_connectivity(adjacency)

        return {
            "eigenvalues": eigenvalues.tolist(),
            "resilience_score": float(np.max(np.real(eigenvalues))),
            "method": "graph_theory_eigenvalues",
            "watermark": WATERMARK,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/brain/neural-activity")
async def get_neural_activity(
    size: int = 20, tmax: int = 100, api_key: str = Depends(verify_api_key)
):
    """
    Get Spiking Neural Network activity pattern

    Mathematical pattern analysis, not trained neural networks!
    """
    if not BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain module not available")

    try:
        activity = snn_activity_pattern(size=size, tmax=tmax)

        return {
            "activity_pattern": activity.tolist(),
            "network_size": size,
            "time_steps": tmax,
            "method": "spiking_neural_network",
            "watermark": WATERMARK,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/brain/predict-scaling")
async def predict_scaling(vm_capacity: int, api_key: str = Depends(verify_api_key)):
    """
    Predict system scaling using dynamic systems theory

    Uses the "Hitchhiker's Equation" - logistic growth model!
    """
    if not BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain module not available")

    try:
        solution = dynamic_systems_think(vm_capacity)

        return {
            "scaling_solution": str(solution),
            "vm_capacity": vm_capacity,
            "method": "dynamic_systems_logistic_growth",
            "equation": "dx/dt = 0.5*x*(1 - x/vm_capacity)",
            "watermark": WATERMARK,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Chat Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with PRIMAX AI

    Conversational interface with context memory.
    No API key required for basic chat.
    """
    if not CHAT_AVAILABLE or not chat_manager:
        raise HTTPException(status_code=503, detail="Chat module not available")

    try:
        result = chat_manager.process_message(
            session_id=request.session_id or "",
            user_message=request.message,
            context=request.context,
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chat/sessions")
async def list_chat_sessions():
    """List recent chat sessions"""
    if not CHAT_AVAILABLE or not chat_manager:
        raise HTTPException(status_code=503, detail="Chat module not available")

    sessions = chat_manager.list_sessions(limit=20)
    return {"sessions": sessions, "watermark": WATERMARK}


@app.get("/api/v1/chat/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    if not CHAT_AVAILABLE or not chat_manager:
        raise HTTPException(status_code=503, detail="Chat module not available")

    session = chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return ChatHistoryResponse(
        session_id=session.session_id,
        messages=session.get_history(),
        created_at=session.created_at,
        last_active=session.last_active,
    )


@app.delete("/api/v1/chat/{session_id}")
async def delete_chat_session(session_id: str, api_key: str = Depends(verify_api_key)):
    """Delete a chat session (requires API key)"""
    if not CHAT_AVAILABLE or not chat_manager:
        raise HTTPException(status_code=503, detail="Chat module not available")

    success = chat_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True, "message": "Session deleted", "watermark": WATERMARK}


# ═══════════════════════════════════════════════════════════════════════════════
# GitHub Scanner Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/analyze-repo")
async def analyze_repository(
    request: RepoAnalysisRequest, api_key: str = Depends(verify_api_key)
):
    """
    Analyze a GitHub repository

    Returns detailed analysis including stars, forks, languages, topics, etc.
    """
    if not SCANNER_AVAILABLE or not github_scanner:
        raise HTTPException(status_code=503, detail="GitHub Scanner not available")

    try:
        analysis = github_scanner.analyze_repo(request.repo_full_name)

        if not analysis:
            raise HTTPException(
                status_code=404, detail="Repository not found or analysis failed"
            )

        return {
            "success": True,
            "repository": analysis.to_dict(),
            "watermark": WATERMARK,
        }

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Repo analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scan-organization")
async def scan_organization(
    request: OrgScanRequest, api_key: str = Depends(verify_api_key)
):
    """
    Scan entire GitHub organization

    Analyzes all repositories in the organization and provides aggregate statistics.
    Perfect for analyzing Baker Street Project!
    """
    if not SCANNER_AVAILABLE or not github_scanner:
        raise HTTPException(status_code=503, detail="GitHub Scanner not available")

    try:
        logger.info(f"Scanning organization: {request.org_name}")
        analysis = github_scanner.analyze_organization(request.org_name, request.limit)

        if not analysis:
            raise HTTPException(
                status_code=404, detail="Organization not found or scan failed"
            )

        return {
            "success": True,
            "organization": analysis.to_dict(),
            "watermark": WATERMARK,
        }

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Org scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/search-repos")
async def search_repositories(
    request: RepoSearchRequest, api_key: str = Depends(verify_api_key)
):
    """
    Search GitHub repositories

    Search across GitHub and analyze matching repositories.
    """
    if not SCANNER_AVAILABLE or not github_scanner:
        raise HTTPException(status_code=503, detail="GitHub Scanner not available")

    try:
        results = github_scanner.search_repos(request.query, request.limit)

        return {
            "success": True,
            "query": request.query,
            "total_results": len(results),
            "repositories": [r.to_dict() for r in results],
            "watermark": WATERMARK,
        }

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Repo search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# AI Code Generation (Groq LLM)
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/ai/generate-code")
async def ai_generate_code(
    request: CodeGenerationRequestV2, api_key: str = Depends(verify_api_key)
):
    """
    AI-powered code generation using Groq or NVIDIA NIM
    """
    if LLM_AVAILABLE and groq_client and groq_client.available:
        client = groq_client
        provider = "Groq"
    elif NIM_AVAILABLE:
        client = NimClient()
        client.available = client.api_key is not None
        provider = "NVIDIA NIM"
    else:
        raise HTTPException(
            status_code=503,
            detail="LLM not available - set GROQ_API_KEY or NIM_API_KEY environment variable",
        )

    try:
        result = await client.generate_code(
            prompt=request.prompt,
            language=request.language or "python",
            context=request.context,
        )

        return {
            "success": True,
            "result": {
                "code": result.code,
                "language": result.language,
                "explanation": result.explanation,
                "model": result.model,
            },
            "provider": provider,
            "watermark": WATERMARK,
        }

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"AI code generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ai/analyze-code")
async def ai_analyze_code(
    code: str, language: str = "python", api_key: str = Depends(verify_api_key)
):
    """
    AI-powered code analysis using Groq or NVIDIA NIM
    """
    if LLM_AVAILABLE and groq_client and groq_client.available:
        client = groq_client
        provider = "Groq"
    elif NIM_AVAILABLE:
        client = NimClient()
        client.available = client.api_key is not None
        provider = "NVIDIA NIM"
    else:
        raise HTTPException(
            status_code=503,
            detail="LLM not available - set GROQ_API_KEY or NIM_API_KEY environment variable",
        )

    try:
        analysis = await client.analyze_code(code, language)

        return {
            "success": True,
            "analysis": analysis,
            "provider": provider,
            "watermark": WATERMARK,
        }

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"AI code analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ollama/query")
async def query_ollama_endpoint(request: OllamaQueryRequest, req: Request = None):
    """
    Query Ollama models with intelligent routing

    Automatically routes queries to appropriate models (coding vs wisdom).
    Falls back gracefully if models are unavailable.
    """
    user_query = request.query
    if not user_query:
        raise HTTPException(400, "Query required")

    model_config = route_query(user_query)
    model_name = model_config["model"]

    print(f"🎯 Routing to {model_name}")

    start_time = time.time()
    response = query_ollama(model_name, user_query)
    response_time = time.time() - start_time

    log_to_supabase(model_name, user_query, response, int(response_time * 1000), req)

    return {
        "query": user_query,
        "model": model_name,
        "personality": model_config.get("personality", "AI Assistant"),
        "response": response,
        "response_time": round(response_time, 2),
        "watermark": WATERMARK,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Startup & Shutdown
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    module_path = "src.main:app"

    uvicorn.run(module_path, host="0.0.0.0", port=8000, reload=False, log_level="info")
