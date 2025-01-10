import chess
from dotenv import load_dotenv
import os

class LLMInterface:
    def __init__(self, api_type, api_key=None):
        self.api_type = api_type
        self.api_key = api_key

    def generate_move(self, game_state):
        # TODO: Implement actual LLM move generation
        pass 