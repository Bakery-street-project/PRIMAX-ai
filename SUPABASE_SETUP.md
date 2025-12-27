# Supabase Setup for PRIMAX AI

## 🗄️ Database Schema

PRIMAX AI can use Supabase for persistent storage of:
- Chat sessions
- Repository analyses
- Code generation history
- User preferences

## 🚀 Quick Setup

### 1. Create Supabase Project
```bash
# Visit https://supabase.com/dashboard
# Create new project: primax-ai
# Save your credentials:
# - Project URL: https://xxx.supabase.co
# - Anon Public Key: eyJhbG...
# - Service Role Key: eyJhbG... (secret!)
```

### 2. Create Tables

```sql
-- Chat Sessions
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_active TIMESTAMPTZ DEFAULT NOW(),
  context JSONB,
  message_count INTEGER DEFAULT 0
);

-- Chat Messages
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT REFERENCES chat_sessions(session_id),
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB
);

-- Repository Analyses
CREATE TABLE repo_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_full_name TEXT NOT NULL,
  analysis_data JSONB NOT NULL,
  analyzed_at TIMESTAMPTZ DEFAULT NOW(),
  INDEX idx_repo_name (repo_full_name)
);

-- Code Generations
CREATE TABLE code_generations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt TEXT NOT NULL,
  language TEXT NOT NULL,
  generated_code TEXT NOT NULL,
  explanation TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. Add to Render Environment

```bash
# In Render Dashboard → primax-ai → Environment:
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...  # Anon key for read/write
SUPABASE_SERVICE_KEY=eyJhbG...  # Service key for admin operations
```

### 4. Install Supabase Client

```bash
pip install supabase
```

### 5. Integration Code (Optional - Not Required for MVP)

Create `src/database/supabase_client.py`:

```python
from supabase import create_client
import os

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client = create_client(url, key) if url and key else None

    async def save_chat_session(self, session_data):
        if not self.client:
            return None
        return self.client.table("chat_sessions").insert(session_data).execute()
```

## 📝 Current Status

**PRIMAX AI currently works WITHOUT Supabase** - all data is in-memory.

**Add Supabase for:**
- Persistent chat history across restarts
- Analytics dashboard
- Multi-user support
- Data export/backup

## 🎯 Next Steps (Optional)

Monday when you upgrade to Starter:
1. Create Supabase free tier project
2. Run SQL schema above
3. Add environment variables to Render
4. Install `supabase` package
5. Data will persist across deployments!

---

**Watermark:** PRIMAX-AI-BSP-2025
**Copyright:** 2024-2025 Bakery Street Project
