"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRIMAX AI - Nexus Agent Adapter                            ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-NEXUS-BSP-2025                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class AgentTask:
    name: str
    role: str
    capabilities: List[str]
    status: str = "idle"
    last_output: Optional[str] = None


class NexusAdapter:
    def __init__(self):
        self.agents: Dict[str, AgentTask] = {}

    def shutdown(self) -> None:
        return None

    def register_agent(self, name: str, role: str, capabilities: List[str]) -> None:
        self.agents[name] = AgentTask(name=name, role=role, capabilities=capabilities)

    async def dispatch_task(
        self, agent_name: str, task: str, context: Optional[Dict] = None
    ) -> Dict:
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found"}

        agent = self.agents[agent_name]
        agent.status = "active"

        try:
            result = await self._execute_task(agent, task, context or {})
            agent.status = "idle"
            agent.last_output = result
            return {"success": True, "result": result, "agent": agent_name}
        except Exception as e:
            agent.status = "error"
            return {"error": str(e), "agent": agent_name}

    async def _execute_task(self, agent: AgentTask, task: str, context: Dict) -> str:
        await asyncio.sleep(0)
        return self._run_agent_task(agent, task, context)

    def _run_agent_task(self, agent: AgentTask, task: str, context: Dict) -> str:
        if "scan" in agent.capabilities:
            return self._handle_scan_task(agent, task, context)
        elif "brain" in agent.capabilities or "research" in agent.capabilities:
            return self._handle_brain_task(agent, task, context)
        elif "code" in agent.capabilities or "analysis" in agent.capabilities:
            return self._handle_code_task(agent, task, context)
        return f"Agent {agent.name} executed task: {task}"

    def _handle_code_task(self, agent: AgentTask, task: str, context: Dict) -> str:
        if "generate" in task.lower():
            return f"[{agent.name}] Code generation requested: {task}"
        return f"[{agent.name}] Code task processed"

    def _handle_brain_task(self, agent: AgentTask, task: str, context: Dict) -> str:
        import numpy as np

        from brain.neuromorphic_core import (
            graph_connectivity,
            snn_activity_pattern,
            dynamic_systems_think,
            agent_recommendation,
        )

        task_lower = task.lower()

        if "graph" in task_lower or "connectivity" in task_lower:
            size = context.get("size", 20)
            eigenvalues = graph_connectivity(np.random.randint(0, 2, (size, size)))
            return f"[{agent.name}] Graph connectivity analysis: {len(eigenvalues)} eigenvalues computed"

        elif "snn" in task_lower or "spike" in task_lower:
            tmax = context.get("tmax", 100)
            activity = snn_activity_pattern(size=20, tmax=tmax)
            return f"[{agent.name}] SNN analysis: {sum(activity)} total spikes across neurons"

        elif "dynamic" in task_lower or "scaling" in task_lower:
            vm_output = context.get("vm_output", 100)
            _solution = dynamic_systems_think(vm_output)
            return f"[{agent.name}] Dynamic system analysis: scaling model solved"

        elif "recommendation" in task_lower:
            try:
                recommendation = agent_recommendation()
                return recommendation or f"[{agent.name}] Recommendation analysis completed"
            except Exception:
                return f"[{agent.name}] Recommendation analysis not available"

        return f"[{agent.name}] Brain task processed: {task}"

    def _handle_scan_task(self, agent: AgentTask, task: str, context: Dict) -> str:
        path = context.get("path", ".")
        path_obj = Path(path)

        if not path_obj.exists():
            return f"[{agent.name}] Path not found: {path}"

        files = list(path_obj.rglob("*.py"))
        return f"[{agent.name}] Scanned {len(files)} Python files in {path}"

    async def run_parallel_tasks(self, tasks: List[tuple]) -> List[Dict]:
        return await asyncio.gather(
            *[
                self.dispatch_task(agent_name, task, context or {})
                for agent_name, task, context in tasks
            ]
        )


def create_primax_agents() -> NexusAdapter:
    adapter = NexusAdapter()

    adapter.register_agent(
        "dragon-coder",
        "Senior Code Architect",
        ["code", "analysis", "generation", "refactoring"],
    )

    adapter.register_agent(
        "wisdom-brain",
        "Neuromorphic Researcher",
        ["brain", "research", "graph", "snn", "dynamic", "recommendation"],
    )

    adapter.register_agent(
        "scout-agent", "Codebase Explorer", ["scan", "analysis", "discovery"]
    )

    adapter.register_agent(
        "innovation-chaos",
        "Creative Problem Solver",
        ["innovation", "creative", "alternative"],
    )

    adapter.register_agent(
        "brain-spark", "Mathematical Intelligence", ["math", "calculation", "modeling"]
    )

    return adapter


async def main():
    adapter = create_primax_agents()
    try:
        print("=== PRIMAX Nexus Agent Demo ===")
        print("Agents registered:", list(adapter.agents.keys()))

        result = await adapter.dispatch_task(
            "wisdom-brain", "graph connectivity analysis", {"size": 10}
        )
        print("Graph analysis:", result)

        result = await adapter.dispatch_task(
            "wisdom-brain", "snn activity pattern", {"tmax": 50}
        )
        print("SNN analysis:", result)

        result = await adapter.dispatch_task(
            "scout-agent", "scan codebase", {"path": "/home/kilisan/primax-ai/src"}
        )
        print("Scan result:", result)
    finally:
        adapter.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
