"""
GitHub Sponsor Verification Module
Checks if a user is an active GitHub sponsor of kilisan
"""

import os
import httpx
import asyncio
from typing import Optional

GITHUB_API_URL = "https://api.github.com"
SPONSOR_USERNAME = "kilisan"
TIMEOUT = 10


async def verify_github_sponsor(github_username: str, github_token: Optional[str] = None) -> bool:
    """
    Verify if a GitHub user is an active sponsor.
    
    Args:
        github_username: GitHub username to check
        github_token: GitHub personal access token (optional, for higher rate limits)
    
    Returns:
        True if user is an active sponsor, False otherwise
    """
    if not github_token:
        github_token = os.getenv("GITHUB_TOKEN")
    
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        headers["Accept"] = "application/vnd.github.v3+json"
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Check if user sponsors kilisan
            response = await client.get(
                f"{GITHUB_API_URL}/users/{github_username}/sponsorships",
                headers=headers
            )
            
            if response.status_code == 200:
                sponsorships = response.json()
                for sponsorship in sponsorships:
                    if sponsorship.get("sponsor", {}).get("login") == SPONSOR_USERNAME:
                        return True
            return False
    except Exception as e:
        print(f"Error checking sponsor status: {e}")
        return False


def verify_github_sponsor_sync(github_username: str, github_token: Optional[str] = None) -> bool:
    """Synchronous wrapper for verify_github_sponsor"""
    return asyncio.run(verify_github_sponsor(github_username, github_token))


def require_sponsor(func):
    """Decorator to gate a function behind sponsor verification"""
    async def wrapper(*args, github_username: str, **kwargs):
        is_sponsor = await verify_github_sponsor(github_username)
        if not is_sponsor:
            raise PermissionError(
                f"This feature requires GitHub Sponsorship. "
                f"Become a sponsor: https://github.com/sponsors/{SPONSOR_USERNAME}"
            )
        return await func(*args, **kwargs)
    return wrapper


if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        username = sys.argv[1]
        is_sponsor = verify_github_sponsor_sync(username)
        print(f"Is {username} a sponsor of {SPONSOR_USERNAME}? {is_sponsor}")
