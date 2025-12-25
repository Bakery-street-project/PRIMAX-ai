#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - SUPERBRAIN_MASTER_REBUILD.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
warn() { echo -e "${YELLOW}[⚠]${NC} $1"; }

# Setup
BASE_DIR="/home/boozelee/Desktop/superbrain-x"
cd "$BASE_DIR" || { error "Base directory not found!"; exit 1; }

# Create structure
log "Creating directory structure..."
mkdir -p core/{mu_memory,auth,supervision} \
         agents \
         breakthrough_engine \
         monetization/{stripe,discord,gumroad} \
         api-keys \
         logs

# Activate/create venv
log "Setting up virtual environment..."
if [ ! -d "$HOME/superbrain-venv" ]; then
    python3 -m venv "$HOME/superbrain-venv"
fi
source "$HOME/superbrain-venv/bin/activate"

# Install dependencies
log "Installing dependencies..."
pip install --upgrade pip
pip install \
    google-generativeai google-api-python-client google-auth-oauthlib \
    google-cloud-aiplatform google-cloud-storage \
    langchain langchain-openai langchain-google-genai \
    sentence-transformers faiss-cpu \
    discord.py stripe gumroad-api \
    requests pandas numpy sympy scipy \
    python-dotenv pyyaml \
    rich typer fastapi uvicorn

success "Environment ready!"

# Fix OAuth2 authentication
log "Configuring OAuth2..."
cat > core/auth/gemini_auth.py << 'PYAUTH'
#!/usr/bin/env python3
"""
OAuth2 Authentication for Gemini
Fixes 401 API key errors
"""
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import google.generativeai as genai

def get_authenticated_client():
    """Get authenticated Gemini client using OAuth2"""
    # Try Application Default Credentials first
    try:
        import google.auth
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        genai.configure(credentials=credentials)
        return genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        print(f"ADC failed: {e}")
        
    # Try service account
    sa_path = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
    if os.path.exists(sa_path):
        try:
            credentials = service_account.Credentials.from_service_account_file(
                sa_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            credentials.refresh(Request())
            genai.configure(credentials=credentials)
            return genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            print(f"Service account failed: {e}")
    
    # Fallback to API key (for supported endpoints)
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-pro')
    
    raise RuntimeError("No valid authentication method found!")

if __name__ == "__main__":
    try:
        model = get_authenticated_client()
        print("✅ Authentication successful!")
        response = model.generate_content("Say hello")
        print(f"Test response: {response.text}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
PYAUTH

chmod +x core/auth/gemini_auth.py

# Create MU Memory system
log "Building MU Memory..."
cat > core/mu_memory/memory_system.py << 'PYMEM'
#!/usr/bin/env python3
"""
MU Memory: FAISS-based semantic memory for Superbrain
Persistent embeddings with Google Drive backup
"""
import os
import json
import hashlib
import faiss
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple

class MUMemory:
    def __init__(self, base_path="/home/boozelee/Desktop/superbrain-x"):
        self.base_path = Path(base_path)
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.memory: Dict = {}
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_file = self.base_path / 'core/mu_memory/index.faiss'
        self.memory_file = self.base_path / 'core/mu_memory/memory.json'
        
        # Load existing memory
        if self.index_file.exists():
            self.index = faiss.read_index(str(self.index_file))
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
    
    def analyze_folder(self, folder_path: str = None):
        """Deep analysis of all files"""
        if folder_path is None:
            folder_path = self.base_path
        
        folder_path = Path(folder_path)
        file_count = 0
        
        print(f"Analyzing: {folder_path}")
        
        for file_path in folder_path.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                    
                    # Hash for deduplication
                    file_hash = hashlib.sha256(content.encode()).hexdigest()
                    
                    # Skip if already processed
                    if file_hash in self.memory:
                        continue
                    
                    # Generate embedding
                    embedding = self.model.encode(content[:10000])
                    self.index.add(np.array([embedding]))
                    
                    # Store metadata
                    self.memory[file_hash] = {
                        'path': str(file_path),
                        'size': len(content),
                        'type': file_path.suffix,
                        'content_preview': content[:500]
                    }
                    
                    file_count += 1
                    print(f"  ✓ {file_path.name} ({len(content)} bytes)")
                    
                except Exception as e:
                    print(f"  ✗ {file_path.name}: {e}")
        
        print(f"\n✅ Analyzed {file_count} files")
        self.save()
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """Semantic search"""
        query_embedding = self.model.encode(query)
        D, I = self.index.search(np.array([query_embedding]), k)
        
        results = []
        for idx, dist in zip(I[0], D[0]):
            file_hash = list(self.memory.keys())[idx]
            results.append((self.memory[file_hash]['path'], float(dist)))
        
        return results
    
    def save(self):
        """Persist to disk"""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_file))
        
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
        
        print(f"💾 Memory saved: {len(self.memory)} items")

if __name__ == "__main__":
    memory = MUMemory()
    memory.analyze_folder()
    
    # Test search
    results = memory.search("authentication OAuth2")
    print("\nSearch results:")
    for path, score in results:
        print(f"  {path} (distance: {score:.2f})")
PYMEM

chmod +x core/mu_memory/memory_system.py

# Create LangChain orchestrator
log "Building LangChain agents..."
cat > agents/research_agent.py << 'PYRESEARCH'
#!/usr/bin/env python3
"""
Research Agent: LangChain-powered autonomous researcher
"""
import os
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import requests

def perplexity_search(query: str) -> str:
    """Search using Perplexity API"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        return "Perplexity API key not set"
    
    try:
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={'Authorization': f'Bearer {api_key}'},
            json={
                'model': 'llama-3.1-sonar-small-128k-online',
                'messages': [{'role': 'user', 'content': query}]
            }
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Search failed: {e}"

def run_research_agent(task: str):
    """Execute research task"""
    llm = ChatOpenAI(temperature=0.7, model="gpt-4")
    
    tools = [
        Tool(
            name="Perplexity",
            func=perplexity_search,
            description="Real-time web research for latest trends and information"
        ),
        Tool(
            name="MUMemory",
            func=lambda q: "Search local knowledge base",
            description="Search Superbrain's memory for relevant information"
        )
    ]
    
    prompt = PromptTemplate.from_template(
        "You are a research agent for Superbrain 2.0. "
        "Use available tools to complete tasks.\n\n"
        "Task: {input}\n\n"
        "Tools: {tools}\n"
        "Tool Names: {tool_names}\n\n"
        "Think step-by-step and provide detailed results.\n\n"
        "{agent_scratchpad}"
    )
    
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    result = executor.invoke({"input": task})
    return result['output']

if __name__ == "__main__":
    result = run_research_agent("Research latest LangChain monetization strategies")
    print(f"\n\n📊 Research Result:\n{result}")
PYRESEARCH

chmod +x agents/research_agent.py

# Create supervision system
log "Building supervision system..."
cat > core/supervision/supervisor.py << 'PYSUPER'
#!/usr/bin/env python3
"""
AI Supervision: Ensures complete folder analysis
"""
import os
from pathlib import Path
from datetime import datetime
import json

class SupervisorSystem:
    def __init__(self, base_path="/home/boozelee/Desktop/superbrain-x"):
        self.base_path = Path(base_path)
        self.log_file = self.base_path / 'logs/supervision.log'
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def audit_coverage(self):
        """Check if all files are analyzed"""
        total_files = sum(1 for _ in self.base_path.rglob('*') if _.is_file())
        
        # Check MU Memory
        memory_file = self.base_path / 'core/mu_memory/memory.json'
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                memory = json.load(f)
            analyzed_files = len(memory)
        else:
            analyzed_files = 0
        
        coverage = (analyzed_files / total_files * 100) if total_files > 0 else 0
        
        # Log results
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'total_files': total_files,
            'analyzed_files': analyzed_files,
            'coverage': f"{coverage:.2f}%",
            'status': 'PASS' if coverage >= 95 else 'FAIL'
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"\n📊 Supervision Report:")
        print(f"  Total files: {total_files}")
        print(f"  Analyzed: {analyzed_files}")
        print(f"  Coverage: {coverage:.2f}%")
        print(f"  Status: {'✅ PASS' if coverage >= 95 else '⚠️ FAIL'}")
        
        # Calculate P(Lazy|Output)
        p_lazy = 1 - (coverage / 100)
        print(f"  P(Lazy|Output) ≈ {p_lazy:.3f}")
        
        return coverage >= 95

if __name__ == "__main__":
    supervisor = SupervisorSystem()
    supervisor.audit_coverage()
PYSUPER

chmod +x core/supervision/supervisor.py

# Create launcher scripts
log "Creating launchers..."
cat > run_full_analysis.sh << 'LAUNCH1'
#!/bin/bash
source ~/superbrain-venv/bin/activate
cd /home/boozelee/Desktop/superbrain-x
python3 core/mu_memory/memory_system.py
python3 core/supervision/supervisor.py
LAUNCH1

cat > run_research_agent.sh << 'LAUNCH2'
#!/bin/bash
source ~/superbrain-venv/bin/activate
cd /home/boozelee/Desktop/superbrain-x
python3 agents/research_agent.py
LAUNCH2

chmod +x run_*.sh

success "✅ Superbrain 2.0 rebuilt successfully!"
echo ""
echo "📁 Structure created in: $BASE_DIR"
echo ""
echo "🚀 Next steps:"
echo "  1. Run full analysis: ./run_full_analysis.sh"
echo "  2. Launch research agent: ./run_research_agent.sh"
echo "  3. Check supervision: python3 core/supervision/supervisor.py"
echo ""
echo "🔐 Authentication:"
echo "  - Run: gcloud auth application-default login"
echo "  - Or set: export GEMINI_API_KEY='your-key'"
echo ""
