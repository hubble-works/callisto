from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class PullRequestEvent(BaseModel):
    """GitHub Pull Request webhook event."""
    action: str
    number: int
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]


class ReviewComment(BaseModel):
    """A review comment to post on a pull request."""
    path: str
    position: Optional[int] = None
    body: str
    line: Optional[int] = None
    side: str = "RIGHT"  # LEFT or RIGHT
    start_line: Optional[int] = None
    start_side: Optional[str] = None


class CodeDiff(BaseModel):
    """Represents a code diff."""
    filename: str
    status: str  # added, removed, modified
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None


class AIReviewRequest(BaseModel):
    """Request for AI code review."""
    diff: str
    filename: str
    context: Optional[str] = None


class AIReviewResponse(BaseModel):
    """Response from AI code review."""
    comments: List[ReviewComment]
    summary: Optional[str] = None
