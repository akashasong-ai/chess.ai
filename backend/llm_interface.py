import chess
import openai
import anthropic
import httpx
import google.generativeai as generativeai
from typing import Dict, Any
from .config import get_ai_config
from openings import get_opening_move, evaluate_position

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
        elif self.api_type == 'perplexity':
            self.client = httpx.Client(
                base_url="https://api.perplexity.ai",
                headers={"Authorization": f"Bearer {config['api_key']}"},
                timeout=10.0
            )
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")

    async def generate_move(self, game_state: Dict[str, Any]) -> str:
        """Generate a move using the configured LLM."""
        # Convert game state to string representation
        board = chess.Board(game_state['fen']) if 'fen' in game_state else game_state['board']
        board_str = str(board)
        
        # Check opening book
        if 'fen' in game_state:
            opening_move = get_opening_move(game_state['fen'])
            if opening_move:
                move, opening_name = opening_move
                print(f"Using opening book: {opening_name}")
                return move
                
        # Get position evaluation
        position_score = evaluate_position(game_state['board'], game_state['currentPlayer'])
        
        # Get game context
        current_player = game_state.get('currentPlayer', 'white')
        last_move = game_state.get('lastMove', '')
        is_check = game_state.get('isCheck', False)
        
        # Create detailed prompt
        prompt = f"""You are playing a game of chess as {current_player}. Here is the current board state:
{board_str}

Game Context:
- You are playing as: {current_player.upper()}
- Last move by opponent: {last_move if last_move else 'Opening move'}
- Your king is in check: {'Yes' if is_check else 'No'}

Position Analysis:
- Current evaluation: {position_score:.2f} (positive favors you)
- Key considerations:
  * Control of center squares
  * Piece development and mobility
  * King safety and pawn structure
  * Material balance and tactical opportunities

Chess Strategy Guidelines:
1. Control the center (e4, d4, e5, d5)
2. Develop pieces efficiently (knights before bishops)
3. Protect your king (consider castling when safe)
4. Create and defend pawn structures
5. Look for tactical opportunities (pins, forks, discoveries)
6. Maintain material balance (unless sacrificing for advantage)

Generate a valid move in algebraic notation (e.g., 'e2e4' or 'g1f3').
Explain your strategic thinking, then provide ONLY the move notation on the last line."""

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
            
            elif self.api_type == 'perplexity':
                response = await self.client.post(
                    "/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100,
                        "temperature": 0.7
                    }
                )
                move = response.json()['choices'][0]['message']['content'].strip()
            
            # Extract move from response (last line)
            move_lines = move.strip().split('\n')
            final_move = move_lines[-1].strip()
            
            # Validate move format
            if len(final_move) >= 4 and all(c in 'abcdefgh12345678' for c in final_move[:4]):
                # Validate move is within board bounds
                from_file = ord(final_move[0]) - ord('a')
                from_rank = 8 - int(final_move[1])
                to_file = ord(final_move[2]) - ord('a')
                to_rank = 8 - int(final_move[3])
                
                if all(0 <= x <= 7 for x in [from_file, from_rank, to_file, to_rank]):
                    return final_move[:4]
                    
            raise ValueError(f"Invalid move format: {final_move}")
                
        except Exception as e:
            print(f"Error generating move with {self.api_type}: {str(e)}")
            # Return a default move in case of error (e2e4)
            return "e2e4"                                                      