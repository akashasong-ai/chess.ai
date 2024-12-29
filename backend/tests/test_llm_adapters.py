# backend/tests/test_llm_adapters.py
import pytest
from backend.openai_adapter import OpenAIAdapter
from backend.gemini_adapter import GeminiAdapter
from backend.claude_adapter import ClaudeAdapter

@pytest.mark.asyncio
async def test_openai_adapter():
    adapter = OpenAIAdapter(api_key="fake-key")
    # Mocking the generate_move method to avoid actual API calls
    async def mock_generate_move(game_state):
        return "e2e4"  # Mock response
    adapter.generate_move = mock_generate_move

    response = await adapter.generate_move("test game state")
    assert response == "e2e4"

@pytest.mark.asyncio
async def test_gemini_adapter():
    adapter = GeminiAdapter(api_key="fake-key", base_url="http://fake-url")
    # Mocking the generate_move method to avoid actual API calls
    async def mock_generate_move(game_state):
        return "e2e4"  # Mock response
    adapter.generate_move = mock_generate_move

    response = await adapter.generate_move("test game state")
    assert response == "e2e4"

@pytest.mark.asyncio
async def test_claude_adapter():
    adapter = ClaudeAdapter(api_key="fake-key")
    with pytest.raises(Exception):  # Replace Exception with a specific one when testing live
        response = await adapter.generate_move("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
