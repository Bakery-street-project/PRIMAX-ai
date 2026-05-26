"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRIMAX AI - GitHub Webhook Listener                        ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-WEBHOOK-BSP-2025                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import hashlib
import hmac
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from aiohttp import web


@dataclass
class WebhookEvent:
    event_type: str
    delivery_id: str
    timestamp: str
    payload: Dict[str, Any]
    signature: Optional[str] = None


class GitHubWebhookHandler:
    def __init__(self, secret: Optional[str] = None):
        self.secret = secret or os.environ.get("GITHUB_WEBHOOK_SECRET")
        self.handlers: Dict[str, Callable] = {}
        self.events: list = []

    def register_handler(self, event_type: str, handler: Callable) -> None:
        self.handlers[event_type] = handler

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        if not self.secret:
            return True

        expected = hmac.new(self.secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    async def handle_webhook(self, request: web.Request) -> web.Response:
        event_type = request.headers.get("X-GitHub-Event", "ping")
        delivery_id = request.headers.get("X-GitHub-Delivery", "")
        signature = request.headers.get("X-Hub-Signature-256")

        payload = await request.read()

        if self.secret and not self.verify_signature(payload, signature):
            return web.Response(status=401, text="Invalid signature")

        try:
            data = json.loads(payload.decode())
        except json.JSONDecodeError:
            return web.Response(status=400, text="Invalid JSON")

        event = WebhookEvent(
            event_type=event_type,
            delivery_id=delivery_id,
            timestamp=datetime.now().isoformat(),
            payload=data,
            signature=signature,
        )

        self.events.append(event)

        if event_type in self.handlers:
            await self.handlers[event_type](event)

        return web.Response(text="OK")

    async def handle_push(self, event: WebhookEvent) -> None:
        repo = event.payload.get("repository", {}).get("full_name", "unknown")
        commits = event.payload.get("commits", [])
        branch = event.payload.get("ref", "").replace("refs/heads/", "")

        print(f"[PUSH] {repo}:{branch} - {len(commits)} commits")

        for commit in commits:
            print(f"  - {commit.get('message', 'N/A')[:50]}")

    async def handle_issues(self, event: WebhookEvent) -> None:
        action = event.payload.get("action", "opened")
        issue = event.payload.get("issue", {})
        repo = event.payload.get("repository", {}).get("full_name", "unknown")

        print(f"[ISSUE] {action} ({repo}): #{issue.get('number')} - {issue.get('title')}")

    async def handle_pull_request(self, event: WebhookEvent) -> None:
        action = event.payload.get("action", "opened")
        pr = event.payload.get("pull_request", {})
        repo = event.payload.get("repository", {}).get("full_name", "unknown")

        print(f"[PR] {action} ({repo}): #{pr.get('number')} - {pr.get('title')}")

        if action == "opened":
            await self._review_pr(event)

    async def _review_pr(self, event: WebhookEvent) -> None:
        pr = event.payload.get("pull_request", {})
        repo = event.payload.get("repository", {}).get("full_name", "")
        _head_sha = pr.get("head", {}).get("sha")

        print(f"  -> Would auto-review PR #{pr.get('number')} for {repo}")

    def get_recent_events(self, limit: int = 50) -> list:
        return self.events[-limit:]


async def create_app(secret: Optional[str] = None) -> web.Application:
    handler = GitHubWebhookHandler(secret)

    handler.register_handler("push", handler.handle_push)
    handler.register_handler("issues", handler.handle_issues)
    handler.register_handler("pull_request", handler.handle_pull_request)

    app = web.Application()
    app.router.add_post("/webhook", handler.handle_webhook)
    app.router.add_get("/health", lambda r: web.Response(text="OK"))

    return app


def run_server(port: int = 8080, secret: Optional[str] = None) -> None:
    app = asyncio.run(create_app(secret))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub Webhook Listener")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--secret", help="Webhook secret")
    args = parser.parse_args()

    run_server(args.port, args.secret)
