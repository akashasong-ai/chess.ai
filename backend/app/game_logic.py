import chess
import openai
import google.generativeai as genai
from anthropic import Anthropic
from app.models import Game, LLM
from app import db
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure APIs
openai.api_key = Config.OPENAI_API_KEY
genai.configure(api_key=Config.GOOGLE_API_KEY)
anthropic = Anthropic(api_key=Config.ANTHROPIC_API_KEY)

class ChessGame:
    def __init__(self, white_llm_id, black_llm_id):
        self.board = chess.Board()
        self.white_llm = LLM.query.get(white_llm_id)
        self.black_llm = LLM.query.get(black_llm_id)
        self.game = Game(
            white_llm_id=white_llm_id,
            black_llm_id=black_llm_id
        )
        db.session.add(self.game)
        db.session.commit()

    def get_move_from_llm(self, llm, is_white):
        color = "White" if is_white else "Black"
        logger.info(f"Getting move for {llm.name} as {color}")
        logger.info(f"Current board position: {self.board.fen()}")
        logger.info(f"Legal moves: {', '.join(map(str, self.board.legal_moves))}")
        
        prompt = f"""You are playing chess as {color}. 
        The current board position in FEN is: {self.board.fen()}
        Legal moves are: {', '.join(map(str, self.board.legal_moves))}
        Provide your next move in algebraic notation (e.g., 'e2e4' or 'g1f3').
        Respond with only the move, no other text."""

        try:
            move_str = None
            
            if llm.api_type == 'openai':
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=10
                )
                move_str = response.choices[0].message.content.strip()

            elif llm.api_type == 'gemini':
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                move_str = response.text.strip()

            elif llm.api_type == 'claude':
                response = anthropic.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=10,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                move_str = response.content[0].text.strip()

            else:
                raise NotImplementedError(f"LLM type {llm.api_type} not supported")

            if move_str:
                logger.info(f"LLM {llm.name} returned move: {move_str}")
            else:
                logger.info(f"LLM {llm.name} failed to return a valid move")

            if move_str:
                try:
                    move = chess.Move.from_uci(move_str)
                    if move in self.board.legal_moves:
                        return move
                except:
                    # Try parsing as SAN if UCI fails
                    try:
                        move = self.board.parse_san(move_str)
                        if move in self.board.legal_moves:
                            return move
                    except:
                        pass
            return None

        except Exception as e:
            print(f"Error getting move from {llm.api_type}: {str(e)}")
            return None

    def play_game(self):
        while not self.board.is_game_over():
            is_white = self.board.turn
            current_llm = self.white_llm if is_white else self.black_llm
            
            move = self.get_move_from_llm(current_llm, is_white)
            if move is None:
                # Invalid move, current player forfeits
                self.game.result = '0-1' if is_white else '1-0'
                break

            self.board.push(move)
            self.game.moves = self.game.moves + f" {move}"
            db.session.commit()

        if self.game.result is None:
            # Game ended normally
            if self.board.is_checkmate():
                self.game.result = '1-0' if not self.board.turn else '0-1'
            else:
                self.game.result = '1/2-1/2'

        self.update_ratings()
        db.session.commit()
        return self.game.result

    def update_ratings(self):
        # Simple Elo rating update
        k_factor = 32
        r1 = 10 ** (self.white_llm.elo_rating / 400)
        r2 = 10 ** (self.black_llm.elo_rating / 400)
        e1 = r1 / (r1 + r2)
        e2 = r2 / (r1 + r2)

        if self.game.result == '1-0':
            s1, s2 = 1, 0
        elif self.game.result == '0-1':
            s1, s2 = 0, 1
        else:
            s1, s2 = 0.5, 0.5

        self.white_llm.elo_rating += k_factor * (s1 - e1)
        self.black_llm.elo_rating += k_factor * (s2 - e2) 