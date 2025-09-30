from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.genai import types

from app.model.model import BaseModelType
from app.service.llm_api import (
    get_deepseek_output,
    get_gemini_output,
    get_groq_output,
    get_model_output,
)


@pytest.fixture
def system_prompt():
    """Fixture for a sample system prompt."""
    return "You are a JSONata expression generator."


@pytest.fixture
def user_prompt():
    """Fixture for a sample user prompt."""
    return "Generate a JSONata expression to filter items where age > 30."


@pytest.fixture
def mock_groq_response():
    """Fixture for a mocked Groq response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[
        0
    ].message.content = "```jsonata\n$filter($, function($v) { $v.age > 30 })\n```"
    return response


@pytest.fixture
def mock_openai_response():
    """Fixture for a mocked OpenAI/DeepSeek response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[
        0
    ].message.content = "```jsonata\n$filter($, function($v) { $v.age > 30 })\n```"
    return response


@pytest.fixture
def mock_gemini_response():
    """Fixture for a mocked Gemini response."""
    response = MagicMock()
    response.text = "```jsonata\n$filter($, function($v) { $v.age > 30 })\n```"
    return response


@pytest.mark.asyncio
async def test_get_model_output_groq(system_prompt, user_prompt, mock_groq_response):
    """Test get_model_output with Groq model."""
    with patch("app.service.llm_api.AsyncGroq") as mock_groq:
        mock_client = mock_groq.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=mock_groq_response)
        result = await get_model_output(system_prompt, user_prompt, BaseModelType.groq)
        assert result == "$filter($, function($v) { $v.age > 30 })"
        mock_client.chat.completions.create.assert_awaited_once_with(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model="llama-3.3-70b-versatile",
            stream=False,
            temperature=0.0,
        )


@pytest.mark.asyncio
async def test_get_model_output_gemini(
    system_prompt, user_prompt, mock_gemini_response
):
    """Test get_model_output with Gemini model."""
    with patch("app.service.llm_api.genai.Client") as mock_genai:
        mock_client = mock_genai.return_value
        mock_client.aio.models.generate_content = AsyncMock(
            return_value=mock_gemini_response
        )
        result = await get_model_output(
            system_prompt, user_prompt, BaseModelType.gemini
        )
        assert result == "$filter($, function($v) { $v.age > 30 })"
        mock_client.aio.models.generate_content.assert_awaited_once_with(
            model="gemini-2.0-flash",
            contents=[user_prompt],
            config=types.GenerateContentConfig(
                temperature=0.0, system_instruction=system_prompt
            ),
        )


@pytest.mark.asyncio
async def test_get_model_output_deepseek(
    system_prompt, user_prompt, mock_openai_response
):
    """Test get_model_output with DeepSeek model."""
    with patch("app.service.llm_api.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(
            return_value=mock_openai_response
        )
        result = await get_model_output(
            system_prompt, user_prompt, BaseModelType.deepseek
        )
        assert result == "$filter($, function($v) { $v.age > 30 })"
        mock_client.chat.completions.create.assert_awaited_once_with(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
            temperature=0.0,
        )


@pytest.mark.asyncio
async def test_get_model_output_invalid_model(system_prompt, user_prompt):
    """Test get_model_output with an invalid BaseModelType."""
    with pytest.raises(ValueError, match="Unsupported base model: invalid"):
        await get_model_output(
            system_prompt, user_prompt, "invalid"
        )  # Invalid BaseModelType


@pytest.mark.asyncio
async def test_get_model_output_none_response(system_prompt, user_prompt):
    """Test get_model_output when model returns None."""
    with patch("app.service.llm_api.genai.Client") as mock_genai:
        mock_client = mock_genai.return_value
        mock_response = MagicMock()
        mock_response.text = None
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        with pytest.raises(
            ValueError, match="No JSONata expression returned from the model"
        ):
            await get_model_output(system_prompt, user_prompt, BaseModelType.gemini)


@pytest.mark.asyncio
async def test_get_groq_output(system_prompt, user_prompt, mock_groq_response):
    """Test get_groq_output with valid response."""
    with patch("app.service.llm_api.AsyncGroq") as mock_groq:
        mock_client = mock_groq.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=mock_groq_response)
        result = await get_groq_output(system_prompt, user_prompt)
        assert result == "```jsonata\n$filter($, function($v) { $v.age > 30 })\n```"
        mock_client.chat.completions.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_gemini_output(system_prompt, user_prompt, mock_gemini_response):
    """Test get_gemini_output with valid response."""
    with patch("app.service.llm_api.genai.Client") as mock_genai:
        mock_client = mock_genai.return_value
        mock_client.aio.models.generate_content = AsyncMock(
            return_value=mock_gemini_response
        )
        result = await get_gemini_output(system_prompt, user_prompt)
        assert result == "```jsonata\n$filter($, function($v) { $v.age > 30 })\n```"
        mock_client.aio.models.generate_content.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_gemini_output_none(system_prompt, user_prompt):
    """Test get_gemini_output when response is None."""
    with patch("app.service.llm_api.genai.Client") as mock_genai:
        mock_client = mock_genai.return_value
        mock_response = MagicMock()
        mock_response.text = None
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        result = await get_gemini_output(system_prompt, user_prompt)
        assert result is None


@pytest.mark.asyncio
async def test_get_deepseek_output(system_prompt, user_prompt, mock_openai_response):
    """Test get_deepseek_output with valid response."""
    with patch("app.service.llm_api.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(
            return_value=mock_openai_response
        )
        result = await get_deepseek_output(system_prompt, user_prompt)
        assert result == "```jsonata\n$filter($, function($v) { $v.age > 30 })\n```"
        mock_client.chat.completions.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_model_output_jsonata_prefix(
    system_prompt, user_prompt, mock_groq_response
):
    """Test get_model_output handling of jsonata prefix."""
    mock_groq_response.choices[
        0
    ].message.content = "jsonata\n$filter($, function($v) { $v.age > 30 })"
    with patch("app.service.llm_api.AsyncGroq") as mock_groq:
        mock_client = mock_groq.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=mock_groq_response)
        result = await get_model_output(system_prompt, user_prompt, BaseModelType.groq)
        assert result == "$filter($, function($v) { $v.age > 30 })"


@pytest.mark.asyncio
async def test_get_model_output_no_code_block(
    system_prompt, user_prompt, mock_groq_response
):
    """Test get_model_output without code block."""
    mock_groq_response.choices[
        0
    ].message.content = "$filter($, function($v) { $v.age > 30 })"
    with patch("app.service.llm_api.AsyncGroq") as mock_groq:
        mock_client = mock_groq.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=mock_groq_response)
        result = await get_model_output(system_prompt, user_prompt, BaseModelType.groq)
        assert result == "$filter($, function($v) { $v.age > 30 })"
