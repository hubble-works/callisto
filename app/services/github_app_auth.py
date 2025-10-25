import time
import logging
import httpx
import jwt
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class GitHubAppAuth:
    """Handles GitHub App authentication and installation access tokens."""

    def __init__(self, app_id: str, private_key: str):
        self.app_id = app_id
        self.private_key = private_key
        self._installation_tokens: Dict[int, Dict[str, Any]] = {}

    @classmethod
    def from_key_path(cls, app_id: str, private_key_path: str) -> "GitHubAppAuth":
        """Create GitHubAppAuth from a private key file path."""
        key_file = Path(private_key_path)
        if not key_file.exists():
            raise FileNotFoundError(f"Private key file not found: {private_key_path}")
        private_key = key_file.read_text()
        return cls(app_id, private_key)

    def generate_jwt(self) -> str:
        """Generate a JWT for authenticating as the GitHub App."""
        now = int(time.time())
        payload = {
            "iat": now - 60,  # Issued at time (60 seconds in the past to account for clock drift)
            "exp": now + 600,  # JWT expiration (10 minutes)
            "iss": self.app_id,  # GitHub App's identifier
        }

        return jwt.encode(payload, self.private_key, algorithm="RS256")

    async def get_installation_id(self, owner: str, repo: str) -> Optional[int]:
        """Get the installation ID for a specific repository."""
        jwt_token = self.generate_jwt()
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        url = f"https://api.github.com/repos/{owner}/{repo}/installation"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return int(data.get("id")) if data.get("id") else None
            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to get installation ID for {owner}/{repo}: {e}")
                return None

    async def get_installation_access_token(self, installation_id: int) -> Optional[str]:
        """Get an installation access token for the GitHub App."""
        # Check if we have a cached token that's still valid
        cached = self._installation_tokens.get(installation_id)
        if cached and cached["expires_at"] > time.time() + 60:  # 60 second buffer
            return str(cached["token"])

        jwt_token = self.generate_jwt()
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                token = str(data["token"])
                expires_at = data["expires_at"]

                # Cache the token
                self._installation_tokens[installation_id] = {
                    "token": token,
                    "expires_at": time.mktime(time.strptime(expires_at, "%Y-%m-%dT%H:%M:%SZ")),
                }

                return token
            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to get installation access token: {e}")
                return None

    async def get_token_for_repo(self, owner: str, repo: str) -> Optional[str]:
        """Get an installation access token for a specific repository."""
        installation_id = await self.get_installation_id(owner, repo)
        if not installation_id:
            return None

        return await self.get_installation_access_token(installation_id)
