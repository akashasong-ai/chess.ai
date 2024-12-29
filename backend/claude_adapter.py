import requests
from llm_interface import LLMInterface

class ClaudeAdapter(LLMInterface):
    def __init__(self, api_key: str, base_url: str = "https://api.claude.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url

    async def generate_move(self, game_state: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"prompt": f"Make the best move for this game state: {game_state}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/chat", json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("text", "").strip()
