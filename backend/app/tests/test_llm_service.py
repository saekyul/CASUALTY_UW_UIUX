"""
Tests for LLM Service
"""
import pytest
from unittest.mock import patch, MagicMock

from app.services.llm_service import LLMService, get_llm_service


class TestLLMService:
    """Test LLM Service functionality"""

    def test_llm_service_initialization(self):
        """Test LLM service initialization"""
        service = LLMService()
        assert service is not None
        assert service.preferred_model in ["claude", "gemini"]

    def test_get_llm_service_singleton(self):
        """Test LLM service singleton pattern"""
        service1 = get_llm_service()
        service2 = get_llm_service()
        assert service1 is service2

    @pytest.mark.asyncio
    async def test_summarize_text_empty_input(self):
        """Test summarize with empty text"""
        service = LLMService()
        summary, model, tokens = await service.summarize_text("")
        assert summary == ""
        assert model == ""
        assert tokens is None

    @pytest.mark.asyncio
    async def test_extract_actions_empty_input(self):
        """Test extract actions with empty text"""
        service = LLMService()
        actions, model, tokens = await service.extract_actions("")
        assert actions == []
        assert model == ""
        assert tokens is None

    @pytest.mark.asyncio
    async def test_generate_response_fallback(self):
        """Test response generation with invalid model falls back"""
        service = LLMService()
        with patch.object(service, '_generate_response_with_claude', return_value=("Response", "claude", 100)):
            response, model, tokens = await service.generate_response(
                "Subject", "Body", model="invalid"
            )
            assert response == "Response"
            assert model == "claude"

    def test_invalid_model_raises_error(self):
        """Test that invalid model is handled"""
        service = LLMService()
        assert service.preferred_model in ["claude", "gemini"]

    @pytest.mark.asyncio
    async def test_text_to_sql_empty_input(self):
        """Test text to SQL with empty input"""
        service = LLMService()
        sql, model, tokens = await service.text_to_sql("", "")
        assert sql == ""
        assert model == ""
        assert tokens is None
