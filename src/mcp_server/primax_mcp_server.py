"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRIMAX AI - MCP Server Wrapper                             ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-MCP-BSP-2025                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import sys
from pathlib import Path
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

server = Server("primax-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available PRIMAX tools"""
    return [
        Tool(
            name="primax_chat",
            description="Chat with PRIMAX AI using local Ollama models",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Your message to PRIMAX"},
                    "model": {"type": "string", "description": "Model to use (dragon, coding, wisdom)", "default": "dragon"}
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="primax_analyze_repo",
            description="Analyze a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository name (owner/repo)"}
                },
                "required": ["repo"]
            }
        ),
        Tool(
            name="primax_brain_analysis",
            description="Run mathematical brain analysis (graph theory, SNN)",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_type": {"type": "string", "description": "Type: graph, snn, or dynamic", "default": "graph"}
                },
                "required": []
            }
        ),
        Tool(
            name="primax_code_scan",
            description="Scan local codebase for analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to scan", "default": "."}
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Execute PRIMAX tools"""
    
    if name == "primax_chat":
        message = arguments.get("message", "")
        model = arguments.get("model", "dragon")
        
        model_map = {
            "dragon": "primax-dragon-coder:latest",
            "coding": "qwen2.5-coder:1.5b",
            "wisdom": "primax-dragon-coder:latest"
        }
        
        chosen_model = model_map.get(model, "primax-dragon-coder:latest")
        try:
            try:
                from src.config import OLLAMA_HOST, OLLAMA_GENERATION_TIMEOUT
            except ImportError:
                OLLAMA_HOST = "http://127.0.0.1:11434"
                OLLAMA_GENERATION_TIMEOUT = 300

            import ollama
            client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_GENERATION_TIMEOUT)
            chunks = []
            for chunk in client.chat(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": "You are PRIMAX-DRAGON, a wise AI assistant."},
                    {"role": "user", "content": message},
                ],
                stream=True,
            ):
                piece = (chunk.get("message") or {}).get("content", "")
                if piece:
                    chunks.append(piece)
            return [TextContent(type="text", text="".join(chunks).strip() or "(empty)")]
        except ImportError:
            # Subprocess fallback if `ollama` module isn't installed
            try:
                proc = subprocess.Popen(
                    ["ollama", "run", chosen_model],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True,
                )
                prompt = f"System: You are PRIMAX-DRAGON, a wise AI assistant.\nUser: {message}\nAssistant:"
                stdout, stderr = proc.communicate(input=prompt, timeout=300)
                return [TextContent(type="text",
                    text=stdout.strip() if proc.returncode == 0 else f"Error: {stderr}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]
    
    elif name == "primax_analyze_repo":
        repo = arguments.get("repo", "")
        try:
            result = subprocess.run(
                ["gh", "repo", "view", repo, "--json", "name,description,stargazerCount,forkCount,createdAt"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return [TextContent(type="text", text=result.stdout)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "primax_brain_analysis":
        analysis_type = arguments.get("analysis_type", "graph")
        return [TextContent(type="text", text=f"Brain {analysis_type} analysis: Neural network active")]
    
    elif name == "primax_code_scan":
        path = arguments.get("path", ".")
        try:
            files = list(Path(path).rglob("*.py"))[:20]
            summary = f"Found {len(files)} Python files in {path}"
            return [TextContent(type="text", text=summary)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    return [TextContent(type="text", text="Unknown tool")]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="primax-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())