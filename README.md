# Callisto – AI-Assisted Code Review for GitHub

A GitHub agent that performs AI-assisted code reviews by analyzing diffs and providing intelligent comments.

## Features

- Receives GitHub webhook events for pull requests
- Analyzes code diffs using AI
- Posts review comments back to GitHub
- Built with FastAPI for high performance
- Async/await support for efficient processing

## Setup

### GitHub App Installation

1. Install the Callisto GitHub App on your repository:
   - Visit https://github.com/apps/callisto-agent
   - Click "Install" and select the repositories you want to enable code reviews for

### Local Development Installation

1. Install dependencies:
```bash
poetry install
```

2. Configure your settings:
```bash
cp .env.example .env
# Edit .env with your GitHub token and AI API keys
```

### Running the Agent

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
- `AI_BASE_URL`: (Optional) Custom base URL for OpenAI-compatible APIs (e.g., Azure OpenAI, LocalAI, Ollama)
  - If not set, defaults to OpenAI's official API endpoint
  - Example for Azure: `https://YOUR-RESOURCE.openai.azure.com/v1`
  - Example for LocalAI: `http://localhost:8080/v1`

## Architecture

- `app/main.py`: FastAPI application entry point
- `app/api/`: API endpoints
- `app/services/`: Business logic (GitHub integration, AI analysis)
- `app/config.py`: Configuration management
- `tests/`: Test suite

## GitHub Webhook Setup

1. Go to your repository settings → Webhooks
2. Add webhook with URL: `https://your-domain.com/webhooks/github`
3. Select events: Pull requests
4. Set the webhook secret matching your `GITHUB_WEBHOOK_SECRET`

## Docker

### Building Locally

```bash
docker build -t callisto .
docker run -p 8000:8000 --env-file .env callisto
```

### GitHub Container Registry

Docker images are automatically built and published to GitHub Container Registry on pushes to `main` and `develop` branches.

Pull the latest image:
```bash
docker pull ghcr.io/hubble-works/callisto:latest
```

Available tags:
- `latest`: Latest build from main branch
- `main`: Latest build from main branch
- `develop`: Latest build from develop branch
- `v*`: Semantic version tags (e.g., v1.0.0)
- `main-<sha>`, `develop-<sha>`: Specific commit builds

Run the container:
```bash
docker run -p 8000:8000 --env-file .env ghcr.io/hubble-works/callisto:latest
```

### Creating a Release

To publish a versioned release:

1. Create and push a tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

2. The Docker image will be automatically built and tagged as:
   - `ghcr.io/hubble-works/callisto:v1.0.0`
   - `ghcr.io/hubble-works/callisto:1.0.0`
   - `ghcr.io/hubble-works/callisto:1.0`
   - `ghcr.io/hubble-works/callisto:1`

## License

MIT
