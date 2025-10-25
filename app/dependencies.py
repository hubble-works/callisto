"""Dependency injection providers for FastAPI."""

from functools import lru_cache
from typing import Optional

import httpx

from app.config import Settings
from app.services.ai_service import AIService
from app.services.github_client import GitHubClient
from app.services.github_auth import GitHubAuthService
from app.services.github_app_auth import GitHubAppCredentials


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (singleton)."""
    return Settings()


@lru_cache()
def get_http_client() -> httpx.AsyncClient:
    """Get HTTP client instance (singleton)."""
    return httpx.AsyncClient()


@lru_cache()
def get_github_app_credentials() -> Optional[GitHubAppCredentials]:
    """Get GitHub App credentials instance (singleton)."""
    settings = get_settings()

    if not settings.github_app_id:
        return None

    # Load private key from file or environment variable
    if settings.github_app_private_key_path:
        return GitHubAppCredentials.from_key_path(
            settings.github_app_id, settings.github_app_private_key_path
        )
    elif settings.github_app_private_key:
        return GitHubAppCredentials(
            app_id=settings.github_app_id, private_key=settings.github_app_private_key
        )

    return None


@lru_cache()
def get_github_auth_service() -> GitHubAuthService:
    """Get GitHub auth service instance (singleton)."""
    settings = get_settings()
    http_client = get_http_client()
    app_credentials = get_github_app_credentials()

    return GitHubAuthService(
        http_client=http_client,
        personal_token=settings.github_token,
        app_credentials=app_credentials,
    )


@lru_cache()
def get_github_client() -> GitHubClient:
    """Get GitHub client instance (singleton)."""
    http_client = get_http_client()
    auth_service = get_github_auth_service()

    return GitHubClient(http_client=http_client, auth_service=auth_service)


@lru_cache()
def get_ai_service() -> AIService:
    """Get AI service instance (singleton)."""
    settings = get_settings()
    return AIService(settings.ai_api_key, settings.ai_model, settings.ai_base_url)
