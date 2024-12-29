import httpx
from llm_interface import LLMInterface

class GeminiAdapter(LLMInterface):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    async def generate_move(self, game_state: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generate_move",
                    json={"game_state": game_state},
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                return response.json()["move"]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error while communicating with Gemini API: {e}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error while communicating with Gemini API: {e}")
