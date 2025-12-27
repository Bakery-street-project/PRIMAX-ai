#!/usr/bin/env python3
"""
Supabase Schema Setup via REST API
Works on Termux where direct PostgreSQL connections are blocked

© 2025 Bakery Street Project
WATERMARK: PRIMAX-AI-BSP-2025
"""
import requests
import os
import sys
import json
from pathlib import Path

def execute_sql_via_api(url: str, service_key: str, sql: str):
    """Execute SQL via Supabase Edge Function or Management API"""

    print("=" * 60)
    print("SUPABASE SCHEMA SETUP (REST API)")
    print("=" * 60)
    print()

    # Try multiple endpoints
    attempts = [
        # Method 1: Use Supabase SQL endpoint (if available)
        {
            'name': 'SQL Endpoint',
            'url': f"{url}/rest/v1/rpc/exec",
            'method': 'POST',
            'headers': {
                'apikey': service_key,
                'Authorization': f'Bearer {service_key}',
                'Content-Type': 'application/json'
            },
            'data': {'query': sql}
        },
        # Method 2: Direct database endpoint
        {
            'name': 'Database Endpoint',
            'url': f"{url}/database/exec",
            'method': 'POST',
            'headers': {
                'apikey': service_key,
                'Authorization': f'Bearer {service_key}',
                'Content-Type': 'application/json'
            },
            'data': {'sql': sql}
        }
    ]

    # Since direct SQL execution isn't available via REST API by default,
    # we'll use the web-based approach with instructions
    print("⚠️  Direct SQL execution requires Supabase dashboard")
    print()
    print("=" * 60)
    print("AUTOMATED SQL SCHEMA PREPARATION")
    print("=" * 60)
    print()

    # Split SQL into executable chunks
    schema_file = Path(__file__).parent / 'supabase_schema.sql'

    with open(schema_file, 'r') as f:
        sql_content = f.read()

    print(f"✅ Loaded schema: {len(sql_content):,} characters")
    print(f"   {len(sql_content.splitlines())} lines")
    print()

    # Save to clipboard-friendly format
    output_file = Path(__file__).parent / 'schema_for_dashboard.sql'

    with open(output_file, 'w') as f:
        f.write(sql_content)

    print(f"✅ Schema ready at: {output_file}")
    print()

    # Provide instructions
    print("=" * 60)
    print("NEXT STEPS (Manual - 2 minutes)")
    print("=" * 60)
    print()
    print("1. Copy the schema SQL:")
    print(f"   cat {output_file}")
    print()
    print("2. Open Supabase dashboard:")
    print(f"   {url.replace('/rest/v1', '')}")
    print()
    print("3. Go to SQL Editor (left sidebar)")
    print()
    print("4. Click 'New query'")
    print()
    print("5. Paste the SQL and click 'Run'")
    print()
    print("6. Verify you see: 'Schema setup complete! ✅'")
    print()

    # Alternative: Use supabase-py client for basic operations
    print("=" * 60)
    print("ALTERNATIVE: Use Python Client (Limited)")
    print("=" * 60)
    print()

    try:
        from supabase import create_client, Client

        supabase: Client = create_client(url, service_key)

        print("✅ Supabase client initialized")
        print()

        # We can at least verify connection works
        print("Testing connection via REST API...")

        # Try to check if tables exist
        try:
            # This will fail if table doesn't exist, which is expected
            result = supabase.table('embeddings').select("count", count='exact').execute()
            print(f"✅ Connection works! Found 'embeddings' table with {result.count} rows")
            print("   (Schema already installed)")
            return True
        except Exception as e:
            if 'relation' in str(e).lower() or 'does not exist' in str(e).lower():
                print("⚠️  Tables not yet created - proceed with manual setup above")
                return False
            else:
                print(f"⚠️  Connection test: {e}")
                return False

    except ImportError:
        print("ℹ️  Install supabase-py: pip install supabase")
        return False

def verify_schema(url: str, service_key: str):
    """Verify schema is installed via REST API"""

    try:
        from supabase import create_client

        supabase = create_client(url, service_key)

        print()
        print("=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        print()

        # Check tables
        tables_to_check = ['embeddings', 'user_queries', 'api_logs']
        tables_found = []

        for table in tables_to_check:
            try:
                result = supabase.table(table).select("count", count='exact').limit(1).execute()
                tables_found.append(table)
                print(f"✅ Table '{table}': exists ({result.count} rows)")
            except Exception:
                print(f"❌ Table '{table}': not found")

        print()
        print(f"Summary: {len(tables_found)}/{len(tables_to_check)} tables verified")

        return len(tables_found) == len(tables_to_check)

    except ImportError:
        print("⚠️  Install supabase-py for verification: pip install supabase")
        return False

def main():
    """Main entry point"""

    # Get credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')

    if not url or not key:
        print("Enter Supabase credentials:")
        url = input("Project URL (https://xxx.supabase.co): ").strip()
        key = input("Service Role Key: ").strip()

    if not url or not key:
        print("❌ Credentials required")
        sys.exit(1)

    # Prepare schema
    execute_sql_via_api(url, key, "")

    print()
    print("After running SQL in dashboard, verify with:")
    print(f"  export SUPABASE_URL='{url}'")
    print(f"  export SUPABASE_SERVICE_KEY='...'")
    print(f"  python setup_supabase_rest.py --verify")
    print()

    # Check if user wants to verify
    if '--verify' in sys.argv or '-v' in sys.argv:
        success = verify_schema(url, key)
        if success:
            print()
            print("✅ Schema verification complete!")
            print()
            print("Next steps:")
            print("  1. Test client: python src/db/supabase_client.py")
            print("  2. Start API: uvicorn src.main:app --reload")
            sys.exit(0)
        else:
            print()
            print("❌ Schema not fully installed")
            sys.exit(1)

if __name__ == "__main__":
    main()
