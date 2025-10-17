from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # GitHub Configuration
    github_token: str = ""
    github_webhook_secret: str = ""
    
    # AI Configuration
    ai_api_key: str = ""
    ai_model: str = "gpt-4"
    ai_base_url: Optional[str] = None  # Optional: custom base URL for OpenAI-compatible APIs
    
    # Application Settings
    log_level: str = "INFO"
    environment: str = "development"


settings = Settings()
