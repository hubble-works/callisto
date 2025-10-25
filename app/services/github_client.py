import logging
from typing import List, Optional, Dict, Any

import httpx
from pydantic import BaseModel

from app.services.github_app_auth import GitHubAppAuth

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
    base_url: str = "https://api.github.com"
    token: Optional[str]
    app_auth: Optional[GitHubAppAuth]

    def __init__(self, token: Optional[str] = None, app_auth: Optional[GitHubAppAuth] = None):
        if not token and not app_auth:
            raise ValueError("Either token or app_auth must be provided")

        self.token = token
        self.app_auth = app_auth

    async def _get_headers(
        self, owner: Optional[str] = None, repo: Optional[str] = None
    ) -> Dict[str, str]:
        """Get headers with appropriate authorization."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        if self.app_auth and owner and repo:
            # Use GitHub App authentication
            token = await self.app_auth.get_token_for_repo(owner, repo)
            if token:
                headers["Authorization"] = f"Bearer {token}"
                return headers
            logger.warning(
                f"Failed to get GitHub App token for {owner}/{repo}, falling back to personal token"
            )

        # Fall back to personal access token
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        else:
            raise ValueError("No valid authentication method available")

        return headers

    async def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> List[CodeDiff]:
        """Get the diff files for a pull request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        headers = await self._get_headers(owner, repo)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
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

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
