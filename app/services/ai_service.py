import logging
from typing import List, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ReviewComment(BaseModel):
    """A review comment to post on a pull request."""

    path: str
    position: Optional[int] = None
    body: str
    line: Optional[int] = None
    side: str = "RIGHT"  # LEFT or RIGHT
    start_line: Optional[int] = None
    start_side: Optional[str] = None


class FileDiff(BaseModel):
    """Represents a file with its diff for AI review."""

    name: str
    diff: str


class AIReviewRequest(BaseModel):
    """Request for AI code review."""

    diff: str
    filename: str
    context: Optional[str] = None


class AIReviewResponse(BaseModel):
    """Response from AI code review."""

    comments: List[ReviewComment]
    summary: Optional[str] = None


class AIService:
    """Service for AI-based code review."""

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        self.model = model

        # Initialize OpenAI client with optional custom base URL
        if base_url:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = AsyncOpenAI(api_key=api_key)

    async def review_pull_request(
        self, files_with_diffs: List[FileDiff], context: str = ""
    ) -> List[ReviewComment]:
        """
        Review entire pull request with all files in a single AI request.

        Args:
            files_with_diffs: List of FileDiff objects containing file name and diff
            context: Additional context about the pull request

        Returns:
            List of review comments
        """

        if not files_with_diffs:
            return []

        system_prompt = """You are an expert code reviewer. \
Analyze the provided pull request diff and provide constructive feedback.
Focus on:
- Potential bugs or errors
- Security vulnerabilities
- Performance issues
- Code quality and best practices
- Maintainability concerns
- Cross-file dependencies and interactions

For each issue found, provide:
1. The file path where the issue occurs
2. The line number where the issue occurs
3. A clear description of the issue
4. A suggestion for improvement

Format your response as a JSON array of objects with fields:
- path: the file path
- line: the line number in the diff (right side)
- comment: the review comment

Only report significant issues. \
Avoid nitpicking on style unless it affects readability or maintainability.
If the code looks good, return an empty array."""

        # Combine all diffs into a single prompt
        combined_diff = ""
        for file_diff in files_with_diffs:
            combined_diff += f"\n\n=== File: {file_diff.name} ===\n{file_diff.diff}"

        user_prompt = f"""Please review this pull request:

{context}

Combined diff of all files:
```
{combined_diff}
```

Provide your review as a JSON array."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=4000,
            )

            # Parse AI response
            ai_response = response.choices[0].message.content or ""
            comments = self._parse_ai_response(ai_response)

            logger.info(
                f"AI reviewed PR with {len(files_with_diffs)} files: found {len(comments)} issues"
            )
            return comments

        except Exception as e:
            logger.error(f"Error during AI review: {str(e)}", exc_info=True)
            return []

    def _parse_ai_response(self, response: str) -> List[ReviewComment]:
        """Parse AI response into ReviewComment objects."""
        import json

        try:
            # Try to extract JSON from the response
            # AI might wrap it in markdown code blocks
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            issues = json.loads(response)

            if not isinstance(issues, list):
                logger.warning("AI response is not a list, returning empty comments")
                return []

            comments = []
            for issue in issues:
                if (
                    isinstance(issue, dict)
                    and "line" in issue
                    and "comment" in issue
                    and "path" in issue
                ):
                    comments.append(
                        ReviewComment(
                            path=issue["path"],
                            line=int(issue["line"]),
                            body=issue["comment"],
                            side="RIGHT",
                        )
                    )

            return comments

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"AI response was: {response}")
            return []
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return []
