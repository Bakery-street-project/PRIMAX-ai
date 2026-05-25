"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRIMAX AI - TUI Application                                ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-TUI-BSP-2025                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Button, Log, TabbedContent
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from rich.text import Text
from rich.panel import Panel
import asyncio
import subprocess
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class ChatMessage(Static):
    def __init__(self, sender: str, message: str, **kwargs):
        super().__init__(**kwargs)
        self.sender = sender
        self.message = message

class PRIMAXApp(App):
    CSS_PATH = "primax_tui.css"
    TITLE = "PRIMAX AI - Neuromorphic Intelligence"
    SUB_TITLE = "WATERMARK: PRIMAX-AI-TUI-BSP-2025"
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="chat-container"):
            yield Log(id="chat-log")
        with Horizontal(id="input-row"):
            yield Input(placeholder="Type your message...", id="message-input")
            yield Button("Send", id="send-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        self.log_message("System", "Welcome to PRIMAX AI TUI")
        self.log_message("System", "WATERMARK: PRIMAX-AI-TUI-BSP-2025")
        self.log_message("System", "Type 'help' for available commands")
        self.log_message("System", "Models: Dragon (wisdom), Coding (qwen2.5-coder)")
        self.log_message("System", "MCP: Available | Nexus: Available")
    
    def log_message(self, sender: str, message: str) -> None:
        try:
            log = self.query_one("#chat-log", Log)
            log.write_line(f"[{sender}] {message}")
        except Exception:
            print(f"[{sender}] {message}")  # Fallback to console
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-btn":
            self.send_message()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.send_message()
    
    def send_message(self) -> None:
        input_widget = self.query_one("#message-input", Input)
        message = input_widget.value.strip()
        input_widget.value = ""
        
        if not message:
            return
        
        self.log_message("You", message)
        
        if message.lower() in ["help", "?"]:
            self.show_help()
            return
        
        self.process_query(message)
    
    def show_help(self) -> None:
        help_text = """
PRIMAX AI TUI - WATERMARK: PRIMAX-AI-TUI-BSP-2025

Commands:
  /dragon <query>   - Ask Dragon (wisdom/creativity)
  /code <query>     - Ask Coding model
  /repo <owner/repo> - Analyze GitHub repo
  /brain            - Show brain status
  /mcp              - Test MCP integration
  /nexus <task>     - Run Nexus agent task
  /scan <path>      - Scan local codebase
  /clear            - Clear chat
  help/?            - Show this help

MCP Tools: GitHub, Filesystem, PRIMAX
Nexus: Multi-agent orchestration
"""
        self.log_message("System", help_text)
    
    def process_query(self, message: str) -> None:
        if message.startswith("/dragon "):
            query = message[8:].strip()
            self.query_dragon(query)
        elif message.startswith("/code "):
            query = message[6:].strip()
            self.query_coding(query)
        elif message.startswith("/repo "):
            repo = message[6:].strip()
            self.analyze_repo(repo)
        elif message.startswith("/scan "):
            path = message[6:].strip()
            self.scan_codebase(path)
        elif message.startswith("/mcp"):
            self.test_mcp()
        elif message.startswith("/nexus "):
            task = message[7:].strip()
            self.run_nexus(task)
        elif message == "/brain":
            self.show_brain_status()
        elif message == "/clear":
            self.clear_chat()
        else:
            self.query_default(message)
    
    def test_mcp(self) -> None:
        self.log_message("MCP", "Testing MCP integration...")
        try:
            result = subprocess.run(
                ["python", "-m", "src.mcp_server.primax_mcp_server"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd="/home/kilisan/primax-ai"
            )
            self.log_message("MCP", f"Server ready: {result.returncode == 0}")
        except Exception as e:
            self.log_message("MCP", f"Error: {str(e)}")
    
    def run_nexus(self, task: str) -> None:
        self.log_message("Nexus", f"Running task: {task}")
        try:
            import asyncio
            from src.nexus_adapter import create_primax_agents
            
            async def run_agent():
                adapter = create_primax_agents()
                result = await adapter.dispatch_task("wisdom-brain", task)
                return result.get("result", str(result))
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(run_agent())
            self.log_message("Nexus", result[:500])
        except Exception as e:
            self.log_message("Nexus", f"Error: {str(e)}")
    
    def query_dragon(self, query: str) -> None:
        self.log_message("Dragon", f"Analyzing: {query}")
        self.run_ollama_query("primax-dragon-coder:latest", query)
    
    def query_coding(self, query: str) -> None:
        self.log_message("Coding", f"Solving: {query}")
        self.run_ollama_query("qwen2.5-coder:1.5b", query)
    
    def query_default(self, query: str) -> None:
        self.log_message("PRIMAX", f"Processing: {query}")
        self.run_ollama_query("primax-dragon-coder:latest", query)
    
    def run_ollama_query(self, model: str, prompt: str) -> None:
        """Stream tokens from Ollama HTTP API; updates the chat log incrementally."""
        try:
            from src.config import OLLAMA_HOST, OLLAMA_GENERATION_TIMEOUT
        except ImportError:
            try:
                from config import OLLAMA_HOST, OLLAMA_GENERATION_TIMEOUT
            except ImportError:
                OLLAMA_HOST = "http://127.0.0.1:11434"
                OLLAMA_GENERATION_TIMEOUT = 300

        try:
            import ollama
            client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_GENERATION_TIMEOUT)
            self.log_message(model, "(streaming…)")
            chunks = []
            for chunk in client.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "You are PRIMAX-DRAGON, a wise AI assistant."},
                    {"role": "user", "content": prompt},
                ],
                stream=True,
            ):
                piece = (chunk.get("message") or {}).get("content", "")
                if piece:
                    chunks.append(piece)
            self.log_message("PRIMAX", "".join(chunks).strip() or "(empty response)")
        except ImportError:
            # Fallback to old subprocess if ollama package unavailable
            try:
                proc = subprocess.Popen(
                    ["ollama", "run", model],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True,
                )
                full_prompt = f"System: You are PRIMAX-DRAGON, a wise AI assistant.\nUser: {prompt}\nAssistant:"
                stdout, stderr = proc.communicate(input=full_prompt, timeout=OLLAMA_GENERATION_TIMEOUT)
                self.log_message("PRIMAX", stdout.strip() if proc.returncode == 0 else f"Error: {stderr}")
            except subprocess.TimeoutExpired:
                self.log_message("PRIMAX", f"Error: Query timeout after {OLLAMA_GENERATION_TIMEOUT}s")
        except Exception as e:
            self.log_message("PRIMAX", f"Error: {type(e).__name__}: {e}")
    
    def analyze_repo(self, repo: str) -> None:
        self.log_message("Scanner", f"Analyzing repository: {repo}")
        try:
            result = subprocess.run(
                ["gh", "repo", "view", repo, "--json", "name,description,stargazerCount,forkCount"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                info = f"""
Repository: {data.get('name', 'N/A')}
Description: {data.get('description', 'N/A')}
Stars: {data.get('stargazerCount', 0)}
Forks: {data.get('forkCount', 0)}
"""
                self.log_message("Scanner", info)
            else:
                self.log_message("Scanner", f"Error: {result.stderr}")
        except Exception as e:
            self.log_message("Scanner", f"Error: {str(e)}")
    
    def scan_codebase(self, path: str) -> None:
        self.log_message("Scanner", f"Scanning codebase: {path}")
        try:
            from src.codebase_scanner import scan_repository
            result = scan_repository(path)
            info = f"""
Codebase Analysis:
  Files: {len(result.files)}
  Lines: {result.total_lines}
  Functions: {result.total_functions}
  Classes: {result.total_classes}
  Languages: {dict(result.languages)}
"""
            self.log_message("Scanner", info)
        except Exception as e:
            self.log_message("Scanner", f"Error: {str(e)}")
    
    def show_brain_status(self) -> None:
        self.log_message("Brain", "Neuromorphic Core Status:")
        self.log_message("Brain", "  - Graph Theory: Active")
        self.log_message("Brain", "  - SNN Engine: Active")
        self.log_message("Brain", "  - Dynamic Systems: Active")
        self.log_message("Brain", "  - Models: Dragon, Coding")
    
    def clear_chat(self) -> None:
        log = self.query_one("#chat-log", Log)
        log.clear()
        self.on_mount()

if __name__ == "__main__":
    app = PRIMAXApp()
    app.run()
