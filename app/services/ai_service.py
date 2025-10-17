import logging
from typing import List, Optional
from openai import AsyncOpenAI
from app.models.schemas import ReviewComment

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-based code review."""
    
    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        self.model = model
        
        # Initialize OpenAI client with optional custom base URL
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = AsyncOpenAI(**client_kwargs)
    
    async def review_code(
        self,
        diff: str,
        filename: str,
        context: str = ""
    ) -> List[ReviewComment]:
        """
        Review code using AI and return comments.
        
        Args:
            diff: The code diff to review
            filename: Name of the file being reviewed
            context: Additional context about the code
        
        Returns:
            List of review comments
        """
        
        system_prompt = """You are an expert code reviewer. Analyze the provided code diff and provide constructive feedback.
Focus on:
- Potential bugs or errors
- Security vulnerabilities
- Performance issues
- Code quality and best practices
- Maintainability concerns

For each issue found, provide:
1. The line number where the issue occurs
2. A clear description of the issue
3. A suggestion for improvement

Format your response as a JSON array of objects with fields:
- line: the line number in the diff (right side)
- comment: the review comment

Only report significant issues. Avoid nitpicking on style unless it affects readability or maintainability.
If the code looks good, return an empty array."""

        user_prompt = f"""Please review this code diff:

File: {filename}
{context}

Diff:
```
{diff}
```

Provide your review as a JSON array."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            comments = self._parse_ai_response(ai_response, filename)
            
            logger.info(f"AI reviewed {filename}: found {len(comments)} issues")
            return comments
                
        except Exception as e:
            logger.error(f"Error during AI review: {str(e)}", exc_info=True)
            return []
    
    def _parse_ai_response(self, response: str, filename: str) -> List[ReviewComment]:
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
                if isinstance(issue, dict) and "line" in issue and "comment" in issue:
                    comments.append(
                        ReviewComment(
                            path=filename,
                            line=int(issue["line"]),
                            body=issue["comment"],
                            side="RIGHT"
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
