#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                PRIMAX-AI Natural Language Interface (NLP-CLI)                 ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-NLP-BSP-2025                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Natural Language Interface for AutomationCodex

Usage:
  primax automate <task_description>

Examples:
  primax automate creating an AI art generator platform with website
  primax automate build a REST API for weather data
  primax automate deploy secure authentication system
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Add Smoothoperator to path
sys.path.append(str(Path(__file__).parent.parent / "Smoothoperator" / "src"))

try:
    from dream_script_engine import DreamScriptEngineSingularity

    DSE_AVAILABLE = True
except:
    DSE_AVAILABLE = False
    print("⚠️  Dream Script Engine not available - using fallback mode")


class PRIMAXNLPInterface:
    """
    Natural Language Parser for PRIMAX AutomationCodex

    Converts: "create an AI art generator platform"
    Into: Task graph with optimal agent assignments
    """

    def __init__(self):
        self.watermark = "PRIMAX-AI-NLP-BSP-2025"

        # Agent capabilities (from AutomationCodex)
        self.agents = {
            "coder": {
                "skills": ["api", "backend", "frontend", "database", "web", "app"],
                "languages": ["python", "javascript", "go", "rust", "typescript"],
                "frameworks": ["fastapi", "react", "nextjs", "django", "flask"],
            },
            "researcher": {
                "skills": ["arxiv", "papers", "research", "analysis", "investigation"],
                "domains": ["ai", "ml", "quantum", "neuromorphic", "blockchain"],
            },
            "deployer": {
                "skills": ["deploy", "cloud", "docker", "kubernetes", "ci/cd"],
                "platforms": ["render", "railway", "fly", "vercel", "netlify"],
            },
            "security": {
                "skills": ["encryption", "auth", "vault", "keys", "permissions"],
                "methods": ["aes", "rsa", "jwt", "oauth", "2fa"],
            },
            "designer": {
                "skills": ["ui", "ux", "art", "graphics", "website", "interface"],
                "tools": ["tailwind", "chakra", "figma", "canvas"],
            },
        }

        # Task keywords (for graph theory routing)
        self.task_patterns = {
            "create": ["build", "make", "generate", "develop", "code"],
            "deploy": ["ship", "publish", "release", "launch", "host"],
            "secure": ["encrypt", "protect", "auth", "lock", "vault"],
            "research": ["analyze", "investigate", "study", "explore"],
            "design": ["ui", "ux", "website", "interface", "art", "graphics"],
        }

        if DSE_AVAILABLE:
            self.dream_engine = DreamScriptEngineSingularity()
        else:
            self.dream_engine = None

    def parse(self, command: str) -> Dict[str, Any]:
        """Parse natural language command into task graph"""

        print(f"🧠 Parsing: {command}")

        # Extract task components
        task_type = self._detect_task_type(command)
        agents_needed = self._select_agents(command)
        technologies = self._extract_technologies(command)
        complexity = self._estimate_complexity(command)

        # Build task graph using AutomationCodex
        task_graph = {
            "task_id": f"primax_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "original_command": command,
            "task_type": task_type,
            "agents": agents_needed,
            "technologies": technologies,
            "complexity": complexity,
            "watermark": self.watermark,
            "steps": self._generate_execution_steps(task_type, agents_needed, command),
        }

        return task_graph

    def _detect_task_type(self, command: str) -> str:
        """Detect primary task type"""
        command_lower = command.lower()

        for task_type, keywords in self.task_patterns.items():
            if any(kw in command_lower for kw in keywords):
                return task_type

        return "create"  # Default

    def _select_agents(self, command: str) -> List[str]:
        """Select optimal agents using graph theory"""
        command_lower = command.lower()
        selected = []

        for agent_name, agent_spec in self.agents.items():
            # Check if agent skills match command keywords
            skill_match = any(skill in command_lower for skill in agent_spec["skills"])

            if skill_match:
                selected.append(agent_name)

        # Always include coder for building tasks
        if "create" in command_lower or "build" in command_lower:
            if "coder" not in selected:
                selected.append("coder")

        return selected if selected else ["coder"]  # Fallback

    def _extract_technologies(self, command: str) -> List[str]:
        """Extract mentioned technologies"""
        tech_keywords = {
            "python",
            "javascript",
            "react",
            "nextjs",
            "fastapi",
            "django",
            "docker",
            "kubernetes",
            "postgres",
            "mongodb",
            "redis",
            "ai",
            "ml",
            "neural",
            "blockchain",
            "solana",
            "ethereum",
        }

        command_lower = command.lower()
        found = [tech for tech in tech_keywords if tech in command_lower]

        # Infer from context
        if "website" in command_lower or "web" in command_lower:
            found.extend(["react", "tailwind"])
        if "api" in command_lower:
            found.append("fastapi")
        if "art" in command_lower or "image" in command_lower:
            found.extend(["canvas", "pillow"])

        return list(set(found))

    def _estimate_complexity(self, command: str) -> str:
        """Estimate task complexity"""
        word_count = len(command.split())
        agent_count = len(self._select_agents(command))
        tech_count = len(self._extract_technologies(command))

        score = word_count + (agent_count * 10) + (tech_count * 5)

        if score < 20:
            return "simple"
        elif score < 50:
            return "moderate"
        else:
            return "complex"

    def _generate_execution_steps(
        self, task_type: str, agents: List[str], command: str
    ) -> List[Dict]:
        """Generate execution steps using AutomationCodex logic"""

        steps = []
        step_counter = 1

        # Step 1: Research phase (if researcher agent involved)
        if "researcher" in agents:
            steps.append(
                {
                    "step": step_counter,
                    "agent": "researcher",
                    "action": "research_requirements",
                    "description": f"Research best practices for: {command}",
                    "estimated_time": "5 minutes",
                }
            )
            step_counter += 1

        # Step 2: Design phase (if designer agent involved)
        if "designer" in agents:
            steps.append(
                {
                    "step": step_counter,
                    "agent": "designer",
                    "action": "create_design",
                    "description": "Design UI/UX and system architecture",
                    "estimated_time": "10 minutes",
                }
            )
            step_counter += 1

        # Step 3: Coding phase
        if "coder" in agents:
            steps.append(
                {
                    "step": step_counter,
                    "agent": "coder",
                    "action": "implement",
                    "description": f"Implement: {command}",
                    "estimated_time": "30 minutes",
                }
            )
            step_counter += 1

        # Step 4: Security phase (if security agent involved)
        if "security" in agents:
            steps.append(
                {
                    "step": step_counter,
                    "agent": "security",
                    "action": "secure_system",
                    "description": "Add authentication, encryption, and security measures",
                    "estimated_time": "15 minutes",
                }
            )
            step_counter += 1

        # Step 5: Deployment phase
        if "deployer" in agents or task_type == "deploy":
            steps.append(
                {
                    "step": step_counter,
                    "agent": "deployer",
                    "action": "deploy",
                    "description": "Deploy to cloud (Render/Railway)",
                    "estimated_time": "10 minutes",
                }
            )
            step_counter += 1

        return steps

    def execute(self, task_graph: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task using Dream Script Engine"""

        print(f"\n🚀 Executing Task: {task_graph['task_id']}")
        print(f"   Type: {task_graph['task_type']}")
        print(f"   Agents: {', '.join(task_graph['agents'])}")
        print(f"   Complexity: {task_graph['complexity']}")
        print(f"\n📋 Execution Plan:")

        for step in task_graph["steps"]:
            print(f"   [{step['step']}] {step['agent']}: {step['description']}")

        if self.dream_engine:
            print(f"\n🔮 Invoking Dream Script Engine...")
            result = self.dream_engine.generate_script(task_graph["original_command"])
            return result
        else:
            print(f"\n⚠️  Dream Script Engine unavailable - manual execution required")
            return {
                "status": "pending",
                "task_graph": task_graph,
                "message": "Task graph generated - requires manual execution",
            }


def main():
    """CLI Entry Point"""

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       PRIMAX-AI Natural Language Interface v1.0.0            ║")
    print("║       Watermark: PRIMAX-AI-NLP-BSP-2025                      ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    if len(sys.argv) < 3 or sys.argv[1] != "automate":
        print("Usage: primax automate <task_description>")
        print("\nExamples:")
        print("  primax automate creating an AI art generator platform")
        print("  primax automate build REST API for weather data")
        print("  primax automate deploy secure authentication system")
        sys.exit(1)

    # Get command from args
    command = " ".join(sys.argv[2:])

    # Initialize NLP interface
    nlp = PRIMAXNLPInterface()

    # Parse command
    task_graph = nlp.parse(command)

    # Execute task
    result = nlp.execute(task_graph)

    # Save task graph
    output_file = f"task_{task_graph['task_id']}.json"
    with open(output_file, "w") as f:
        json.dump(task_graph, f, indent=2)

    print(f"\n✅ Task graph saved: {output_file}")
    print(f"   Watermark: {task_graph['watermark']}")


if __name__ == "__main__":
    main()
