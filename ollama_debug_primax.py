#!/usr/bin/env python3
"""
PRIMAX AI Debugger using Ollama
Uses qwen2.5-coder:0.5b model for debugging and fixing issues
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_ollama_query(prompt, model="qwen2.5-coder:0.5b"):
    """Run a query against Ollama model"""
    try:
        cmd = ["ollama", "run", model]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=prompt, timeout=60)
        
        if process.returncode == 0:
            return stdout.strip()
        else:
            print(f"❌ Ollama error: {stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Ollama timeout")
        return None
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return None

def analyze_codebase():
    """Analyze the PRIMAX codebase for issues"""
    
    print("🔍 Analyzing PRIMAX codebase...")
    
    # Check main issues
    issues = []
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        import sympy
        import numpy
    except ImportError as e:
        issues.append(f"Missing dependency: {e}")
    
    # Check brain module
    try:
        sys.path.insert(0, 'src')
        from brain import graph_connectivity, snn_activity_pattern, dynamic_systems_think
        print("✅ Brain module imports OK")
    except Exception as e:
        issues.append(f"Brain module error: {e}")
    
    # Check database connection
    try:
        import asyncpg
        print("✅ asyncpg available")
    except ImportError:
        issues.append("asyncpg not installed")
    
    # Check vault manager
    vault_issues = []
    try:
        from src.vault_manager import PrimaxVault
        vault = PrimaxVault()
        # Try to check if vault exists
        if not os.path.exists(vault.vault_file):
            vault_issues.append("Vault file does not exist")
        else:
            vault_issues.append("Vault file exists but may need password")
    except Exception as e:
        vault_issues.append(f"Vault manager error: {e}")
    
    return issues, vault_issues

def get_ollama_fixes(issues):
    """Get fixes from Ollama for identified issues"""
    
    if not issues:
        return []
    
    prompt = f"""
You are an expert Python developer debugging a FastAPI application called PRIMAX AI.

The following issues were found in the codebase:

{chr(10).join(f"- {issue}" for issue in issues)}

Please provide specific fixes for each issue. Format your response as:

ISSUE: [brief description]
FIX: [specific code changes or commands]
REASON: [why this fix works]

Separate each issue with a blank line.
"""
    
    response = run_ollama_query(prompt)
    if response:
        print("🤖 Ollama Analysis:")
        print(response)
        return response
    else:
        return []

def main():
    """Main debugging function"""
    
    print("🚀 PRIMAX AI Debugger with Ollama")
    print("=" * 50)
    
    # Analyze codebase
    issues, vault_issues = analyze_codebase()
    
    print(f"\n📊 Found {len(issues)} issues:")
    for issue in issues:
        print(f"  • {issue}")
    
    print(f"\n🔐 Vault issues: {len(vault_issues)}")
    for issue in vault_issues:
        print(f"  • {issue}")
    
    # Get Ollama fixes
    if issues:
        print("\n" + "=" * 50)
        get_ollama_fixes(issues)
    
    # Specific vault fix
    if vault_issues:
        print("\n" + "=" * 50)
        print("🔧 VAULT FIX SUGGESTIONS:")
        
        vault_prompt = """
The vault manager requires interactive password input, but we need programmatic access.

Current vault_manager.py uses:
    password = getpass.getpass("Enter vault password: ")

How can we modify it to work non-interactively? Provide a solution that:
1. Uses environment variable for password if available
2. Falls back to a default password for development
3. Maintains security for production

Show the specific code changes needed.
"""
        
        vault_fix = run_ollama_query(vault_prompt)
        if vault_fix:
            print("Vault Fix:")
            print(vault_fix)
    
    print("\n" + "=" * 50)
    print("✅ Analysis complete!")

if __name__ == "__main__":
    main()
