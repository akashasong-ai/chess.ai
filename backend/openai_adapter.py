import openai
from llm_interface import LLMInterface

class OpenAIAdapter(LLMInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    async def generate_move(self, game_state: str) -> str:
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a chess engine."},
                    {"role": "user", "content": f"What is the best move for this game state: {game_state}"}
                ]
            )
            return response["choices"][0]["message"]["content"].strip()
        except openai.error.OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {e}")
