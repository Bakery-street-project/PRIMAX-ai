"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRIMAX AI - GitHub GraphQL Client                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-GRAPHQL-BSP-2025                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import urllib.request
import urllib.error
from urllib.parse import urlparse


@dataclass
class GraphQLRepo:
    id: str
    name: str
    owner: str
    description: Optional[str]
    primaryLanguage: Optional[str]
    stargazerCount: int
    forkCount: int
    issues: Dict[str, int]
    createdAt: str
    updatedAt: str
    diskUsage: int
    isPrivate: bool
    defaultBranchRef: str


@dataclass
class GraphQLOrg:
    org_name: str
    totalRepos: int
    repositories: List[GraphQLRepo]
    analyzedAt: str


class GitHubGraphQLClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.api_url = "https://api.github.com/graphql"

    def _make_request(self, query: str, variables: Optional[Dict] = None) -> Dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"bearer {self.token}"

        data = {"query": query, "variables": variables or {}}

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(data).encode(),
                headers=headers,
                method="POST",
            )
            parsed = urlparse(req.full_url if hasattr(req, 'full_url') else self.api_url)
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"Disallowed URL scheme: {parsed.scheme}")
            with urllib.request.urlopen(req, timeout=30) as response:  # nosec B310 - validated scheme
                return json.loads(response.read().decode())
        except urllib.error.URLError as e:
            return {"errors": [{"message": str(e)}]}

    def get_org_repos(self, org_name: str, first: int = 100) -> Optional[GraphQLOrg]:
        query = """
        query($orgName: String!, $first: Int!) {
          organization(login: $orgName) {
            name
            repositories(first: $first, ownerAffiliations: [OWNER], isHidden: false) {
              totalCount
              nodes {
                id
                name
                description
                primaryLanguage
                stargazerCount
                forkCount
                issues(first: 1) {
                  totalCount
                }
                createdAt
                updatedAt
                diskUsage
                isPrivate
                defaultBranchRef
              }
            }
          }
        }
        """

        result = self._make_request(query, {"orgName": org_name, "first": first})

        if "errors" in result:
            return None

        org_data = result.get("data", {}).get("organization")
        if not org_data:
            return None

        repos = []
        for node in org_data.get("repositories", {}).get("nodes", []):
            issues = node.get("issues", {})
            repos.append(
                GraphQLRepo(
                    id=node.get("id", ""),
                    name=node.get("name", ""),
                    owner=org_name,
                    description=node.get("description"),
                    primaryLanguage=node.get("primaryLanguage"),
                    stargazerCount=node.get("stargazerCount", 0),
                    forkCount=node.get("forkCount", 0),
                    issues=(
                        {"totalCount": issues.get("totalCount", 0)} if issues else {}
                    ),
                    createdAt=node.get("createdAt", ""),
                    updatedAt=node.get("updatedAt", ""),
                    diskUsage=node.get("diskUsage", 0),
                    isPrivate=node.get("isPrivate", False),
                    defaultBranchRef=node.get("defaultBranchRef", "main"),
                )
            )

        return GraphQLOrg(
            org_name=org_name,
            totalRepos=org_data.get("repositories", {}).get("totalCount", 0),
            repositories=repos,
            analyzedAt=datetime.now().isoformat(),
        )

    def get_repo_details(self, owner: str, name: str) -> Optional[GraphQLRepo]:
        query = """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            id
            name
            description
            primaryLanguage
            stargazerCount
            forkCount
            issues(first: 1) {
              totalCount
            }
            createdAt
            updatedAt
            diskUsage
            isPrivate
            defaultBranchRef
          }
        }
        """

        result = self._make_request(query, {"owner": owner, "name": name})

        if "errors" in result:
            return None

        node = result.get("data", {}).get("repository")
        if not node:
            return None

        issues = node.get("issues", {})
        return GraphQLRepo(
            id=node.get("id", ""),
            name=node.get("name", ""),
            owner=owner,
            description=node.get("description"),
            primaryLanguage=node.get("primaryLanguage"),
            stargazerCount=node.get("stargazerCount", 0),
            forkCount=node.get("forkCount", 0),
            issues={"totalCount": issues.get("totalCount", 0)} if issues else {},
            createdAt=node.get("createdAt", ""),
            updatedAt=node.get("updatedAt", ""),
            diskUsage=node.get("diskUsage", 0),
            isPrivate=node.get("isPrivate", False),
            defaultBranchRef=node.get("defaultBranchRef", "main"),
        )


def scan_github_org(org_name: str, token: Optional[str] = None) -> Dict[str, Any]:
    client = GitHubGraphQLClient(token)
    org_data = client.get_org_repos(org_name)

    if not org_data:
        return {"error": f"Could not fetch organization: {org_name}"}

    return {
        "org_name": org_data.org_name,
        "total_repos": org_data.totalRepos,
        "repositories": [
            {
                "name": r.name,
                "owner": r.owner,
                "description": r.description,
                "language": r.primaryLanguage,
                "stars": r.stargazerCount,
                "forks": r.forkCount,
                "issues": r.issues.get("totalCount", 0),
                "is_private": r.isPrivate,
            }
            for r in org_data.repositories
        ],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub GraphQL Client")
    parser.add_argument("org", help="Organization name")
    parser.add_argument("--token", help="GitHub token")
    args = parser.parse_args()

    result = scan_github_org(args.org, args.token)
    print(json.dumps(result, indent=2))
