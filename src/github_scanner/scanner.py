"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRIMAX AI - GitHub Scanner                                 ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-SCANNER-BSP-2025                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import subprocess
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("primax-github-scanner")


@dataclass
class RepoAnalysis:
    """Repository analysis result"""
    name: str
    owner: str
    description: Optional[str]
    language: Optional[str]
    stars: int
    forks: int
    open_issues: int
    created_at: str
    updated_at: str
    topics: List[str] = field(default_factory=list)
    is_private: bool = False
    default_branch: str = "main"
    size_kb: int = 0
    has_wiki: bool = False
    has_issues: bool = False
    license: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "owner": self.owner,
            "full_name": f"{self.owner}/{self.name}",
            "description": self.description,
            "language": self.language,
            "stars": self.stars,
            "forks": self.forks,
            "open_issues": self.open_issues,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "topics": self.topics,
            "is_private": self.is_private,
            "default_branch": self.default_branch,
            "size_kb": self.size_kb,
            "has_wiki": self.has_wiki,
            "has_issues": self.has_issues,
            "license": self.license
        }


@dataclass
class OrgAnalysis:
    """Organization-wide analysis result"""
    org_name: str
    total_repos: int
    public_repos: int
    private_repos: int
    total_stars: int
    total_forks: int
    languages: Dict[str, int] = field(default_factory=dict)
    topics: Dict[str, int] = field(default_factory=dict)
    repositories: List[RepoAnalysis] = field(default_factory=list)
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "org_name": self.org_name,
            "total_repos": self.total_repos,
            "public_repos": self.public_repos,
            "private_repos": self.private_repos,
            "total_stars": self.total_stars,
            "total_forks": self.total_forks,
            "languages": self.languages,
            "topics": self.topics,
            "top_languages": sorted(
                self.languages.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "top_topics": sorted(
                self.topics.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20],
            "repositories": [r.to_dict() for r in self.repositories],
            "analyzed_at": self.analyzed_at
        }


class GitHubScanner:
    """Scanner for GitHub repositories and organizations"""

    def __init__(self):
        self.gh_available = self._check_gh_cli()

    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is available and authenticated"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"GitHub CLI not available: {e}")
            return False

    def _run_gh_command(self, args: List[str]) -> Optional[str]:
        """Run GitHub CLI command"""
        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"GH command failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"GH command error: {e}")
            return None

    def analyze_repo(self, repo_full_name: str) -> Optional[RepoAnalysis]:
        """
        Analyze a single repository

        Args:
            repo_full_name: Full repo name (owner/repo)

        Returns:
            RepoAnalysis or None if failed
        """
        if not self.gh_available:
            raise RuntimeError("GitHub CLI not available or not authenticated")

        # Get repo info using gh API
        output = self._run_gh_command([
            "repo", "view", repo_full_name, "--json",
            "name,owner,description,primaryLanguage,stargazerCount,forkCount,"
            "openIssues,createdAt,updatedAt,repositoryTopics,isPrivate,"
            "defaultBranchRef,diskUsage,hasWikiEnabled,hasIssuesEnabled,licenseInfo"
        ])

        if not output:
            return None

        try:
            data = json.loads(output)

            return RepoAnalysis(
                name=data.get("name", ""),
                owner=data.get("owner", {}).get("login", ""),
                description=data.get("description"),
                language=data.get("primaryLanguage", {}).get("name") if data.get("primaryLanguage") else None,
                stars=data.get("stargazerCount", 0),
                forks=data.get("forkCount", 0),
                open_issues=data.get("openIssues", {}).get("totalCount", 0) if isinstance(data.get("openIssues"), dict) else 0,
                created_at=data.get("createdAt", ""),
                updated_at=data.get("updatedAt", ""),
                topics=[t.get("name", "") for t in data.get("repositoryTopics", {}).get("nodes", [])],
                is_private=data.get("isPrivate", False),
                default_branch=data.get("defaultBranchRef", {}).get("name", "main"),
                size_kb=data.get("diskUsage", 0),
                has_wiki=data.get("hasWikiEnabled", False),
                has_issues=data.get("hasIssuesEnabled", False),
                license=data.get("licenseInfo", {}).get("name") if data.get("licenseInfo") else None
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse repo data: {e}")
            return None

    def list_org_repos(self, org_name: str, limit: int = 100) -> List[str]:
        """
        List all repositories in an organization

        Args:
            org_name: Organization name
            limit: Maximum number of repos to list

        Returns:
            List of repo full names (owner/repo)
        """
        if not self.gh_available:
            raise RuntimeError("GitHub CLI not available or not authenticated")

        output = self._run_gh_command([
            "repo", "list", org_name,
            "--limit", str(limit),
            "--json", "nameWithOwner"
        ])

        if not output:
            return []

        try:
            repos = json.loads(output)
            return [r["nameWithOwner"] for r in repos]
        except json.JSONDecodeError:
            return []

    def analyze_organization(
        self,
        org_name: str,
        limit: Optional[int] = None
    ) -> Optional[OrgAnalysis]:
        """
        Analyze entire organization

        Args:
            org_name: Organization name
            limit: Maximum number of repos to analyze

        Returns:
            OrgAnalysis or None if failed
        """
        if not self.gh_available:
            raise RuntimeError("GitHub CLI not available or not authenticated")

        # Get list of repos
        repo_names = self.list_org_repos(org_name, limit or 100)

        if not repo_names:
            return None

        # Analyze each repo
        repositories: List[RepoAnalysis] = []
        languages: Dict[str, int] = {}
        topics: Dict[str, int] = {}
        total_stars = 0
        total_forks = 0
        public_count = 0
        private_count = 0

        for repo_name in repo_names:
            logger.info(f"Analyzing {repo_name}...")
            repo_analysis = self.analyze_repo(repo_name)

            if repo_analysis:
                repositories.append(repo_analysis)

                # Aggregate stats
                total_stars += repo_analysis.stars
                total_forks += repo_analysis.forks

                if repo_analysis.is_private:
                    private_count += 1
                else:
                    public_count += 1

                # Count languages
                if repo_analysis.language:
                    languages[repo_analysis.language] = languages.get(repo_analysis.language, 0) + 1

                # Count topics
                for topic in repo_analysis.topics:
                    topics[topic] = topics.get(topic, 0) + 1

        return OrgAnalysis(
            org_name=org_name,
            total_repos=len(repositories),
            public_repos=public_count,
            private_repos=private_count,
            total_stars=total_stars,
            total_forks=total_forks,
            languages=languages,
            topics=topics,
            repositories=repositories
        )

    def search_repos(
        self,
        query: str,
        limit: int = 20
    ) -> List[RepoAnalysis]:
        """
        Search for repositories

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of RepoAnalysis
        """
        if not self.gh_available:
            raise RuntimeError("GitHub CLI not available or not authenticated")

        output = self._run_gh_command([
            "search", "repos", query,
            "--limit", str(limit),
            "--json", "nameWithOwner"
        ])

        if not output:
            return []

        try:
            results = json.loads(output)
            repos = []

            for result in results:
                repo_name = result.get("nameWithOwner")
                if repo_name:
                    repo_analysis = self.analyze_repo(repo_name)
                    if repo_analysis:
                        repos.append(repo_analysis)

            return repos

        except json.JSONDecodeError:
            return []
