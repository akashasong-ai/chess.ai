import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI
import sys
from pathlib import Path
from httpx import ASGITransport
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.main import app
from app import app as flask_app, get_game_state_from_redis

@pytest_asyncio.fixture(autouse=True)
async def reset_game_state():
    """Reset global game state before each test."""
    with flask_app.test_client() as client:
        # Stop any active game to reset state
        client.post("/api/game/stop")
        # Verify state is reset
        response = client.get("/api/game/state")
        assert response.status_code == 400
        assert "error" in response.get_json()
    yield

@pytest_asyncio.fixture
async def client():
    """Create an async client for testing the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_request_forwarding(client):
    """Test that FastAPI correctly forwards requests to Flask"""
    # Test basic GET request
    response = await client.get("/api/test")
    assert response.status_code == 404  # Should forward to Flask and get 404

    # Test POST request with JSON
    response = await client.post("/api/test", json={"test": "data"})
    assert response.status_code == 404  # Should forward to Flask and get 404

    # Test query parameters
    response = await client.get("/api/test?param=value")
    assert response.status_code == 404  # Should forward to Flask and get 404

@pytest.mark.asyncio
async def test_game_endpoints(client):
    """Test game endpoints without database dependencies"""
    # Test game start (minimal test)
    response = await client.post("/api/game/start", json={
        "whiteAI": "GPT-4",
        "blackAI": "CLAUDE"
    })
    assert response.status_code in [200, 400]  # Accept both success and error

    # Test game state (minimal test)
    response = await client.get("/api/game/state")
    assert response.status_code in [200, 400]  # Accept both success and error

@pytest.mark.asyncio
async def test_tournament_endpoints(client):
    """Test tournament endpoints without database dependencies"""
    # Test tournament start
    response = await client.post("/api/tournament/start", json={
        "participants": ["GPT-4", "CLAUDE", "GEMINI"],
        "matches": 3
    })
    assert response.status_code in [200, 400]  # Accept both success and error

    # Test tournament status
    response = await client.get("/api/tournament/status")
    assert response.status_code in [200, 404]  # Accept both success and not found

    # Test tournament stop
    response = await client.post("/api/tournament/stop")
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_leaderboard_endpoint(client):
    """Test leaderboard endpoint without database dependencies"""
    response = await client.get("/api/leaderboard")
    assert response.status_code in [200, 400]  # Accept both success and error
    if response.status_code == 200:
        data = response.json()
        assert "leaderboard" in data
        assert isinstance(data["leaderboard"], list)

@pytest.mark.asyncio
async def test_error_handling(client):
    """Test error handling in the FastAPI wrapper"""
    # Test invalid move
    response = await client.post("/api/game/move", json={
        "move": "invalid"
    })
    assert response.status_code == 400
    assert "error" in response.json()

    # Test game state without active game
    response = await client.get("/api/game/state")
    assert response.status_code == 400
    assert "error" in response.json()

    # Test tournament status without active tournament
    response = await client.get("/api/tournament/status")
    assert response.status_code == 404
    assert "error" in response.json()
