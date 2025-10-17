from app.services.github_client import CodeDiff, PullRequestEvent, ReviewComment


def test_code_diff():
    """Test CodeDiff schema."""
    diff = CodeDiff(
        filename="test.py",
        status="modified",
        additions=5,
        deletions=2,
        changes=7,
        patch="@@ -1,3 +1,3 @@",
    )
    assert diff.filename == "test.py"
    assert diff.status == "modified"
    assert diff.additions == 5
    assert diff.deletions == 2
    assert diff.changes == 7
    assert diff.patch == "@@ -1,3 +1,3 @@"


def test_review_comment():
    """Test ReviewComment schema."""
    comment = ReviewComment(path="test.py", line=10, body="This is a test comment", side="RIGHT")
    assert comment.path == "test.py"
    assert comment.line == 10
    assert comment.body == "This is a test comment"
    assert comment.side == "RIGHT"


def test_pull_request_event():
    """Test PullRequestEvent schema."""
    event = PullRequestEvent(
        action="opened",
        number=123,
        pull_request={"id": 1, "title": "Test PR"},
        repository={"name": "test-repo", "owner": {"login": "test-user"}},
    )
    assert event.action == "opened"
    assert event.number == 123
    assert event.pull_request["title"] == "Test PR"
    assert event.repository["name"] == "test-repo"
