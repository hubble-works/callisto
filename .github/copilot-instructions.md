# Copilot Instructions for AI Agents

## Project Overview
- **Purpose:** AI-powered GitHub agent for automated code review analyzing pull request diffs.
- **Data Flow:** GitHub webhook → FastAPI endpoint → AI analysis → GitHub review comments
- **Core Pattern:** Use Pydantic models for all data structures; async/await throughout; dependency injection for services

## Architecture
- `app/main.py`: FastAPI app entry point; includes webhook router at `/webhooks` prefix
- `app/api/webhooks.py`: Single webhook handler for GitHub events (PR opened/sync, `/review` commands)
- `app/services/`:
  - `ai_service.py`: OpenAI client with combined PR analysis (not per-file)
  - `github_client.py`: GitHub API client for diff retrieval and review posting
- `app/config.py`: Pydantic settings with `.env` loading
- `app/dependencies.py`: Singleton services via `@lru_cache()` decorators

## Key Patterns & Conventions
- **Data Models:** Use Pydantic BaseModel classes (not dicts) - see `ReviewComment`, `FileDiff`, `CodeDiff`
- **Async Everything:** All API endpoints and service methods are async
- **Service Singletons:** Services injected via `Depends()` with cached constructors in `dependencies.py`
- **Error Handling:** Log with context and re-raise - see webhook error handling pattern
- **Configuration:** All secrets via environment variables in `Settings` class

## Developer Workflows
- **Poetry-based:** Use `poetry install` and `poetry run` for dependency management
- **Make targets:** `make run` (dev server), `make test` (pytest), `make format` (black), `make lint` (flake8+mypy), `make ci` (all checks)
- **Testing:** Schema-only tests in `tests/test_*.py` - no mocking/integration tests currently
- **Environment:** Copy `.env.example` to `.env` with `GITHUB_TOKEN`, `AI_API_KEY`, etc.

## Critical Implementation Details
- **Webhook Processing:** Validates GitHub signature, handles PR events and `/review` commands
- **AI Review Strategy:** Combines all file diffs into single AI request (not per-file) for better context
- **Line Mapping:** AI returns line numbers for "RIGHT" side of diff; GitHub API posts at specific lines
- **Response Parsing:** AI returns JSON array; robust parsing handles markdown code blocks
- **OpenAI Compatibility:** Supports custom `base_url` for Azure OpenAI, LocalAI, etc.

## Common Extension Points
- **New Webhook Events:** Add handlers in `github_webhook()` function checking `x_github_event`
- **AI Providers:** Modify `AIService.__init__()` to support different clients while keeping same interface
- **Review Filters:** Extend file filtering logic in `process_pull_request_review()`
- **Comment Formatting:** Customize AI system prompt in `review_pull_request()` method

## Key Files to Understand
- `app/api/webhooks.py`: Lines 50-80 show webhook signature validation pattern
- `app/services/ai_service.py`: Lines 72-98 show combined diff strategy and JSON parsing
- `app/services/github_client.py`: Lines 51-75 show GitHub API pagination and diff retrieval
