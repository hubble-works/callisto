import httpx
import logging
from typing import List, Optional
from app.models.schemas import CodeDiff, ReviewComment

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> List[CodeDiff]:
        """Get the diff files for a pull request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            files = response.json()
            
            return [
                CodeDiff(
                    filename=file["filename"],
                    status=file["status"],
                    additions=file["additions"],
                    deletions=file["deletions"],
                    changes=file["changes"],
                    patch=file.get("patch")
                )
                for file in files
            ]
    
    async def post_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        comments: List[ReviewComment],
        event: str = "COMMENT"
    ):
        """Post a review with comments on a pull request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        # Format comments for GitHub API
        formatted_comments = [
            {
                "path": comment.path,
                "body": comment.body,
                "line": comment.line,
                "side": comment.side
            }
            for comment in comments
        ]
        
        payload = {
            "event": event,
            "comments": formatted_comments
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def get_pr_details(self, owner: str, repo: str, pr_number: int) -> dict:
        """Get pull request details."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def post_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str
    ):
        """Post a general comment on a pull request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        payload = {"body": body}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
