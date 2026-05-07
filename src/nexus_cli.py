#!/usr/bin/env python3
"""
PRIMAX AI Nexus CLI.

This is a thin command-line boundary around the in-process Nexus adapter. It is
intentionally local-first: team files live in the target repository, while
agent routing and execution stay inside Primax AI.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _load_team_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Team file not found: {path}")

    try:
        import yaml  # type: ignore

        with path.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle) or {}
        if not isinstance(loaded, dict):
            raise ValueError("Team file must contain a mapping at the root")
        return loaded
    except ImportError:
        return _load_supported_yaml_subset(path)


def _load_supported_yaml_subset(path: Path) -> dict[str, Any]:
    """Parse the subset used by sentinel-team.yaml without a PyYAML dependency."""
    data: dict[str, Any] = {}
    current_section: str | None = None
    current_item: dict[str, Any] | None = None
    current_child_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped in {">", "|"}:
            continue

        indent = len(line) - len(line.lstrip(" "))

        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_section = key
            current_item = None
            current_child_key = None
            data[key] = _clean_scalar(value) if value.strip() else [] if key in {"agents", "workflows"} else ""
            continue

        if current_section in {"agents", "workflows"} and stripped.startswith("- "):
            body = stripped[2:]
            if ":" in body:
                key, value = body.split(":", 1)
                current_item = {key: _clean_scalar(value)}
                data.setdefault(current_section, []).append(current_item)
                current_child_key = None
            elif current_item is not None and current_child_key:
                current_item.setdefault(current_child_key, []).append(_clean_scalar(body))
            continue

        if current_item is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            if value.strip():
                current_item[key] = _clean_scalar(value)
                current_child_key = None
            else:
                current_item[key] = []
                current_child_key = key
            continue

        if current_item is not None and current_child_key and stripped.startswith("- "):
            current_item.setdefault(current_child_key, []).append(_clean_scalar(stripped[2:]))
            continue

        if current_section == "outputs" and ":" in stripped:
            if not isinstance(data.get("outputs"), dict):
                data["outputs"] = {}
            key, value = stripped.split(":", 1)
            data["outputs"][key] = _clean_scalar(value)

    return data


def _clean_scalar(value: str) -> str:
    return value.strip().strip("'\"")


async def _run_agent_task(agent: str, task: str, context: dict[str, Any] | None = None) -> int:
    from src.nexus_adapter import create_primax_agents

    adapter = create_primax_agents()
    try:
        result = await adapter.dispatch_task(agent, task, context or {})
        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("success") else 1
    finally:
        adapter.shutdown()


async def _run_team(args: argparse.Namespace) -> int:
    team_file = Path(args.team_file).expanduser().resolve()
    team = _load_team_file(team_file)
    root = Path(args.root).expanduser().resolve() if args.root else team_file.parent
    workflows = team.get("workflows", [])
    workflow_ids = [workflow.get("id") for workflow in workflows if isinstance(workflow, dict)]

    print(f"Nexus team: {team.get('name', team_file.stem)}")
    print(f"Root: {root}")
    print(f"Workflows: {', '.join(workflow_ids) if workflow_ids else 'none'}")

    if args.dry_run:
        return 0

    sentinel_script = root / "scripts" / "sentinel_integrity.sh"
    has_sentinel_step = any(
        "run_sentinel_integrity_script" in (workflow.get("steps") or [])
        for workflow in workflows
        if isinstance(workflow, dict)
    )

    if sentinel_script.exists() and has_sentinel_step:
        print(f"Running integrity script: {sentinel_script}")
        completed = subprocess.run(
            [str(sentinel_script), str(root)],
            cwd=str(root),
            text=True,
        )
        if completed.returncode != 0:
            return completed.returncode
    else:
        from src.nexus_adapter import create_primax_agents

        adapter = create_primax_agents()
        try:
            result = await adapter.dispatch_task(
                "scout-agent",
                "scan codebase",
                {"path": str(root / "src" if (root / "src").exists() else root)},
            )
            print(json.dumps(result, indent=2, default=str))
            if not result.get("success"):
                return 1
        finally:
            adapter.shutdown()

    output_target = (team.get("outputs") or {}).get("target") if isinstance(team.get("outputs"), dict) else None
    if output_target:
        print(f"Report target: {root / output_target}")
    return 0


def _list_agents() -> int:
    from src.nexus_adapter import create_primax_agents

    adapter = create_primax_agents()
    for agent in adapter.agents.values():
        print(f"{agent.name}\t{agent.role}\t{', '.join(agent.capabilities)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nexus", description="PRIMAX AI Nexus orchestration CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("agents", help="List available Nexus agents")

    task_parser = subparsers.add_parser("task", help="Dispatch one task to one Nexus agent")
    task_parser.add_argument("task", help="Task text to dispatch")
    task_parser.add_argument("--agent", default="wisdom-brain", help="Agent id to use")
    task_parser.add_argument("--path", help="Optional path context for scan tasks")

    run_parser = subparsers.add_parser("run", help="Run a Nexus team YAML file")
    run_parser.add_argument("team_file", help="Path to team YAML")
    run_parser.add_argument("--root", help="Repository root to run from")
    run_parser.add_argument("--dry-run", action="store_true", help="Parse and print workflow metadata only")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "agents":
        return _list_agents()
    if args.command == "task":
        context = {"path": args.path} if args.path else {}
        return asyncio.run(_run_agent_task(args.agent, args.task, context))
    if args.command == "run":
        return asyncio.run(_run_team(args))

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
