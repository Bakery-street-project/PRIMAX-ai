"""
WATERMARK: PRIMAX-AI-CONFIG-BSP-2025
Architecture: Centralized config — env-var driven, single source of truth
License: Proprietary - Bakery Street Project

Single place to read environment-based runtime configuration so timeouts,
hosts, and model defaults are consistent across main.py, mcp_server, tui.
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Any, Dict

_REPO_ROOT = Path(__file__).resolve().parent.parent
_ROUTER_FILE = _REPO_ROOT / "model_router.json"


def _load_router() -> Dict[str, Any]:
    if _ROUTER_FILE.exists():
        try:
            return json.loads(_ROUTER_FILE.read_text())
        except Exception:
            pass
    return {}


_ROUTER = _load_router()


# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

# Long enough for 14GB models on CPU. Override via env when needed.
OLLAMA_GENERATION_TIMEOUT = int(os.getenv(
    "OLLAMA_GENERATION_TIMEOUT",
    str(_ROUTER.get("load_balancing", {}).get("timeout_seconds", 300)),
))

# Quick health-check timeout (don't wait long for daemon-down).
OLLAMA_HEALTH_TIMEOUT = int(os.getenv("OLLAMA_HEALTH_TIMEOUT", "5"))

DEFAULT_DRAGON_MODEL = _ROUTER.get("models", {}).get("dragon_wise", {}).get(
    "model", "primax-dragon-coder:latest"
)
DEFAULT_OPTIMUS_MODEL = _ROUTER.get("models", {}).get("optimus_prime", {}).get(
    "model", "optimus-prime-local:latest"
)


def model_for(intent: str) -> str:
    """Resolve a routing intent (coding/wisdom/creative/default) to a model name."""
    rules = _ROUTER.get("routing_rules", {})
    key = rules.get(intent, rules.get("default", "dragon_wise"))
    return _ROUTER.get("models", {}).get(key, {}).get("model", DEFAULT_DRAGON_MODEL)


def fallback_for(model: str) -> str:
    """Find the configured fallback for a model identifier."""
    for entry in _ROUTER.get("models", {}).values():
        if entry.get("model") == model:
            return entry.get("fallback", DEFAULT_DRAGON_MODEL)
    return DEFAULT_DRAGON_MODEL


# ── GitHub CLI ────────────────────────────────────────────────────────────────
GH_AUTH_TIMEOUT = int(os.getenv("GH_AUTH_TIMEOUT", "5"))
GH_COMMAND_TIMEOUT = int(os.getenv("GH_COMMAND_TIMEOUT", "30"))
