#!/usr/bin/env python3
"""
Automated Supabase Schema Setup (non-interactive)
"""

import asyncio
import asyncpg
import os

async def setup_schema():
    """Execute schema SQL against Supabase database"""

    # Hardcoded for primax-ai project
    url = "https://oqlhdqhcxugjqpvgdnfb.supabase.co"
    
    # You'll need to get this from supabase secrets
    # For now, let's try without service key and see what happens
    service_key = os.getenv('SUPABASE_SERVICE_KEY', '')
    
    if not service_key:
        print("❌ SUPABASE_SERVICE_KEY not set")
        print("Please run: export SUPABASE_SERVICE_KEY=your_service_key_here")
        return False

    # Extract project ID from URL
    project_id = url.replace('https://', '').replace('.supabase.co', '')

    # Construct direct Postgres connection
    db_url = f"postgresql://postgres:{service_key}@db.{project_id}.supabase.co:5432/postgres"

    print("=" * 60)
    print("SUPABASE SCHEMA SETUP")
    print("=" * 60)
    print(f"\nProject ID: {project_id}")
    print(f"Connecting to database...\n")

    try:
        # Connect
        conn = await asyncpg.connect(db_url, timeout=30)
        print("✅ Connected to Supabase PostgreSQL")

        # Read SQL schema
        schema_file = 'supabase_schema.sql'

        if not os.path.exists(schema_file):
            print(f"❌ Schema file not found: {schema_file}")
            return False

        with open(schema_file, 'r') as f:
            sql = f.read()

        print(f"📄 Loaded schema: {len(sql):,} characters")
        print(f"   {len(sql.splitlines())} lines\n")

        # Split and execute SQL statements
        print("Executing schema...\n")

        # Execute as one transaction
        await conn.execute(sql)

        print("✅ Schema executed successfully")

        # Verify installation
        print("\n" + "=" * 60)
        print("VERIFICATION")
        print("=" * 60 + "\n")

        # Check pgvector
        ext_count = await conn.fetchval(
            "SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'"
        )
        print(f"{'✅' if ext_count > 0 else '❌'} pgvector extension: {'installed' if ext_count > 0 else 'MISSING'}")

        # Check tables
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)

        print(f"\n✅ Tables created: {len(tables)}")
        for table in tables:
            print(f"   • {table['table_name']}")

        # Check indexes
        indexes = await conn.fetch("""
            SELECT tablename, indexname FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)

        print(f"\n✅ Indexes created: {len(indexes)}")

        # Check sample data
        embedding_count = await conn.fetchval("SELECT COUNT(*) FROM embeddings")
        print(f"\n✅ Sample embeddings: {embedding_count}")

        await conn.close()

        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE")
        print("=" * 60)

        return True

    except asyncpg.PostgresError as e:
        print(f"\n❌ PostgreSQL Error: {e}")
        return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_schema())
    
    if success:
        print(f"\nNext steps:")
        print(f"  1. Test connection: python src/db/supabase_client.py")
        print(f"  2. Start FastAPI: uvicorn src.main:app --reload")
        print(f"  3. Deploy to Render: ~/execute-primax-deployment.sh")
    else:
        print("\n❌ Setup failed - check errors above")
