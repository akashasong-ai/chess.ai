import pytest
from backend.openai_adapter import OpenAIAdapter
from backend.gemini_adapter import GeminiAdapter

@pytest.mark.asyncio
async def test_openai_adapter():
    adapter = OpenAIAdapter(api_key="fake-key")
    response = await adapter.send_query("Hello")
    assert response == "OpenAI Mock Response"

@pytest.mark.asyncio
async def test_gemini_adapter():
    adapter = GeminiAdapter(api_key="fake-key")
    response = await adapter.send_query("Hello")
    assert response == "Gemini Mock Response"
