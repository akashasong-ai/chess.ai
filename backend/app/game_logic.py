import chess
from datetime import datetime
from .models import Game, LLM
from . import db
from config import Config

class ChessGame:
    def __init__(self, white_llm_id, black_llm_id):
        self.board = chess.Board()
        self.white_llm = LLM.query.get(white_llm_id)
        self.black_llm = LLM.query.get(black_llm_id)
        self.game = Game(
            white_llm_id=white_llm_id,
            black_llm_id=black_llm_id,
            started_at=datetime.utcnow()
        )
        db.session.add(self.game)
        db.session.commit()
        
    def get_next_move(self, llm, board_state):
        # TODO: Implement LLM-specific move generation based on api_type
        # For now, just make a random legal move
        legal_moves = list(self.board.legal_moves)
        if legal_moves:
            return legal_moves[0]
        return None
        
    def play_game(self, max_moves=100):
        moves = []
        
        for move_num in range(max_moves):
            if self.board.is_game_over():
                break
                
            current_llm = self.white_llm if self.board.turn else self.black_llm
            move = self.get_next_move(current_llm, self.board.fen())
            
            if move is None:
                break
                
            self.board.push(move)
            moves.append(move.uci())
            
        # Update game record
        self.game.moves = ' '.join(moves)
        self.game.ended_at = datetime.utcnow()
        
        # Determine result
        if self.board.is_checkmate():
            winner = self.white_llm if not self.board.turn else self.black_llm
            self.game.result = f"{winner.name} wins by checkmate"
        elif self.board.is_stalemate():
            self.game.result = "Draw by stalemate"
        elif self.board.is_insufficient_material():
            self.game.result = "Draw by insufficient material"
        elif self.board.is_fifty_moves():
            self.game.result = "Draw by fifty-move rule"
        elif self.board.is_repetition():
            self.game.result = "Draw by repetition"
        else:
            self.game.result = "Game abandoned"
            
        # Update LLM ratings
        # TODO: Implement proper Elo rating updates
        
        db.session.commit()
        return self.game.result 