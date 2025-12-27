# PRIMAX DEPLOYMENT - Supabase Integration

**Database Infrastructure Manifold**
**Platform:** Termux Android ARM64 + Supabase Cloud
**Constraints:** 4GB RAM, batch <1000 vectors, async ops only

---

## ARCHITECTURE OVERVIEW

```
PRIMAX Core
    ├── Supabase Postgres (pgvector)
    │   ├── embeddings table (1536-dim vectors)
    │   ├── user_queries table (history)
    │   └── api_logs table (monitoring)
    ├── Local Vault (GPG-encrypted)
    │   ├── API keys (Anthropic, Groq, Supabase)
    │   └── Secrets rotation
    └── FastAPI Endpoints
        ├── /v1/embed (async batch processing)
        ├── /v1/search (vector similarity)
        └── /v1/analyze (LLM integration)
```

---

## CONSTRAINTS & SOLUTIONS

### Android RAM Limits
- **Problem:** 4GB RAM, pgvector ops memory-intensive
- **Solution:** Batch embeddings in chunks of 500, use async/await
- **Implementation:** `asyncpg` client with connection pooling

### Termux Network
- **Problem:** Direct internet routing issues
- **Solution:** Use Supabase hosted service (bypass local network)
- **Alternative:** proot-distro Ubuntu for micromamba if needed

### Vector Dimensions
- **Standard:** OpenAI embeddings = 1536 dimensions
- **Alternative:** all-MiniLM-L6-v2 = 384 dimensions (lighter)
- **Choice:** Use MiniLM for RAM efficiency

---

## SUPABASE SETUP

### 1. Create Supabase Project

Go to https://supabase.com/dashboard

**Free tier limits:**
- Database: 500 MB
- Storage: 1 GB
- Bandwidth: 2 GB/month
- **Sufficient for initial deployment**

### 2. Enable pgvector Extension

In Supabase SQL Editor:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embeddings table
CREATE TABLE embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(384), -- MiniLM dimensions
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for similarity search
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create user queries table
CREATE TABLE user_queries (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT,
    query TEXT NOT NULL,
    results JSONB,
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create API logs table
CREATE TABLE api_logs (
    id BIGSERIAL PRIMARY KEY,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER,
    request_data JSONB,
    response_data JSONB,
    ip_address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_queries_user ON user_queries(user_id);
CREATE INDEX idx_queries_created ON user_queries(created_at DESC);
CREATE INDEX idx_logs_endpoint ON api_logs(endpoint);
CREATE INDEX idx_logs_created ON api_logs(created_at DESC);

-- Row Level Security (RLS)
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_logs ENABLE ROW LEVEL SECURITY;

-- Policies (allow service role full access)
CREATE POLICY "Service role full access" ON embeddings
    FOR ALL USING (true);

CREATE POLICY "Service role full access" ON user_queries
    FOR ALL USING (true);

CREATE POLICY "Service role full access" ON api_logs
    FOR ALL USING (true);
```

### 3. Get Credentials

From Supabase Dashboard → Settings → API:

- **Project URL:** `https://your-project.supabase.co`
- **Anon Key:** `eyJhbG...` (public, for client apps)
- **Service Role Key:** `eyJhbG...` (secret, for server)

---

## VAULT INTEGRATION

### Store Credentials in GPG Vault

```bash
cd ~/claude_enterprise/workspace/PRIMAX-ai

# Create secrets file
cat > .secrets << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbG...your-service-role-key
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
EOF

# Encrypt with vault manager
python src/vault_manager.py store-file --file=.secrets

# Remove plaintext
shred -u .secrets

# Retrieve when needed
python src/vault_manager.py get --key=SUPABASE_URL
```

### Vault Manager Enhancement

Add to `src/vault_manager.py`:

```python
def get_all_env():
    """Load all secrets as environment variables"""
    import os
    secrets = {
        'SUPABASE_URL': get_secret('SUPABASE_URL'),
        'SUPABASE_SERVICE_KEY': get_secret('SUPABASE_SERVICE_KEY'),
        'ANTHROPIC_API_KEY': get_secret('ANTHROPIC_API_KEY'),
        'GROQ_API_KEY': get_secret('GROQ_API_KEY'),
    }
    for key, value in secrets.items():
        if value:
            os.environ[key] = value
    return secrets
```

---

## ASYNC DATABASE CLIENT

Create `src/db/supabase_client.py`:

```python
"""
Async Supabase client with pgvector support
Constraints: Batch size <1000, connection pooling for 4GB RAM
"""
import asyncio
import asyncpg
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import os
from functools import lru_cache

# Embedding model (cached in RAM)
@lru_cache(maxsize=1)
def get_model():
    """Load embedding model once"""
    return SentenceTransformer('all-MiniLM-L6-v2')

class SupabaseVectorClient:
    """Async client for Supabase with pgvector"""

    def __init__(self, url: str, service_key: str):
        self.url = url
        self.service_key = service_key
        self.pool: Optional[asyncpg.Pool] = None

        # Extract connection params from Supabase URL
        # Format: https://project-id.supabase.co
        project_id = url.replace('https://', '').replace('.supabase.co', '')
        self.db_url = f"postgresql://postgres:{service_key}@db.{project_id}.supabase.co:5432/postgres"

    async def connect(self):
        """Create connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=1,
                max_size=3,  # Low for RAM constraints
                command_timeout=60,
            )
            print("✅ Connected to Supabase")

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            print("✅ Disconnected from Supabase")

    async def embed_text(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings (batch <1000)"""
        if len(texts) > 1000:
            raise ValueError(f"Batch too large: {len(texts)} > 1000")

        model = get_model()
        embeddings = model.encode(texts, show_progress_bar=False)
        return embeddings

    async def insert_embeddings(
        self,
        texts: List[str],
        metadata: Optional[List[Dict]] = None,
        batch_size: int = 500
    ) -> int:
        """Insert embeddings in batches"""
        if not self.pool:
            await self.connect()

        total_inserted = 0

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size] if metadata else [{}] * len(batch_texts)

            # Generate embeddings
            embeddings = await self.embed_text(batch_texts)

            # Insert batch
            async with self.pool.acquire() as conn:
                for text, embedding, meta in zip(batch_texts, embeddings, batch_metadata):
                    await conn.execute(
                        """
                        INSERT INTO embeddings (content, embedding, metadata)
                        VALUES ($1, $2, $3)
                        """,
                        text,
                        embedding.tolist(),
                        meta
                    )
                    total_inserted += 1

            print(f"  Inserted batch {i//batch_size + 1}: {len(batch_texts)} embeddings")

        return total_inserted

    async def search_similar(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Vector similarity search"""
        if not self.pool:
            await self.connect()

        # Embed query
        query_embedding = await self.embed_text([query])
        query_vector = query_embedding[0].tolist()

        # Search
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    id,
                    content,
                    metadata,
                    1 - (embedding <=> $1::vector) AS similarity
                FROM embeddings
                WHERE 1 - (embedding <=> $1::vector) > $2
                ORDER BY embedding <=> $1::vector
                LIMIT $3
                """,
                query_vector,
                threshold,
                limit
            )

        results = [
            {
                'id': row['id'],
                'content': row['content'],
                'metadata': row['metadata'],
                'similarity': float(row['similarity'])
            }
            for row in rows
        ]

        return results

    async def log_query(
        self,
        user_id: str,
        query: str,
        results: List[Dict],
        response_time_ms: int
    ):
        """Log user query"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_queries (user_id, query, results, response_time_ms)
                VALUES ($1, $2, $3, $4)
                """,
                user_id,
                query,
                results,
                response_time_ms
            )

    async def log_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        request_data: Dict,
        response_data: Dict,
        ip_address: str
    ):
        """Log API call"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO api_logs (endpoint, method, status_code, request_data, response_data, ip_address)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                endpoint,
                method,
                status_code,
                request_data,
                response_data,
                ip_address
            )

# Global client instance
_client: Optional[SupabaseVectorClient] = None

def get_client() -> SupabaseVectorClient:
    """Get or create client"""
    global _client
    if _client is None:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY required")
        _client = SupabaseVectorClient(url, key)
    return _client
```

---

## FASTAPI INTEGRATION

Update `src/main.py`:

```python
"""
PRIMAX FastAPI with Supabase pgvector backend
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import os

from db.supabase_client import get_client

app = FastAPI(
    title="PRIMAX AI",
    description="Self-learning automation engine with vector search",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class EmbedRequest(BaseModel):
    texts: List[str]
    metadata: Optional[List[Dict]] = None

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    threshold: float = 0.7

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query_time_ms: int

# Startup
@app.on_event("startup")
async def startup():
    """Initialize Supabase client"""
    # Load secrets from vault
    from vault_manager import get_all_env
    get_all_env()

    # Connect to Supabase
    client = get_client()
    await client.connect()
    print("🚀 PRIMAX started with Supabase backend")

@app.on_event("shutdown")
async def shutdown():
    """Close connections"""
    client = get_client()
    await client.close()

# Endpoints
@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "backend": "supabase"}

@app.post("/v1/embed")
async def embed_texts(req: EmbedRequest, request: Request):
    """Embed and store texts"""
    if len(req.texts) > 1000:
        raise HTTPException(400, "Batch too large (max 1000)")

    client = get_client()

    try:
        start = time.time()
        count = await client.insert_embeddings(req.texts, req.metadata)
        elapsed_ms = int((time.time() - start) * 1000)

        # Log API call
        await client.log_api_call(
            endpoint="/v1/embed",
            method="POST",
            status_code=200,
            request_data={"count": len(req.texts)},
            response_data={"inserted": count},
            ip_address=request.client.host
        )

        return {
            "inserted": count,
            "time_ms": elapsed_ms
        }

    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/v1/search", response_model=SearchResponse)
async def search_vectors(req: SearchRequest, request: Request):
    """Vector similarity search"""
    client = get_client()

    try:
        start = time.time()
        results = await client.search_similar(
            req.query,
            req.limit,
            req.threshold
        )
        elapsed_ms = int((time.time() - start) * 1000)

        # Log query
        await client.log_query(
            user_id=request.client.host,
            query=req.query,
            results=results,
            response_time_ms=elapsed_ms
        )

        return SearchResponse(
            results=results,
            query_time_ms=elapsed_ms
        )

    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/v1/analytics")
async def get_analytics():
    """Get usage analytics"""
    client = get_client()

    async with client.pool.acquire() as conn:
        # Total embeddings
        total_embeddings = await conn.fetchval("SELECT COUNT(*) FROM embeddings")

        # Total queries
        total_queries = await conn.fetchval("SELECT COUNT(*) FROM user_queries")

        # Avg response time
        avg_response = await conn.fetchval(
            "SELECT AVG(response_time_ms) FROM user_queries"
        )

        # Top queries
        top_queries = await conn.fetch(
            """
            SELECT query, COUNT(*) as count
            FROM user_queries
            GROUP BY query
            ORDER BY count DESC
            LIMIT 10
            """
        )

    return {
        "total_embeddings": total_embeddings,
        "total_queries": total_queries,
        "avg_response_time_ms": float(avg_response) if avg_response else 0,
        "top_queries": [dict(row) for row in top_queries]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## DEPLOYMENT SCRIPT

Create `deploy-primax-supabase.sh`:

```bash
#!/bin/zsh
# Deploy PRIMAX with Supabase backend

set -e

cd ~/claude_enterprise/workspace/PRIMAX-ai

# 1. Install dependencies
source ~/claude_enterprise/.venvs/tools_env/bin/activate
pip install -q fastapi uvicorn asyncpg sentence-transformers numpy

# 2. Load secrets from vault
python -c "from src.vault_manager import get_all_env; get_all_env()"

# 3. Test Supabase connection
python -c "
import asyncio
from src.db.supabase_client import get_client

async def test():
    client = get_client()
    await client.connect()
    print('✅ Supabase connected')
    await client.close()

asyncio.run(test())
"

# 4. Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
asyncpg==0.29.0
sentence-transformers==2.2.2
numpy==1.24.3
pydantic==2.5.0
python-dotenv==1.0.0
EOF

# 5. Update render.yaml
cat > render.yaml << 'EOF'
services:
  - type: web
    name: primax-ai-supabase
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
    autoDeploy: true
EOF

# 6. Test locally
echo "🧪 Testing locally..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!
sleep 5

curl -s http://localhost:8000/health | grep "supabase" && echo "✅ Health check passed"

kill $UVICORN_PID

# 7. Commit and push
git add -A
git commit -m "Add Supabase pgvector backend

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

echo ""
echo "✅ Ready to deploy!"
echo ""
echo "Next steps:"
echo "  1. Push to GitHub: git push origin main"
echo "  2. Go to https://dashboard.render.com"
echo "  3. Connect repo and add env vars"
echo "  4. Deploy!"
```

---

## MONETIZATION AUTOMATION

### Ethical Email Marketing (Consent-Based)

Create `src/monetization/email_automation.py`:

```python
"""
Ethical email marketing automation
REQUIRES: Double opt-in, unsubscribe links, GDPR compliance
"""
import asyncio
from supabase import create_client, Client
import os
from typing import List, Dict

# Supabase client for leads
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

class EmailCampaign:
    """Consent-based email campaigns"""

    def __init__(self, campaign_name: str):
        self.campaign_name = campaign_name

    async def add_lead(
        self,
        email: str,
        name: str,
        source: str,
        opted_in: bool = False
    ):
        """Add lead (requires explicit consent)"""
        if not opted_in:
            print(f"⚠️ {email} not opted in - sending confirmation")
            await self.send_opt_in_email(email, name)
            return

        # Store in Supabase
        supabase.table('email_leads').insert({
            'email': email,
            'name': name,
            'source': source,
            'campaign': self.campaign_name,
            'opted_in': True,
            'opt_in_date': 'now()'
        }).execute()

        print(f"✅ Lead added: {email}")

    async def send_opt_in_email(self, email: str, name: str):
        """Send double opt-in confirmation"""
        # Use SendGrid or similar
        # MUST include unsubscribe link
        # MUST comply with GDPR/CAN-SPAM
        pass

    async def send_campaign(
        self,
        subject: str,
        content: str,
        limit: int = 50  # Daily limit to avoid spam
    ):
        """Send to opted-in leads only"""
        # Get opted-in leads
        leads = supabase.table('email_leads')\
            .select('*')\
            .eq('campaign', self.campaign_name)\
            .eq('opted_in', True)\
            .limit(limit)\
            .execute()

        print(f"📧 Sending to {len(leads.data)} opted-in leads")

        for lead in leads.data:
            # Send via SendGrid/Mailgun
            # MUST include unsubscribe link
            print(f"  → {lead['email']}")

        return len(leads.data)

# Usage example
async def main():
    campaign = EmailCampaign("PRIMAX Launch")

    # Add lead with consent
    await campaign.add_lead(
        email="user@example.com",
        name="John Doe",
        source="website_signup",
        opted_in=True  # User clicked confirmation link
    )

    # Send campaign (max 50/day)
    await campaign.send_campaign(
        subject="PRIMAX AI is Live!",
        content="...",
        limit=50
    )

if __name__ == "__main__":
    asyncio.run(main())
```

**CRITICAL:** This requires:
1. Double opt-in (confirmation email)
2. Unsubscribe link in every email
3. GDPR consent tracking
4. CAN-SPAM compliance
5. Daily sending limits

---

## EXECUTION TIMELINE

### Hour 0-2: Supabase Setup
```bash
# 1. Create Supabase project
# 2. Run SQL schema (above)
# 3. Get credentials
# 4. Store in vault
python src/vault_manager.py store --key=SUPABASE_URL --value=https://...
python src/vault_manager.py store --key=SUPABASE_SERVICE_KEY --value=eyJ...
```

### Hour 2-4: Local Testing
```bash
cd ~/claude_enterprise/workspace/PRIMAX-ai
source ~/claude_enterprise/.venvs/tools_env/bin/activate
pip install fastapi uvicorn asyncpg sentence-transformers
uvicorn src.main:app --reload
```

### Hour 4-6: Deployment
```bash
./deploy-primax-supabase.sh
git push origin main
# Configure Render with env vars
```

### Hour 6-8: Validation
```bash
# Test embeddings
curl -X POST https://primax-ai.onrender.com/v1/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Test embedding"]}'

# Test search
curl -X POST https://primax-ai.onrender.com/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "automation", "limit": 5}'

# Check analytics
curl https://primax-ai.onrender.com/v1/analytics
```

---

## REVENUE STREAMS (ETHICAL)

1. **API as a Service:** Charge for vector search API access
2. **Consulting:** RAG integration services (€300/sprint)
3. **White Label:** License PRIMAX stack (€5,000)
4. **Content:** Gumroad products on automation

**Avoid:** Spam, unsolicited emails, data scraping

---

**WATERMARK: PRIMAX-AI-BSP-2025**
**© 2025 Bakery Street Project**
