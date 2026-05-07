#!/bin/bash
# PRIMAX AI Supabase Deployment

echo "🚀 Deploying PRIMAX AI to Supabase..."

# Check requirements
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 required"
    exit 1
fi

if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama required" 
    exit 1
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install fastapi uvicorn supabase requests --quiet

# Check models
echo "🔍 Checking models..."
python3 -c "
import subprocess
result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
print('Available models:')
for line in result.stdout.split('
')[1:]:
    if line.strip():
        print(' ', line.split()[0])
"

# Run API
echo "🌐 Starting PRIMAX API..."
echo "API will be available at http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

python primax_api_supabase.py
