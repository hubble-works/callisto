import logging
from typing import Optional

import httpx

from app.services.github_app_auth import GitHubAppCredentials, GitHubAppAuthService

logger = logging.getLogger(__name__)


class GitHubAuthService:
    """Service for GitHub authentication using either personal token or GitHub App."""

    personal_token: Optional[str]
    app_auth_service: Optional[GitHubAppAuthService]

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        personal_token: Optional[str] = None,
        app_credentials: Optional[GitHubAppCredentials] = None,
    ):
        if personal_token and app_credentials:
            raise ValueError("Provide either personal_token or app_credentials, not both")
        if not personal_token and not app_credentials:
            raise ValueError("Either personal_token or app_credentials must be provided")

        self.personal_token = personal_token
        self.app_auth_service = None

        if app_credentials:
            self.app_auth_service = GitHubAppAuthService(app_credentials, http_client)

    async def get_auth_header(self, owner: Optional[str] = None, repo: Optional[str] = None) -> str:
        """Get GitHub API authorization header value."""
        if self.app_auth_service:
            if not owner or not repo:
                raise ValueError("owner and repo are required for GitHub App authentication")
            token = await self.app_auth_service.get_token_for_repo(owner, repo)
            if not token:
                raise ValueError(
                    f"GitHub App authentication failed for {owner}/{repo}. "
                    "Check app installation and permissions."
                )
            return f"Bearer {token}"

        if self.personal_token:
            return f"Bearer {self.personal_token}"

        raise ValueError("No valid authentication method available")
