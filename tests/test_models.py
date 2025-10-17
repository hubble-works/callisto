import pytest
from app.models.schemas import CodeDiff, ReviewComment, AIReviewRequest


def test_code_diff_model():
    """Test CodeDiff model."""
    diff = CodeDiff(
        filename="test.py",
        status="modified",
        additions=5,
        deletions=2,
        changes=7,
        patch="@@ -1,3 +1,3 @@"
    )
    assert diff.filename == "test.py"
    assert diff.status == "modified"
    assert diff.additions == 5


def test_review_comment_model():
    """Test ReviewComment model."""
    comment = ReviewComment(
        path="test.py",
        line=10,
        body="This is a test comment",
        side="RIGHT"
    )
    assert comment.path == "test.py"
    assert comment.line == 10
    assert comment.body == "This is a test comment"


def test_ai_review_request_model():
    """Test AIReviewRequest model."""
    request = AIReviewRequest(
        diff="@@ -1,3 +1,3 @@",
        filename="test.py",
        context="Test context"
    )
    assert request.diff == "@@ -1,3 +1,3 @@"
    assert request.filename == "test.py"
    assert request.context == "Test context"
