"""Dependency injection providers for FastAPI."""

from functools import lru_cache
from typing import Optional

from app.config import Settings
from app.services.ai_service import AIService
from app.services.github_client import GitHubClient
from app.services.github_app_auth import GitHubAppAuth


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (singleton)."""
    return Settings()


@lru_cache()
def get_github_app_auth() -> Optional[GitHubAppAuth]:
    """Get GitHub App auth instance (singleton)."""
    settings = get_settings()

    if not settings.github_app_id:
        return None

    # Load private key from file or environment variable
    if settings.github_app_private_key_path:
        return GitHubAppAuth.from_key_path(
            settings.github_app_id, settings.github_app_private_key_path
        )
    elif settings.github_app_private_key:
        return GitHubAppAuth(settings.github_app_id, settings.github_app_private_key)

    return None


@lru_cache()
def get_github_client() -> GitHubClient:
    """Get GitHub client instance (singleton)."""
    settings = get_settings()
    app_auth = get_github_app_auth()

    # Prioritize GitHub App authentication if available
    return GitHubClient(token=settings.github_token, app_auth=app_auth)


@lru_cache()
def get_ai_service() -> AIService:
    """Get AI service instance (singleton)."""
    settings = get_settings()
    return AIService(settings.ai_api_key, settings.ai_model, settings.ai_base_url)
