# Copilot Instructions for AI Agents

## Project Overview
- **Purpose:** AI-powered GitHub bot for automated code review.
- **Key Flows:**
  - Receives GitHub webhook events (pull requests) at `/webhooks/github` (see `app/api/webhooks.py`).
  - Analyzes code diffs with AI (see `app/services/ai_service.py`).
  - Posts review comments to GitHub (see `app/services/github_service.py`).

## Specific Instructions
- Use classes instead of dicts for data models where appropriate.

## Architecture
- `app/main.py`: FastAPI app entry point; configures API routes and app startup.
- `app/api/`: API endpoints, especially `webhooks.py` for GitHub integration.
- `app/services/`: Core business logic:
    - `ai_service.py`: Handles AI model calls and code analysis.
    - `github_service.py`: Manages GitHub API interactions.
- `app/config.py`: Loads environment/configuration variables.
- `tests/`: Pytest-based test suite for all major components.

## Developer Workflows
- **Install dependencies:** `poetry install`
- **Run server (dev):** `poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Run tests:** `poetry run pytest`
- **Format code:** `poetry run black app/ tests/`
- **Lint:** `poetry run flake8 app/ tests/` and `poetry run mypy app/`
- **Environment:** Copy `.env.example` to `.env` and set required secrets (see README for details).

## Patterns & Conventions
- **Async-first:** All service and API logic uses async/await for concurrency.
- **Separation of concerns:** API, service layer, dao and config are clearly separated.
- **Configuration:** Use `app/config.py` and environment variables for all secrets and settings.
- **Testing:** Place tests in `tests/` with filenames like `test_*.py`.
- **No hardcoded secrets:** All tokens/keys must come from environment/config.

## Integration Points
- **GitHub:** Webhook endpoint (`/webhooks/github`), GitHub API via `github_service.py`.
- **AI Service:** Model calls abstracted in `ai_service.py`; model and key set via env/config.

## Examples
- To add a new webhook handler, extend `app/api/webhooks.py` and register the route in `main.py`.
- To add a new AI model, update `ai_service.py` to support the new provider/model, and add config keys as needed.

## References
- See `README.md` for setup, environment, and workflow details.
- Key files: `app/main.py`, `app/api/webhooks.py`, `app/services/ai_service.py`, `app/services/github_service.py`, `app/config.py`.

---

If any conventions or flows are unclear, ask for clarification or check the README for up-to-date instructions.
