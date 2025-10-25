import logging
from typing import List, Optional, Dict, Any

import httpx
from pydantic import BaseModel

from app.services.github_auth import GitHubAuthService

logger = logging.getLogger(__name__)


class PullRequestEvent(BaseModel):
    """GitHub Pull Request webhook event."""

    action: str
    number: int
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]


class ReviewComment(BaseModel):
    """A review comment to post on a pull request."""

    path: str
    position: Optional[int] = None
    body: str
    line: Optional[int] = None
    side: str = "RIGHT"  # LEFT or RIGHT
    start_line: Optional[int] = None
    start_side: Optional[str] = None


class CodeDiff(BaseModel):
    """Represents a code diff."""

    filename: str
    status: str  # added, removed, modified
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None


class GitHubClient:
    """Client for interacting with GitHub API."""

    base_url: str
    http_client: httpx.AsyncClient
    auth_service: GitHubAuthService

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        auth_service: GitHubAuthService,
    ):
        self.base_url = "https://api.github.com"
        self.http_client = http_client
        self.auth_service = auth_service

    async def _get_headers(self, owner: str, repo: str) -> Dict[str, str]:
        """Get standard GitHub API headers with authorization."""
        return {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": await self.auth_service.get_auth_header(owner, repo),
        }

    async def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> List[CodeDiff]:
        """Get the diff files for a pull request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        headers = await self._get_headers(owner, repo)

        response = await self.http_client.get(url, headers=headers)
        response.raise_for_status()
        files = response.json()

        return [
            CodeDiff(
                filename=file["filename"],
                status=file["status"],
                additions=file["additions"],
                deletions=file["deletions"],
                changes=file["changes"],
                patch=file.get("patch"),
            )
            for file in files
        ]

    async def post_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        comments: List[ReviewComment],
        event: str = "COMMENT",
    ):
        """Post a review with comments on a pull request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        headers = await self._get_headers(owner, repo)

        # Format comments for GitHub API
        formatted_comments = [
            {"path": comment.path, "body": comment.body, "line": comment.line, "side": comment.side}
            for comment in comments
        ]

        payload = {"event": event, "comments": formatted_comments}

        response = await self.http_client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
