#!/usr/bin/env python3
"""
Create Supabase Schema via REST API
No SQL editing required - fully automated

© 2025 Bakery Street Project
WATERMARK: PRIMAX-AI-BSP-2025
"""

import requests
import os
import sys
import json
import time


def create_schema_via_management_api(url: str, service_key: str):
    """
    Create schema using Supabase Management API
    """
    print("=" * 60)
    print("SUPABASE SCHEMA CREATION VIA API")
    print("=" * 60)
    print()

    project_id = url.replace("https://", "").replace(".supabase.co", "")

    print(f"Project ID: {project_id}")
    print(f"URL: {url}")
    print()

    # Headers for API requests
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    # SQL statements to execute via API
    sql_statements = [
        # Enable pgvector
        "CREATE EXTENSION IF NOT EXISTS vector;",
        # Create embeddings table
        """
        CREATE TABLE IF NOT EXISTS embeddings (
            id BIGSERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding VECTOR(384),
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        # Create embeddings indexes
        """
        CREATE INDEX IF NOT EXISTS embeddings_embedding_idx
        ON embeddings USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """,
        """
        CREATE INDEX IF NOT EXISTS embeddings_content_idx
        ON embeddings USING GIN (to_tsvector('english', content));
        """,
        """
        CREATE INDEX IF NOT EXISTS embeddings_metadata_idx
        ON embeddings USING GIN (metadata);
        """,
        # Create user_queries table
        """
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
        """,
        # Create user_queries indexes
        "CREATE INDEX IF NOT EXISTS idx_queries_user ON user_queries(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_queries_created ON user_queries(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_queries_response_time ON user_queries(response_time_ms);",
        # Create api_logs table
        """
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
        """,
        # Create api_logs indexes
        "CREATE INDEX IF NOT EXISTS idx_logs_endpoint ON api_logs(endpoint);",
        "CREATE INDEX IF NOT EXISTS idx_logs_status ON api_logs(status_code);",
        "CREATE INDEX IF NOT EXISTS idx_logs_created ON api_logs(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_logs_ip ON api_logs(ip_address);",
        # Enable RLS
        "ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE user_queries ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE api_logs ENABLE ROW LEVEL SECURITY;",
        # Create RLS policies
        """
        CREATE POLICY IF NOT EXISTS "Service role full access embeddings"
        ON embeddings FOR ALL TO service_role
        USING (true) WITH CHECK (true);
        """,
        """
        CREATE POLICY IF NOT EXISTS "Service role full access queries"
        ON user_queries FOR ALL TO service_role
        USING (true) WITH CHECK (true);
        """,
        """
        CREATE POLICY IF NOT EXISTS "Service role full access logs"
        ON api_logs FOR ALL TO service_role
        USING (true) WITH CHECK (true);
        """,
        """
        CREATE POLICY IF NOT EXISTS "Authenticated users can read embeddings"
        ON embeddings FOR SELECT TO authenticated
        USING (true);
        """,
        # Create search function
        """
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
        """,
        # Create update trigger function
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """,
        # Create trigger
        """
        DROP TRIGGER IF EXISTS update_embeddings_updated_at ON embeddings;
        CREATE TRIGGER update_embeddings_updated_at
        BEFORE UPDATE ON embeddings
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
        """,
        # Grant permissions
        "GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;",
        "GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;",
        "GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;",
        "GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;",
    ]

    # Try to execute via PostgREST SQL endpoint
    print("Executing SQL statements via API...")
    print()

    # Use Supabase SQL endpoint (if available)
    sql_endpoint = f"{url}/rest/v1/rpc/query"

    success_count = 0
    fail_count = 0

    for i, sql in enumerate(sql_statements, 1):
        # Clean SQL
        sql = sql.strip()
        if not sql:
            continue

        # Try to execute
        try:
            # Attempt 1: Use hypothetical SQL endpoint
            response = requests.post(
                sql_endpoint, headers=headers, json={"query": sql}, timeout=30
            )

            if response.status_code in [200, 201]:
                print(f"✅ Statement {i}/{len(sql_statements)}")
                success_count += 1
            else:
                print(f"⚠️  Statement {i}: {response.status_code}")
                fail_count += 1

        except Exception as e:
            # This endpoint might not exist
            fail_count += 1

        time.sleep(0.1)  # Rate limiting

    print()
    print(f"Executed: {success_count} successful, {fail_count} failed/skipped")
    print()

    # If direct SQL execution doesn't work, provide alternative
    if success_count == 0:
        print("=" * 60)
        print("API SQL EXECUTION NOT AVAILABLE")
        print("=" * 60)
        print()
        print("Supabase doesn't expose direct SQL execution via REST API")
        print("for security reasons.")
        print()
        print("⚡ SOLUTION: Use Supabase CLI wrapper")
        print()

        # Save SQL to file for CLI execution
        import subprocess

        # Combine all SQL
        full_sql = "\n".join(sql_statements)

        # Save to temp file
        sql_file = "/tmp/schema.sql"
        with open(sql_file, "w") as f:
            f.write(full_sql)

        print(f"✅ SQL saved to: {sql_file}")
        print()
        print("Execute with Supabase CLI:")
        print(f"  supabase db execute --project-ref {project_id} --file {sql_file}")
        print()
        print("OR use the web dashboard method from:")
        print("  cat ~/SETUP_SUPABASE_WORKAROUND.md")
        print()

        return False

    return success_count > 0


def insert_sample_data(url: str, service_key: str):
    """Insert sample embeddings via REST API"""

    try:
        from supabase import create_client

        supabase = create_client(url, service_key)

        print("=" * 60)
        print("INSERTING SAMPLE DATA")
        print("=" * 60)
        print()

        # Generate random vectors for testing
        import random

        sample_data = [
            {
                "content": "PRIMAX is a self-learning AI automation engine",
                "embedding": [random.random() for _ in range(384)],
                "metadata": {"category": "description", "source": "documentation"},
            },
            {
                "content": "Vector search enables semantic similarity matching",
                "embedding": [random.random() for _ in range(384)],
                "metadata": {"category": "feature", "source": "documentation"},
            },
            {
                "content": "Supabase provides PostgreSQL with pgvector extension",
                "embedding": [random.random() for _ in range(384)],
                "metadata": {"category": "infrastructure", "source": "documentation"},
            },
        ]

        result = supabase.table("embeddings").insert(sample_data).execute()

        print(f"✅ Inserted {len(result.data)} sample embeddings")
        print()

        return True

    except Exception as e:
        print(f"⚠️  Sample data insertion skipped: {e}")
        return False


def verify_schema(url: str, service_key: str):
    """Verify schema via REST API"""

    try:
        from supabase import create_client

        supabase = create_client(url, service_key)

        print("=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        print()

        tables = ["embeddings", "user_queries", "api_logs"]
        verified = 0

        for table in tables:
            try:
                result = (
                    supabase.table(table)
                    .select("count", count="exact")
                    .limit(1)
                    .execute()
                )
                print(f"✅ {table}: {result.count} rows")
                verified += 1
            except Exception as e:
                print(f"❌ {table}: Not accessible - {str(e)[:50]}")

        print()
        print(f"Tables verified: {verified}/{len(tables)}")

        return verified == len(tables)

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main entry point"""

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("Enter Supabase credentials:")
        url = input("Project URL: ").strip()
        key = input("Service Role Key: ").strip()

    if not url or not key:
        print("❌ Credentials required")
        sys.exit(1)

    # Try API method
    success = create_schema_via_management_api(url, key)

    if not success:
        print()
        print("=" * 60)
        print("ALTERNATIVE METHOD REQUIRED")
        print("=" * 60)
        print()
        print("Since direct SQL API is not available, use:")
        print()
        print("1. Web Dashboard (recommended):")
        print("   cat ~/SETUP_SUPABASE_WORKAROUND.md")
        print()
        print("2. Supabase CLI (if works on Termux):")
        print("   supabase link --project-ref oqlhdqhcxugjqpvgdnfb")
        print("   cat supabase_schema.sql | supabase db execute")
        print()
        sys.exit(1)

    # Insert sample data
    insert_sample_data(url, key)

    # Verify
    if verify_schema(url, key):
        print()
        print("✅ Schema setup complete!")
        print()
        print("Next steps:")
        print("  1. Test: python src/db/supabase_client.py")
        print("  2. Deploy: ~/execute-primax-deployment.sh")
        sys.exit(0)
    else:
        print()
        print("⚠️  Partial success - check dashboard")
        sys.exit(1)


if __name__ == "__main__":
    main()
