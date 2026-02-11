-- PRIMAX Supabase Schema
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard
-- © 2025 Bakery Street Project
-- WATERMARK: PRIMAX-AI-BSP-2025

-- ============================================================================
-- STEP 1: Enable pgvector Extension
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- STEP 2: Create Embeddings Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(384),  -- 384 dimensions for all-MiniLM-L6-v2
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for vector similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx
ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create text search index
CREATE INDEX IF NOT EXISTS embeddings_content_idx
ON embeddings
USING GIN (to_tsvector('english', content));

-- Create metadata index
CREATE INDEX IF NOT EXISTS embeddings_metadata_idx
ON embeddings
USING GIN (metadata);

COMMENT ON TABLE embeddings IS 'Vector embeddings for semantic search';
COMMENT ON COLUMN embeddings.embedding IS '384-dimensional vectors from all-MiniLM-L6-v2';

-- ============================================================================
-- STEP 3: Create User Queries Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_queries (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT,
    query TEXT NOT NULL,
    results JSONB,
    response_time_ms INTEGER,
    similarity_threshold REAL DEFAULT 0.7,
    limit_count INTEGER DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_queries_user ON user_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_created ON user_queries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_queries_response_time ON user_queries(response_time_ms);

COMMENT ON TABLE user_queries IS 'Log of all search queries for analytics';

-- ============================================================================
-- STEP 4: Create API Logs Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS api_logs (
    id BIGSERIAL PRIMARY KEY,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER,
    request_data JSONB,
    response_data JSONB,
    ip_address TEXT,
    user_agent TEXT,
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_logs_endpoint ON api_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_logs_status ON api_logs(status_code);
CREATE INDEX IF NOT EXISTS idx_logs_created ON api_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_ip ON api_logs(ip_address);

COMMENT ON TABLE api_logs IS 'API request/response logs for monitoring';

-- ============================================================================
-- STEP 5: Create Analytics Views
-- ============================================================================

-- Popular queries
CREATE OR REPLACE VIEW popular_queries AS
SELECT
    query,
    COUNT(*) as query_count,
    AVG(response_time_ms) as avg_response_time,
    MIN(response_time_ms) as min_response_time,
    MAX(response_time_ms) as max_response_time
FROM user_queries
GROUP BY query
ORDER BY query_count DESC
LIMIT 100;

-- API endpoint stats
CREATE OR REPLACE VIEW api_stats AS
SELECT
    endpoint,
    method,
    COUNT(*) as request_count,
    AVG(execution_time_ms) as avg_execution_time,
    COUNT(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 END) as success_count,
    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count
FROM api_logs
GROUP BY endpoint, method
ORDER BY request_count DESC;

-- Daily usage stats
CREATE OR REPLACE VIEW daily_usage AS
SELECT
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(*) as total_queries,
    AVG(response_time_ms) as avg_response_time
FROM user_queries
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================================================
-- STEP 6: Enable Row Level Security (RLS)
-- ============================================================================

ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- STEP 7: Create RLS Policies
-- ============================================================================

-- Service role has full access (for backend API)
CREATE POLICY "Service role full access embeddings"
ON embeddings
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role full access queries"
ON user_queries
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role full access logs"
ON api_logs
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Authenticated users can read embeddings
CREATE POLICY "Authenticated users can read embeddings"
ON embeddings
FOR SELECT
TO authenticated
USING (true);

-- ============================================================================
-- STEP 8: Create Functions
-- ============================================================================

-- Function to search similar embeddings
CREATE OR REPLACE FUNCTION search_embeddings(
    query_embedding VECTOR(384),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        embeddings.id,
        embeddings.content,
        embeddings.metadata,
        1 - (embeddings.embedding <=> query_embedding) AS similarity
    FROM embeddings
    WHERE 1 - (embeddings.embedding <=> query_embedding) > match_threshold
    ORDER BY embeddings.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to update embeddings updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_embeddings_updated_at
BEFORE UPDATE ON embeddings
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- STEP 9: Insert Sample Data (Optional - for testing)
-- ============================================================================

-- Insert test embeddings (random vectors for testing)
INSERT INTO embeddings (content, embedding, metadata) VALUES
(
    'PRIMAX is a self-learning AI automation engine',
    ARRAY(SELECT random() FROM generate_series(1, 384))::vector,
    '{"category": "description", "source": "documentation"}'::jsonb
),
(
    'Vector search enables semantic similarity matching',
    ARRAY(SELECT random() FROM generate_series(1, 384))::vector,
    '{"category": "feature", "source": "documentation"}'::jsonb
),
(
    'Supabase provides PostgreSQL with pgvector extension',
    ARRAY(SELECT random() FROM generate_series(1, 384))::vector,
    '{"category": "infrastructure", "source": "documentation"}'::jsonb
);

-- ============================================================================
-- STEP 10: Grant Permissions
-- ============================================================================

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

-- ============================================================================
-- STEP 11: Verify Installation
-- ============================================================================

-- Check if pgvector is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Check indexes
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Count sample data
SELECT
    'embeddings' as table_name,
    COUNT(*) as row_count
FROM embeddings;

-- ============================================================================
-- SETUP COMPLETE
-- ============================================================================

-- Next steps:
-- 1. Copy Project URL from Settings → API
-- 2. Copy Service Role Key from Settings → API
-- 3. Store credentials in PRIMAX vault
-- 4. Test connection from PRIMAX

SELECT 'Schema setup complete! ✅' as status;
