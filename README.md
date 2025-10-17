# AI-Assisted Code Review Bot

A GitHub bot that performs AI-assisted code reviews by analyzing diffs and providing intelligent comments.

## Features

- Receives GitHub webhook events for pull requests
- Analyzes code diffs using AI
- Posts review comments back to GitHub
- Built with FastAPI for high performance
- Async/await support for efficient processing

## Setup

### Prerequisites

- Python 3.11+
- Poetry (install from https://python-poetry.org/docs/#installation)
- GitHub account and repository access

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Configure your settings:
```bash
cp .env.example .env
# Edit .env with your GitHub token and AI API keys
```

### Running the Bot

Start the development server:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the Poetry script:
```bash
poetry run start
```

### Running Tests

```bash
poetry run pytest
```

### Code Quality

Format code:
```bash
poetry run black app/ tests/
```

Lint code:
```bash
poetry run flake8 app/ tests/
poetry run mypy app/
```

## Configuration

Set these environment variables in your `.env` file:

- `GITHUB_TOKEN`: Your GitHub personal access token
- `GITHUB_WEBHOOK_SECRET`: Secret for validating GitHub webhooks
- `AI_API_KEY`: API key for your AI service (e.g., OpenAI)
- `AI_MODEL`: AI model to use (e.g., gpt-4)

## Architecture

- `app/main.py`: FastAPI application entry point
- `app/api/`: API endpoints
- `app/services/`: Business logic (GitHub integration, AI analysis)
- `app/models/`: Data models
- `app/config.py`: Configuration management
- `tests/`: Test suite

## GitHub Webhook Setup

1. Go to your repository settings → Webhooks
2. Add webhook with URL: `https://your-domain.com/webhooks/github`
3. Select events: Pull requests
4. Set the webhook secret matching your `GITHUB_WEBHOOK_SECRET`

## License

MIT
