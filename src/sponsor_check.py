"""
GitHub Sponsors verification for BoozeLee projects.

Usage:
    from src.sponsor_check import verify_github_sponsor, require_sponsor

    # Async check
    result = await verify_github_sponsor("username", github_token)
    # Returns: {"is_sponsor": True, "tier": "Pro Backer", "monthly_usd": 12}

    # Decorator
    @require_sponsor(min_tier_usd=12)
    async def premium_feature(username, token):
        ...
"""
import asyncio
import functools
import os
from typing import Optional

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    import urllib.request
    import json as _json

GRAPHQL_URL = "https://api.github.com/graphql"
SPONSOR_LOGIN = "BoozeLee"

TIER_MAP = {
    5:   "Community Supporter",
    12:  "Pro Backer",
    25:  "Gold Sponsor",
    50:  "Enterprise Partner",
    100: "Lifetime Supporter",
}

_QUERY = """
query CheckSponsor($login: String!) {
  user(login: $login) {
    isSponsoringViewer
    sponsorshipForViewerAsSponsoree {
      tier {
        monthlyPriceInDollars
        name
        isOneTime
      }
    }
  }
}
"""


async def verify_github_sponsor(username: str, token: Optional[str] = None) -> dict:
    """
    Check if `username` sponsors BoozeLee.

    Returns dict with keys:
        is_sponsor (bool)
        tier (str | None)
        monthly_usd (int)  — 0 if not sponsoring, 100 for one-time lifetime
    """
    token = token or os.getenv("GITHUB_TOKEN", "")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"query": _QUERY, "variables": {"login": username}}

    try:
        if AIOHTTP_AVAILABLE:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    GRAPHQL_URL, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    data = await resp.json()
        else:
            import json
            req = urllib.request.Request(
                GRAPHQL_URL,
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())

        user = data.get("data", {}).get("user", {}) or {}
        is_sponsor = bool(user.get("isSponsoringViewer", False))
        tier_data = user.get("sponsorshipForViewerAsSponsoree") or {}
        tier_node = tier_data.get("tier") or {}
        monthly_usd = tier_node.get("monthlyPriceInDollars", 0)
        tier_name = tier_node.get("name") or TIER_MAP.get(monthly_usd, "Unknown")

        return {
            "is_sponsor": is_sponsor,
            "tier": tier_name if is_sponsor else None,
            "monthly_usd": monthly_usd if is_sponsor else 0,
            "is_lifetime": bool(tier_node.get("isOneTime", False)),
        }

    except Exception as exc:
        return {"is_sponsor": False, "tier": None, "monthly_usd": 0, "error": str(exc)}


def verify_github_sponsor_sync(username: str, token: Optional[str] = None) -> dict:
    """Synchronous wrapper around verify_github_sponsor."""
    return asyncio.run(verify_github_sponsor(username, token))


def require_sponsor(min_tier_usd: int = 5):
    """
    Decorator factory. Raises PermissionError if caller is not a sponsor at the
    required tier or above.

    The decorated function must accept `username` and `token` as first two args.

    Example:
        @require_sponsor(min_tier_usd=12)
        async def pro_feature(username, token, *args, **kwargs): ...
    """
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(username: str, token: str, *args, **kwargs):
            result = await verify_github_sponsor(username, token)
            if not result["is_sponsor"]:
                raise PermissionError(
                    f"This feature requires a GitHub Sponsors subscription at "
                    f"${min_tier_usd}/mo or higher. "
                    f"Become a sponsor: https://github.com/sponsors/{SPONSOR_LOGIN}"
                )
            if result["monthly_usd"] < min_tier_usd and not result.get("is_lifetime"):
                tier_needed = TIER_MAP.get(min_tier_usd, f"${min_tier_usd}/mo")
                raise PermissionError(
                    f"This feature requires the '{tier_needed}' tier or above "
                    f"(${min_tier_usd}/mo). Upgrade: https://github.com/sponsors/{SPONSOR_LOGIN}"
                )
            return await fn(username, token, *args, **kwargs)
        return wrapper
    return decorator
