"""Dependency injection providers for FastAPI."""

from functools import lru_cache

from app.config import Settings
from app.services.ai_service import AIService
from app.services.github_client import GitHubClient


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (singleton)."""
    return Settings()


@lru_cache()
def get_github_client() -> GitHubClient:
    """Get GitHub client instance (singleton)."""
    settings = get_settings()
    return GitHubClient(settings.github_token)


@lru_cache()
def get_ai_service() -> AIService:
    """Get AI service instance (singleton)."""
    settings = get_settings()
    return AIService(settings.ai_api_key, settings.ai_model, settings.ai_base_url)
