# backend/claude_adapter.py
from llm_interface import LLMInterface
import httpx

class ClaudeAdapter(LLMInterface):
    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com"):
        self.api_key = api_key
        self.base_url = base_url

    async def generate_move(self, game_state: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generate_move",
                json={"game_state": game_state},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return response.json()["move"]
