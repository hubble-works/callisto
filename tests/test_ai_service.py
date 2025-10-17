import pytest
from app.services.ai_service import FileDiff, ReviewComment, AIReviewRequest, AIReviewResponse


def test_file_diff():
    """Test FileDiff schema."""
    file_diff = FileDiff(
        name="test.py",
        diff="@@ -1,3 +1,3 @@"
    )
    assert file_diff.name == "test.py"
    assert file_diff.diff == "@@ -1,3 +1,3 @@"


def test_review_comment():
    """Test ReviewComment schema."""
    comment = ReviewComment(
        path="test.py",
        line=10,
        body="This is a test comment",
        side="RIGHT"
    )
    assert comment.path == "test.py"
    assert comment.line == 10
    assert comment.body == "This is a test comment"
    assert comment.side == "RIGHT"


def test_ai_review_request():
    """Test AIReviewRequest schema."""
    request = AIReviewRequest(
        diff="@@ -1,3 +1,3 @@",
        filename="test.py",
        context="Test context"
    )
    assert request.diff == "@@ -1,3 +1,3 @@"
    assert request.filename == "test.py"
    assert request.context == "Test context"


def test_ai_review_response():
    """Test AIReviewResponse schema."""
    comment = ReviewComment(
        path="test.py",
        line=10,
        body="Test comment"
    )
    response = AIReviewResponse(
        comments=[comment],
        summary="Test summary"
    )
    assert len(response.comments) == 1
    assert response.comments[0].path == "test.py"
    assert response.summary == "Test summary"
