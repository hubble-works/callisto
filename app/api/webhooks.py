from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import hmac
import hashlib
import logging

from app.services.github_service import GitHubService
from app.services.ai_service import AIService
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

github_service = GitHubService(settings.github_token)
ai_service = AIService(settings.ai_api_key, settings.ai_model, settings.ai_base_url)


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
    x_github_event: Optional[str] = Header(None)
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
    
    logger.info(f"Received GitHub event: {x_github_event}")
    
    # Handle pull request events
    if x_github_event == "pull_request":
        action = payload.get("action")
        
        # Process PR opened or synchronized (new commits)
        if action in ["opened", "synchronize"]:
            await process_pull_request(payload)
            return {"status": "processing"}
    
    # Handle issue comment events (includes PR comments)
    elif x_github_event == "issue_comment":
        action = payload.get("action")
        
        # Process when comment is created
        if action == "created":
            comment_body = payload.get("comment", {}).get("body", "").strip()
            
            # Check if comment contains /review command
            if comment_body.startswith("/review"):
                # Verify it's a pull request comment
                if "pull_request" in payload.get("issue", {}):
                    await process_review_command(payload)
                    return {"status": "processing"}
    
    return {"status": "ignored"}


async def process_review_command(payload: dict):
    """Process a /review command from a PR comment."""
    
    issue = payload["issue"]
    pr_number = issue["number"]
    repo_full_name = payload["repository"]["full_name"]
    owner, repo = repo_full_name.split("/")
    
    logger.info(f"Processing /review command for PR #{pr_number} in {repo_full_name}")
    
    await process_pull_request_review(owner, repo, pr_number)


async def process_pull_request(payload: dict):
    """Process a pull request and perform AI code review."""
    
    pr_number = payload["number"]
    repo_full_name = payload["repository"]["full_name"]
    owner, repo = repo_full_name.split("/")
    
    logger.info(f"Processing PR #{pr_number} in {repo_full_name}")
    
    await process_pull_request_review(owner, repo, pr_number)


async def process_pull_request_review(owner: str, repo: str, pr_number: int):
    """Perform AI code review on a pull request."""
    
    try:
        # Get PR diff
        diff_files = await github_service.get_pr_diff(owner, repo, pr_number)
        
        if not diff_files:
            logger.info(f"No files to review in PR #{pr_number}")
            return
        
        # Analyze each file with AI
        all_comments = []
        for file in diff_files:
            if file.patch:
                comments = await ai_service.review_code(
                    diff=file.patch,
                    filename=file.filename
                )
                all_comments.extend(comments)
        
        # Post review comments
        if all_comments:
            await github_service.post_review(
                owner, repo, pr_number, all_comments
            )
            logger.info(f"Posted {len(all_comments)} review comments on PR #{pr_number}")
        else:
            logger.info(f"No issues found in PR #{pr_number}")
    
    except Exception as e:
        logger.error(f"Error processing PR #{pr_number}: {str(e)}", exc_info=True)
        raise
