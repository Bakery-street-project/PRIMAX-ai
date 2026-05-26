"""
Async Supabase client with pgvector support
Constraints: Batch size <1000, connection pooling for 4GB RAM

© 2025 Bakery Street Project
WATERMARK: PRIMAX-AI-BSP-2025
"""

import asyncio
import asyncpg
import numpy as np
from typing import List, Dict, Any, Optional
import os
from functools import lru_cache

# Try to import sentence-transformers, fallback to mock
try:
    from sentence_transformers import SentenceTransformer

    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("⚠️ sentence-transformers not installed - using mock embeddings")


# Embedding model (cached in RAM)
@lru_cache(maxsize=1)
def get_model():
    """Load embedding model once (384-dim for RAM efficiency)"""
    if HAS_TRANSFORMERS:
        return SentenceTransformer("all-MiniLM-L6-v2")
    else:
        # Mock model for testing
        class MockModel:
            def encode(self, texts, show_progress_bar=False):
                # Return random 384-dim vectors
                return np.random.rand(len(texts), 384).astype(np.float32)

        return MockModel()


class SupabaseVectorClient:
    """Async client for Supabase with pgvector"""

    def __init__(self, url: str, service_key: str):
        self.url = url
        self.service_key = service_key
        self.pool: Optional[asyncpg.Pool] = None

        # Extract connection params from Supabase URL
        # Format: https://project-id.supabase.co
        project_id = url.replace("https://", "").replace(".supabase.co", "")

        # Supabase direct database connection
        # Password is the service role key
        self.db_url = f"postgresql://postgres.{project_id}:{service_key}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

    async def connect(self):
        """Create connection pool"""
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    self.db_url,
                    min_size=1,
                    max_size=3,  # Low for RAM constraints
                    command_timeout=60,
                    server_settings={"jit": "off"},  # Disable JIT for stability
                )
                print("✅ Connected to Supabase")
            except Exception as e:
                print(f"❌ Failed to connect to Supabase: {e}")
                print("   Check your SUPABASE_URL and SUPABASE_SERVICE_KEY")
                raise

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
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
        batch_size: int = 500,
    ) -> int:
        """Insert embeddings in batches"""
        if not self.pool:
            await self.connect()

        total_inserted = 0

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_metadata = (
                metadata[i : i + batch_size] if metadata else [{}] * len(batch_texts)
            )

            # Generate embeddings
            embeddings = await self.embed_text(batch_texts)

            # Insert batch
            if not self.pool:
                await self.connect()

            async with self.pool.acquire() as conn:
                for text, embedding, meta in zip(
                    batch_texts, embeddings, batch_metadata
                ):
                    try:
                        await conn.execute(
                            """
                            INSERT INTO embeddings (content, embedding, metadata)
                            VALUES ($1, $2, $3)
                            """,
                            text,
                            embedding.tolist(),
                            meta,
                        )
                        total_inserted += 1
                    except Exception as e:
                        print(f"⚠️ Failed to insert embedding: {e}")

                print(
                    f"  Inserted batch {i // batch_size + 1}: {len(batch_texts)} embeddings"
                )

        return total_inserted

    async def search_similar(
        self, query: str, limit: int = 10, threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Vector similarity search using cosine distance"""
        if not self.pool:
            await self.connect()

        # Embed query
        query_embedding = await self.embed_text([query])
        query_vector = query_embedding[0].tolist()

        # Search using pgvector cosine distance operator (<=>)
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
                limit,
            )

        results = [
            {
                "id": row["id"],
                "content": row["content"],
                "metadata": row["metadata"],
                "similarity": float(row["similarity"]),
            }
            for row in rows
        ]

        return results

    async def log_query(
        self, user_id: str, query: str, results: List[Dict], response_time_ms: int
    ):
        """Log user query for analytics"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            try:
                await conn.execute(
                    """
                    INSERT INTO user_queries (user_id, query, results, response_time_ms)
                    VALUES ($1, $2, $3, $4)
                    """,
                    user_id,
                    query,
                    results,
                    response_time_ms,
                )
            except Exception as e:
                print(f"⚠️ Failed to log query: {e}")

    async def log_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        request_data: Dict,
        response_data: Dict,
        ip_address: str,
    ):
        """Log API call for monitoring"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            try:
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
                    ip_address,
                )
            except Exception as e:
                print(f"⚠️ Failed to log API call: {e}")

    async def get_analytics(self) -> Dict[str, Any]:
        """Get usage analytics"""
        if not self.pool:
            await self.connect()

        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            # Total embeddings
            total_embeddings = await conn.fetchval("SELECT COUNT(*) FROM embeddings")

            # Total queries
            total_queries = await conn.fetchval("SELECT COUNT(*) FROM user_queries")

            # Avg response time
            avg_response = await conn.fetchval(
                "SELECT AVG(response_time_ms) FROM user_queries"
            )

            # Top queries
            top_queries = await conn.fetch("""
                SELECT query, COUNT(*) as count
                FROM user_queries
                GROUP BY query
                ORDER BY count DESC
                LIMIT 10
                """)

        return {
            "total_embeddings": total_embeddings,
            "total_queries": total_queries,
            "avg_response_time_ms": float(avg_response) if avg_response else 0,
            "top_queries": [dict(row) for row in top_queries],
        }


# Global client instance
_client: Optional[SupabaseVectorClient] = None


def get_client() -> SupabaseVectorClient:
    """Get or create singleton client"""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables required\n"
                "Get them from: https://supabase.com/dashboard → Settings → API"
            )

        _client = SupabaseVectorClient(url, key)

    return _client


# CLI test
if __name__ == "__main__":

    async def test():
        """Test connection and basic operations"""
        print("Testing Supabase connection...")

        client = get_client()
        await client.connect()

        # Test embedding
        print("\n1. Testing embedding...")
        texts = ["Hello world", "Test embedding", "PRIMAX automation"]
        count = await client.insert_embeddings(texts)
        print(f"✅ Inserted {count} embeddings")

        # Test search
        print("\n2. Testing search...")
        results = await client.search_similar("automation", limit=5)
        print(f"✅ Found {len(results)} results")
        for r in results:
            print(f"   - {r['content']} (similarity: {r['similarity']:.3f})")

        # Test analytics
        print("\n3. Testing analytics...")
        analytics = await client.get_analytics()
        print(f"✅ Analytics: {analytics}")

        await client.close()

    asyncio.run(test())
