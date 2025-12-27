# PRIMAX AI - Terminal UI

## ⌨️ Claude Code-Style Terminal Interface

### Features
- Terminal chat with PRIMAX
- Repository browser
- Code generation
- Keyboard shortcuts
- Fast and lightweight

### Quick Start

```bash
cd tui

# Install dependencies
pip install rich textual httpx

# Run TUI
python primax_tui.py
```

### Create TUI (primax_tui.py)

```python
from textual.app import App
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Static
import httpx

API_URL = "https://primax-ai.onrender.com/api/v1"

class PrimaxTUI(App):
    """PRIMAX AI Terminal Interface"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    """
    
    def compose(self):
        yield Header()
        yield Container(
            Static("PRIMAX AI - Chat", id="messages"),
            Input(placeholder="Message PRIMAX...", id="input")
        )
        yield Footer()
    
    async def on_input_submitted(self, event):
        # Send to PRIMAX API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/chat",
                json={"message": event.value}
            )
            data = response.json()
            # Display response
            self.query_one("#messages").update(data["response"])

if __name__ == "__main__":
    app = PrimaxTUI()
    app.run()
```

### Keyboard Shortcuts
- `Ctrl+C` - Quit
- `Enter` - Send message
- `↑/↓` - Navigate history
- `/help` - Show commands

---

**Watermark:** PRIMAX-AI-BSP-2025
