import logging

from fastapi import FastAPI

from app.api import webhooks
from app.config import Settings

# Load settings
settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Set app logger to configured level
app_logger = logging.getLogger("app")
app_logger.setLevel(getattr(logging, settings.log_level.upper()))

app = FastAPI(
    title="Callisto AI Code Review Agent",
    description="GitHub agent that performs AI-assisted code reviews",
    version="1.0.0",
)

# Include routers
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


@app.get("/")
async def root():
    return {"status": "healthy", "service": "Callisto AI Code Review Agent"}


@app.get("/health")
async def health():
    return {"status": "ok"}
