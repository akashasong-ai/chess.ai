import chess
import openai
import anthropic
import google.generativeai as generativeai
from typing import Dict, Any
from config import get_ai_config

class LLMInterface:
    def __init__(self, player_id: str):
        config = get_ai_config(player_id)
        self.api_type = config['api_type']
        self.model = config['model']
        
        # Initialize API clients
        if self.api_type == 'openai':
            self.client = openai.OpenAI(api_key=config['api_key'])
        elif self.api_type == 'anthropic':
            self.client = anthropic.Anthropic(api_key=config['api_key'])
        elif self.api_type == 'google':
            generativeai.configure(api_key=config['api_key'])
            self.client = generativeai.GenerativeModel(self.model)
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")

    async def generate_move(self, game_state: Dict[str, Any]) -> str:
        """Generate a move using the configured LLM."""
        # Convert game state to string representation
        board_str = str(chess.Board(game_state['fen'])) if 'fen' in game_state else str(game_state['board'])
        prompt = f"""You are playing a game. Here is the current board state:
{board_str}

Generate a valid move in algebraic notation (e.g., 'e2e4' or 'g1f3').
Your move should be a single line containing only the move notation."""

        try:
            if self.api_type == 'openai':
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                move = response.choices[0].message.content.strip()
            
            elif self.api_type == 'anthropic':
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": prompt}]
                )
                move = response.content[0].text.strip()
            
            elif self.api_type == 'google':
                response = await self.client.generate_content(prompt)
                move = response.text.strip()
            
            # Validate move format (basic check)
            if len(move) >= 4 and all(c in 'abcdefgh12345678' for c in move[:4]):
                return move[:4]
            else:
                raise ValueError(f"Invalid move format: {move}")
                
        except Exception as e:
            print(f"Error generating move with {self.api_type}: {str(e)}")
            # Return a default move in case of error (e2e4)
            return "e2e4"   