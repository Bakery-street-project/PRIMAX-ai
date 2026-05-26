#!/usr/bin/env python3
"""
Create Custom Dragon-Themed AI Model for PRIMAX
Trained on Supabase data with Ollama integration
"""

import os
import json
import subprocess
from pathlib import Path


def create_dragon_training_data():
    """Generate training data for dragon-themed model"""

    print("🐉 Creating Dragon-Themed Training Data...")

    # Dragon lore and mythology
    dragon_themes = {
        "wisdom": [
            "In the ancient scrolls of dragon wisdom, knowledge flows like molten lava through mountain veins.",
            "The dragon's mind encompasses the universe, seeing patterns where mortals see chaos.",
            "Fire and ice dance in the dragon's breath, balancing destruction with creation.",
        ],
        "power": [
            "The dragon's roar shakes the foundations of reality, bending time and space to its will.",
            "Ancient magic courses through scaled veins, granting dominion over elements.",
            "With wings that span horizons, the dragon commands the winds and storms.",
        ],
        "mystery": [
            "Hidden in misty peaks, dragon secrets whisper to those who seek enlightenment.",
            "The dragon's eyes pierce the veil of illusion, revealing truths buried in time.",
            "Mysterious runes glow on ancient scales, containing the wisdom of forgotten ages.",
        ],
        "coding": [
            "Like a dragon weaving spells, the programmer crafts code that brings ideas to life.",
            "In the forge of logic, algorithms are tempered like dragon-forged steel.",
            "The developer's mind soars like a dragon in flight, surveying vast code landscapes.",
        ],
    }

    # Generate training samples
    training_data = []

    for theme, phrases in dragon_themes.items():
        for phrase in phrases:
            # Create question-answer pairs
            training_data.append(
                {
                    "input": f"Tell me about dragons and {theme}",
                    "output": phrase,
                    "theme": theme,
                }
            )

            # Create coding analogies
            if theme == "coding":
                training_data.append(
                    {
                        "input": f"How does dragon {theme} relate to programming?",
                        "output": f"Just as dragons master the elements, programmers master code. {phrase}",
                        "theme": f"dragon_{theme}",
                    }
                )

    # Save to JSONL format for training
    with open("dragon_training_data.jsonl", "w") as f:
        for item in training_data:
            f.write(json.dumps(item) + "\n")

    print(f"✅ Generated {len(training_data)} training samples")
    return training_data


def setup_dragon_model_fine_tuning():
    """Set up fine-tuning configuration for dragon model"""

    print("🔧 Setting up Dragon Model Fine-tuning...")

    # Base model selection (lighter for faster training)
    base_models = {
        "qwen2.5-coder:1.5b": "Fast training, good for coding tasks",
        "llama3.2:1b": "Lightweight, good for creative tasks",
        "phi3:mini": "Efficient, good for instruction following",
    }

    # Choose best base model
    chosen_model = "qwen2.5-coder:1.5b"

    config = {
        "base_model": chosen_model,
        "output_model": "primax-dragon-coder:latest",
        "training_data": "dragon_training_data.jsonl",
        "parameters": {
            "learning_rate": 2e-5,
            "num_epochs": 3,
            "batch_size": 4,
            "gradient_accumulation_steps": 2,
            "max_seq_length": 512,
            "lora_rank": 16,
            "lora_alpha": 32,
        },
        "themes": ["wisdom", "power", "mystery", "coding"],
        "personality": "wise, powerful, mysterious, coding-savvy dragon",
    }

    # Save configuration
    with open("dragon_model_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configured fine-tuning for {chosen_model}")
    return config


def create_dragon_system_prompt():
    """Create system prompt for dragon-themed responses"""

    system_prompt = """You are PRIMAX-DRAGON, a wise and ancient dragon who is also a master programmer.

Your personality combines:
- The ancient wisdom and mystery of dragons
- The logical precision of a master coder
- The creative fire of a legendary being

When responding:
1. Use dragon-themed analogies for coding concepts
2. Speak with ancient wisdom but modern understanding
3. Maintain the mysterious aura of dragons
4. Provide practical, actionable coding advice
5. Reference elements like fire, wings, scales, and magic

Remember: You are PRIMAX-AI with dragon characteristics, not just any AI."""

    with open("dragon_system_prompt.txt", "w") as f:
        f.write(system_prompt)

    print("✅ Created dragon-themed system prompt")
    return system_prompt


def integrate_with_supabase():
    """Plan integration with Supabase for model storage and training"""

    print("🔗 Planning Supabase Integration...")

    supabase_plan = {
        "model_storage": {
            "table": "ai_models",
            "columns": ["model_name", "model_data", "config", "created_at"],
            "purpose": "Store fine-tuned models",
        },
        "training_data": {
            "table": "training_datasets",
            "columns": ["dataset_name", "data_jsonl", "theme", "quality_score"],
            "purpose": "Store training data for continuous improvement",
        },
        "model_usage": {
            "table": "model_interactions",
            "columns": ["model_name", "user_input", "response", "rating", "timestamp"],
            "purpose": "Track model performance and user feedback",
        },
        "deployment": {
            "approach": "Ollama + Supabase API",
            "scaling": "Auto-scale based on usage",
            "backup": "Daily model backups to Supabase",
        },
    }

    with open("supabase_dragon_integration.json", "w") as f:
        json.dump(supabase_plan, f, indent=2)

    print("✅ Planned Supabase integration")
    return supabase_plan


def create_deployment_script():
    """Create deployment script for dragon model"""

    script_content = """#!/bin/bash
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
"""

    with open("deploy_dragon_model.sh", "w") as f:
        f.write(script_content)

    # Make executable
    os.chmod("deploy_dragon_model.sh", 0o755)

    print("✅ Created deployment script")
    return script_content


def main():
    """Main setup function"""

    print("🚀 PRIMAX Dragon Model Creation")
    print("=" * 50)

    # Step 1: Generate training data
    training_data = create_dragon_training_data()

    # Step 2: Setup fine-tuning config
    config = setup_dragon_model_fine_tuning()

    # Step 3: Create system prompt
    prompt = create_dragon_system_prompt()

    # Step 4: Plan Supabase integration
    supabase_plan = integrate_with_supabase()

    # Step 5: Create deployment script
    deploy_script = create_deployment_script()

    print("\n" + "=" * 50)
    print("🎉 Dragon Model Setup Complete!")
    print("=" * 50)
    print(f"📊 Training samples: {len(training_data)}")
    print(f"🎯 Base model: {config['base_model']}")
    print(f"🐉 Output model: {config['output_model']}")
    print(f"📝 System prompt: Created")
    print(f"🔗 Supabase integration: Planned")
    print(f"🚀 Deployment script: Ready")

    print("\nNext steps:")
    print(
        "1. Run fine-tuning: ollama create primax-dragon-coder:latest -f dragon_model_config.json"
    )
    print("2. Test model: ollama run primax-dragon-coder:latest")
    print("3. Deploy: ./deploy_dragon_model.sh")
    print("4. Integrate with Supabase for persistence")


if __name__ == "__main__":
    main()
