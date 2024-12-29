from llm_interface import LLMInterface

class LlamaAdapter(LLMInterface):
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None

    def load_model(self):
        from llama import Llama
        self.model = Llama.load_model(self.model_path)

    async def generate_move(self, game_state: str) -> str:
        if self.model is None:
            self.load_model()

        response = self.model.chat(
            instruction="You are a chess engine.",
            inputs=f"What is the best move for this game state: {game_state}",
            max_tokens=200,
        )
        return response["text"].strip()
