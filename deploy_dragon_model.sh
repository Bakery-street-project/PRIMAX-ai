#!/bin/bash
# Deploy PRIMAX Dragon Model

echo "🐉 Deploying PRIMAX Dragon Model..."

# 1. Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not installed"
    exit 1
fi

# 2. Start Ollama service
ollama serve &
sleep 5

# 3. Load dragon model (after fine-tuning)
echo "Loading PRIMAX-Dragon model..."
ollama create primax-dragon-coder:latest -f dragon_model_config.json

# 4. Test model
echo "Testing dragon model..."
echo "You are a wise dragon programmer. Explain recursion." | ollama run primax-dragon-coder:latest

echo "✅ Dragon model deployed!"
