"""
LLM Service - Integration with Claude and Gemini APIs
"""
import logging
from typing import Optional

from anthropic import Anthropic as ClaudeClient
from anthropic import APIError as ClaudeAPIError
import google.generativeai as gemini

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM operations (Claude + Gemini)"""

    def __init__(self):
        self.preferred_model = settings.PREFERRED_LLM
        self.claude_client = None
        self.gemini_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize LLM clients"""
        if settings.CLAUDE_API_KEY:
            try:
                self.claude_client = ClaudeClient(api_key=settings.CLAUDE_API_KEY)
                logger.info("Claude API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")

        if settings.GEMINI_API_KEY:
            try:
                gemini.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_client = gemini
                logger.info("Gemini API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

    async def summarize_text(
        self,
        text: str,
        model: Optional[str] = None,
        language: str = "korean",
    ) -> tuple[str, str, Optional[int]]:
        """
        Summarize text using LLM

        Args:
            text: Text to summarize
            model: LLM model to use (claude or gemini). If None, uses preferred model
            language: Language for summary (korean or english)

        Returns:
            Tuple of (summary, model_used, tokens_used)
        """
        if not text:
            return "", "", None

        model = model or self.preferred_model

        if model == "claude":
            return await self._summarize_with_claude(text, language)
        elif model == "gemini":
            return await self._summarize_with_gemini(text, language)
        else:
            logger.warning(f"Unknown model: {model}, falling back to preferred model")
            return await self.summarize_text(text, self.preferred_model, language)

    async def _summarize_with_claude(
        self, text: str, language: str = "korean"
    ) -> tuple[str, str, Optional[int]]:
        """Summarize using Claude API"""
        try:
            if not self.claude_client:
                raise Exception("Claude client not initialized")

            lang_instruction = "한국어로" if language == "korean" else "English로"

            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"""다음 텍스트를 {lang_instruction} 간단하게 요약해주세요.
중요한 내용을 3-5줄로 정리해주세요.

텍스트:
{text}""",
                    }
                ],
            )

            summary = message.content[0].text
            tokens_used = message.usage.output_tokens

            logger.info(f"Claude summarization completed. Tokens: {tokens_used}")
            return summary, "claude", tokens_used

        except ClaudeAPIError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Claude summarization error: {e}")
            raise

    async def _summarize_with_gemini(
        self, text: str, language: str = "korean"
    ) -> tuple[str, str, Optional[int]]:
        """Summarize using Gemini API"""
        try:
            if not self.gemini_client:
                raise Exception("Gemini client not initialized")

            lang_instruction = "한국어로" if language == "korean" else "English로"

            model = self.gemini_client.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                f"""다음 텍스트를 {lang_instruction} 간단하게 요약해주세요.
중요한 내용을 3-5줄로 정리해주세요.

텍스트:
{text}"""
            )

            summary = response.text
            logger.info("Gemini summarization completed")
            return summary, "gemini", None

        except Exception as e:
            logger.error(f"Gemini summarization error: {e}")
            raise

    async def extract_actions(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> tuple[list[dict], str, Optional[int]]:
        """
        Extract action items from text

        Args:
            text: Text to extract actions from
            model: LLM model to use

        Returns:
            Tuple of (actions, model_used, tokens_used)
            Actions format: [{"action": str, "priority": str, "deadline": Optional[str]}, ...]
        """
        model = model or self.preferred_model

        if model == "claude":
            return await self._extract_actions_with_claude(text)
        elif model == "gemini":
            return await self._extract_actions_with_gemini(text)
        else:
            return await self.extract_actions(text, self.preferred_model)

    async def _extract_actions_with_claude(self, text: str) -> tuple[list[dict], str, Optional[int]]:
        """Extract actions using Claude API"""
        try:
            if not self.claude_client:
                raise Exception("Claude client not initialized")

            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"""다음 텍스트에서 해야 할 일/액션 아이템을 추출해주세요.
JSON 형식으로 다음과 같이 응답해주세요:
{{"actions": [{{"action": "액션 설명", "priority": "high/medium/low", "deadline": "기한 또는 null"}}]}}

텍스트:
{text}""",
                    }
                ],
            )

            import json

            try:
                response_text = message.content[0].text
                # Find JSON in response
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    parsed = json.loads(json_str)
                    actions = parsed.get("actions", [])
                else:
                    actions = []
            except (json.JSONDecodeError, ValueError):
                logger.warning("Failed to parse actions JSON from Claude")
                actions = []

            tokens_used = message.usage.output_tokens
            logger.info(f"Claude action extraction completed. Tokens: {tokens_used}")
            return actions, "claude", tokens_used

        except Exception as e:
            logger.error(f"Claude action extraction error: {e}")
            raise

    async def _extract_actions_with_gemini(self, text: str) -> tuple[list[dict], str, Optional[int]]:
        """Extract actions using Gemini API"""
        try:
            if not self.gemini_client:
                raise Exception("Gemini client not initialized")

            model = self.gemini_client.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                f"""다음 텍스트에서 해야 할 일/액션 아이템을 추출해주세요.
JSON 형식으로 다음과 같이 응답해주세요:
{{"actions": [{{"action": "액션 설명", "priority": "high/medium/low", "deadline": "기한 또는 null"}}]}}

텍스트:
{text}"""
            )

            import json

            try:
                response_text = response.text
                # Find JSON in response
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    parsed = json.loads(json_str)
                    actions = parsed.get("actions", [])
                else:
                    actions = []
            except (json.JSONDecodeError, ValueError):
                logger.warning("Failed to parse actions JSON from Gemini")
                actions = []

            logger.info("Gemini action extraction completed")
            return actions, "gemini", None

        except Exception as e:
            logger.error(f"Gemini action extraction error: {e}")
            raise

    async def generate_response(
        self,
        email_subject: str,
        email_body: str,
        model: Optional[str] = None,
    ) -> tuple[str, str, Optional[int]]:
        """
        Generate auto-response to email

        Args:
            email_subject: Email subject
            email_body: Email body
            model: LLM model to use

        Returns:
            Tuple of (response, model_used, tokens_used)
        """
        model = model or self.preferred_model

        if model == "claude":
            return await self._generate_response_with_claude(email_subject, email_body)
        elif model == "gemini":
            return await self._generate_response_with_gemini(email_subject, email_body)
        else:
            return await self.generate_response(email_subject, email_body, self.preferred_model)

    async def _generate_response_with_claude(
        self, email_subject: str, email_body: str
    ) -> tuple[str, str, Optional[int]]:
        """Generate response using Claude API"""
        try:
            if not self.claude_client:
                raise Exception("Claude client not initialized")

            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""다음 이메일에 대한 전문적인 응답을 한국어로 작성해주세요.
간결하고 친절한 톤으로 작성해주세요.

제목: {email_subject}
본문: {email_body}

응답:""",
                    }
                ],
            )

            response = message.content[0].text
            tokens_used = message.usage.output_tokens
            logger.info(f"Claude response generation completed. Tokens: {tokens_used}")
            return response, "claude", tokens_used

        except Exception as e:
            logger.error(f"Claude response generation error: {e}")
            raise

    async def _generate_response_with_gemini(
        self, email_subject: str, email_body: str
    ) -> tuple[str, str, Optional[int]]:
        """Generate response using Gemini API"""
        try:
            if not self.gemini_client:
                raise Exception("Gemini client not initialized")

            model = self.gemini_client.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                f"""다음 이메일에 대한 전문적인 응답을 한국어로 작성해주세요.
간결하고 친절한 톤으로 작성해주세요.

제목: {email_subject}
본문: {email_body}

응답:"""
            )

            response_text = response.text
            logger.info("Gemini response generation completed")
            return response_text, "gemini", None

        except Exception as e:
            logger.error(f"Gemini response generation error: {e}")
            raise

    async def text_to_sql(
        self,
        natural_language_query: str,
        schema_info: str,
        model: Optional[str] = None,
    ) -> tuple[str, str, Optional[int]]:
        """
        Convert natural language to SQL query

        Args:
            natural_language_query: User's natural language query
            schema_info: Database schema information
            model: LLM model to use

        Returns:
            Tuple of (sql_query, model_used, tokens_used)
        """
        model = model or self.preferred_model

        if model == "claude":
            return await self._text_to_sql_with_claude(natural_language_query, schema_info)
        elif model == "gemini":
            return await self._text_to_sql_with_gemini(natural_language_query, schema_info)
        else:
            return await self.text_to_sql(natural_language_query, schema_info, self.preferred_model)

    async def _text_to_sql_with_claude(
        self, natural_language_query: str, schema_info: str
    ) -> tuple[str, str, Optional[int]]:
        """Convert to SQL using Claude API"""
        try:
            if not self.claude_client:
                raise Exception("Claude client not initialized")

            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": f"""다음 데이터베이스 스키마를 기반으로 SQL 쿼리를 작성해주세요.

스키마:
{schema_info}

요청:
{natural_language_query}

SQL 쿼리만 응답해주세요. 설명은 필요 없습니다.""",
                    }
                ],
            )

            sql_query = message.content[0].text.strip()
            tokens_used = message.usage.output_tokens
            logger.info(f"Claude SQL generation completed. Tokens: {tokens_used}")
            return sql_query, "claude", tokens_used

        except Exception as e:
            logger.error(f"Claude SQL generation error: {e}")
            raise

    async def _text_to_sql_with_gemini(
        self, natural_language_query: str, schema_info: str
    ) -> tuple[str, str, Optional[int]]:
        """Convert to SQL using Gemini API"""
        try:
            if not self.gemini_client:
                raise Exception("Gemini client not initialized")

            model = self.gemini_client.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                f"""다음 데이터베이스 스키마를 기반으로 SQL 쿼리를 작성해주세요.

스키마:
{schema_info}

요청:
{natural_language_query}

SQL 쿼리만 응답해주세요. 설명은 필요 없습니다."""
            )

            sql_query = response.text.strip()
            logger.info("Gemini SQL generation completed")
            return sql_query, "gemini", None

        except Exception as e:
            logger.error(f"Gemini SQL generation error: {e}")
            raise


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
