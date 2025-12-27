#!/usr/bin/env python3
"""
Automated Supabase Schema Setup
Executes SQL schema via asyncpg

© 2025 Bakery Street Project
WATERMARK: PRIMAX-AI-BSP-2025
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

async def setup_schema(url: str, service_key: str):
    """Execute schema SQL against Supabase database"""

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
        schema_file = Path(__file__).parent / 'supabase_schema.sql'

        if not schema_file.exists():
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

        # Check functions
        functions = await conn.fetch("""
            SELECT routine_name FROM information_schema.routines
            WHERE routine_schema = 'public' AND routine_type = 'FUNCTION'
        """)

        print(f"\n✅ Functions created: {len(functions)}")
        for func in functions:
            print(f"   • {func['routine_name']}")

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

def main():
    """Main entry point"""

    # Get credentials from environment or prompt
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')

    if not url or not key:
        print("Enter Supabase credentials:")
        url = input("Project URL (https://xxx.supabase.co): ").strip()
        key = input("Service Role Key: ").strip()

    if not url or not key:
        print("❌ Credentials required")
        sys.exit(1)

    # Validate URL
    if not url.startswith('https://'):
        print("❌ URL must start with https://")
        sys.exit(1)

    if not '.supabase.co' in url:
        print("❌ URL must be a Supabase URL")
        sys.exit(1)

    # Run setup
    success = asyncio.run(setup_schema(url, key))

    if success:
        print(f"\nNext steps:")
        print(f"  1. Test connection: python src/db/supabase_client.py")
        print(f"  2. Start FastAPI: uvicorn src.main:app --reload")
        print(f"  3. Deploy to Render: ~/execute-primax-deployment.sh")
        print(f"\nDatabase URL: {url}")
        sys.exit(0)
    else:
        print("\n❌ Setup failed - check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()
