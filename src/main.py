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
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import sys
import os
from pathlib import Path
from datetime import datetime
import logging
import hashlib
import secrets
from collections import defaultdict
import time

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
        agent_recommendation
    )
    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False
    logger.warning("AutomationCodex Brain not available - running in lite mode")

# ═══════════════════════════════════════════════════════════════════════════════
# Constants & Configuration
# ═══════════════════════════════════════════════════════════════════════════════

WATERMARK = "PRIMAX-AI-BSP-2025"
VERSION = "1.0.0"
COPYRIGHT = "Copyright © 2024-2025 Bakery Street Project"

# Security Configuration - PROTOCOL V2
# Load from Blackout Vault
vault_path = os.path.expanduser("~/my-app-vault/secrets/.env")
if os.path.exists(vault_path):
    from dotenv import load_dotenv
    load_dotenv(vault_path)
    API_KEY = os.getenv("PRIMAX_API_KEY")
    if not API_KEY:
        raise ValueError("CRITICAL: Vault found but PRIMAX_API_KEY missing")
    logger.info("✅ SECURE: Rotated key loaded from Blackout Vault")
else:
    raise FileNotFoundError(f"CRITICAL: Blackout Vault not found at {vault_path}")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Rate limiting
rate_limit_store = defaultdict(list)
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

# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="PRIMAX AI",
    description="Autonomous DevOps Agent on Decentralized Cloud",
    version=VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware - RESTRICTED
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://primax-neuromorphic.fly.dev"],  # Only self
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

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
        req_time for req_time in rate_limit_store[client_ip]
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
        "docs": "/api/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=VERSION,
        watermark=WATERMARK,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/v1/watermark")
async def get_watermark():
    """Get watermark information"""
    return {
        "watermark": WATERMARK,
        "version": VERSION,
        "copyright": COPYRIGHT,
        "license": "Proprietary - See LICENSE_PROPRIETARY.md"
    }

@app.post("/api/v1/automate", response_model=AutomationResponse)
async def run_automation(request: AutomationRequest, api_key: str = Depends(verify_api_key)):
    """
    Run automation task using Dream Script Engine

    This endpoint integrates with Smoothoperator's Dream Script Engine
    """
    try:
        # Try to import Dream Script Engine
        try:
            from dream_script_engine import DreamScriptEngineSingularity

            # Initialize engine
            engine = DreamScriptEngineSingularity()

            # Process task (simplified for MVP)
            result = {
                "processed": True,
                "task": request.task,
                "mode": request.mode,
                "parameters": request.parameters
            }

            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            return AutomationResponse(
                success=True,
                task_id=task_id,
                result=result,
                message="Automation task queued successfully"
            )

        except ImportError:
            # Fallback if Smoothoperator not available
            logger.warning("Dream Script Engine not available, using fallback")
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            return AutomationResponse(
                success=True,
                task_id=task_id,
                result={"simulated": True},
                message="Automation simulated (Dream Engine not loaded)"
            )

    except Exception as e:
        logger.error(f"Automation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest, api_key: str = Depends(verify_api_key)):
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
            code=full_code,
            language=request.language,
            license_header=license_header
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
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/brain/analyze-resilience")
async def analyze_system_resilience(adjacency_matrix: List[List[int]], api_key: str = Depends(verify_api_key)):
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
            "watermark": WATERMARK
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/brain/neural-activity")
async def get_neural_activity(size: int = 20, tmax: int = 100, api_key: str = Depends(verify_api_key)):
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
            "watermark": WATERMARK
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
            "watermark": WATERMARK
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# Startup & Shutdown
# ═══════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info(f"🚀 PRIMAX AI v{VERSION} starting...")
    logger.info(f"   Watermark: {WATERMARK}")
    logger.info(f"   {COPYRIGHT}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("🛑 PRIMAX AI shutting down...")

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
