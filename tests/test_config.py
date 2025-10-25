from unittest.mock import patch
from app.config import Settings


def test_settings_default_values():
    """Test that Settings loads with default values when no env vars are set."""
    with patch.dict("os.environ", {}, clear=True):
        settings = Settings(_env_file=None)

        assert settings.github_token is None
        assert settings.github_webhook_secret == ""
        assert settings.ai_api_key == ""
        assert settings.ai_model == "gpt-4"
        assert settings.ai_base_url is None
        assert settings.log_level == "INFO"
        assert settings.environment == "development"


def test_settings_from_environment_variables():
    """Test that Settings loads values from environment variables."""
    env_vars = {
        "GITHUB_TOKEN": "test-github-token",
        "GITHUB_WEBHOOK_SECRET": "test-webhook-secret",
        "AI_API_KEY": "test-api-key",
        "AI_MODEL": "gpt-3.5-turbo",
        "AI_BASE_URL": "https://custom-api.example.com",
        "LOG_LEVEL": "DEBUG",
        "ENVIRONMENT": "production",
    }

    with patch.dict("os.environ", env_vars, clear=True):
        settings = Settings(_env_file=None)

        assert settings.github_token == "test-github-token"
        assert settings.github_webhook_secret == "test-webhook-secret"
        assert settings.ai_api_key == "test-api-key"
        assert settings.ai_model == "gpt-3.5-turbo"
        assert settings.ai_base_url == "https://custom-api.example.com"
        assert settings.log_level == "DEBUG"
        assert settings.environment == "production"
