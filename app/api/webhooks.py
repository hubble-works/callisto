import hashlib
import hmac
import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Header, Depends

from app.config import Settings
from app.dependencies import get_github_client, get_ai_service, get_settings
from app.services.ai_service import AIService, FileDiff
from app.services.github_client import GitHubClient, ReviewComment as GitHubReviewComment

router = APIRouter()
logger = logging.getLogger(__name__)


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature:
        return False

    hash_algorithm, signature_value = signature.split("=")
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()

    return hmac.compare_digest(expected_signature, signature_value)


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    github_client: GitHubClient = Depends(get_github_client),
    ai_service: AIService = Depends(get_ai_service),
    settings: Settings = Depends(get_settings),
):
    """Handle GitHub webhook events."""

    # Read raw body for signature verification
    body = await request.body()

    # Verify webhook signature
    if not verify_signature(body, x_hub_signature_256 or "", settings.github_webhook_secret):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    payload = await request.json()
    action = payload.get("action")

    logger.info(f"Received GitHub event: {x_github_event}.{action}")
    logger.debug(f"Request body: {payload}")

    # Handle pull request events
    if x_github_event == "pull_request":
        # Process PR opened or synchronized (new commits)
        if action in ["opened", "synchronize"]:
            await process_pull_request(payload, github_client, ai_service)
            return {"status": "processing"}

    # Handle issue comment events (includes PR comments)
    elif x_github_event == "issue_comment":
        # Process when comment is created
        if action == "created":
            comment_body = payload.get("comment", {}).get("body", "").strip()

            # Check if comment contains /review command
            if comment_body.startswith("/review"):
                # Verify it's a pull request comment
                if "pull_request" in payload.get("issue", {}):
                    await process_review_command(payload, github_client, ai_service)
                    return {"status": "processing"}

    return {"status": "ignored"}


async def process_review_command(payload: dict, github_client: GitHubClient, ai_service: AIService):
    """Process a /review command from a PR comment."""

    issue = payload["issue"]
    pr_number = issue["number"]
    repo_full_name = payload["repository"]["full_name"]
    owner, repo = repo_full_name.split("/")

    logger.info(f"Processing /review command for PR #{pr_number} in {repo_full_name}")

    await process_pull_request_review(owner, repo, pr_number, github_client, ai_service)


async def process_pull_request(payload: dict, github_client: GitHubClient, ai_service: AIService):
    """Process a pull request and perform AI code review."""

    pr_number = payload["number"]
    repo_full_name = payload["repository"]["full_name"]
    owner, repo = repo_full_name.split("/")

    logger.info(f"Processing PR #{pr_number} in {repo_full_name}")

    await process_pull_request_review(owner, repo, pr_number, github_client, ai_service)


async def process_pull_request_review(
    owner: str, repo: str, pr_number: int, github_client: GitHubClient, ai_service: AIService
):
    """Perform AI code review on a pull request."""

    try:
        # Get PR diff
        diff_files = await github_client.get_pr_diff(owner, repo, pr_number)

        if not diff_files:
            logger.info(f"No files to review in PR #{pr_number}")
            return

        # Combine all diffs into a single list
        files_with_diffs = [
            FileDiff(name=file.filename, diff=file.patch) for file in diff_files if file.patch
        ]

        if not files_with_diffs:
            logger.info(f"No files with patches to review in PR #{pr_number}")
            return

        # Analyze entire PR with AI in a single request
        all_comments = await ai_service.review_pull_request(
            files_with_diffs=files_with_diffs,
            context=f"Pull Request #{pr_number} in {owner}/{repo}",
        )

        # Convert AI ReviewComments to GitHub ReviewComments
        github_comments = [
            GitHubReviewComment(
                path=comment.path,
                position=comment.position,
                body=comment.body,
                line=comment.line,
                side=comment.side,
                start_line=comment.start_line,
                start_side=comment.start_side,
            )
            for comment in all_comments
        ]

        # Post review comments
        if github_comments:
            await github_client.post_review(owner, repo, pr_number, github_comments)
            logger.info(f"Posted {len(github_comments)} review comments on PR #{pr_number}")
        else:
            logger.info(f"No issues found in PR #{pr_number}")

    except Exception as e:
        logger.error(f"Error processing PR #{pr_number}: {str(e)}", exc_info=True)
        raise
