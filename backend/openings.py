"""Chess opening book and position evaluation."""
from typing import Dict, List, Optional, Tuple, TypedDict, Literal
from typing_extensions import NotRequired

class SquareBonus(TypedDict):
    bonus: float
    description: NotRequired[str]

# Type definitions for board positions
CenterSquare = Tuple[Literal[3, 4], Literal[3, 4]]
ExtendedSquare = Tuple[Literal[2, 3, 4, 5], Literal[2, 3, 4, 5]]

# Simple opening book with common first moves
OPENING_BOOK = {
    # Empty board
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": [
        ("e2e4", "King's Pawn Opening"),
        ("d2d4", "Queen's Pawn Opening"),
        ("c2c4", "English Opening"),
        ("g1f3", "Reti Opening")
    ],
    # After 1. e4
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3": [
        ("e7e5", "Open Game"),
        ("c7c5", "Sicilian Defense"),
        ("e7e6", "French Defense"),
        ("c7c6", "Caro-Kann Defense")
    ],
    # After 1. d4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3": [
        ("d7d5", "Closed Game"),
        ("g8f6", "Indian Defense"),
        ("f7f5", "Dutch Defense"),
        ("d7d6", "Pirc Defense")
    ]
}

def evaluate_position(board: List[List[str]], color: str) -> float:
    """Evaluate chess position from given color's perspective."""
    piece_values = {
        'P': 1.0,   # Pawn
        'N': 3.0,   # Knight
        'B': 3.0,   # Bishop
        'R': 5.0,   # Rook
        'Q': 9.0,   # Queen
        'K': 0.0    # King (not counted in material)
    }
    
    # Center squares for piece-square tables
    center_squares: Dict[CenterSquare, SquareBonus] = {
        (3, 3): {"bonus": 0.3, "description": "center"},
        (3, 4): {"bonus": 0.3, "description": "center"},
        (4, 3): {"bonus": 0.3, "description": "center"},
        (4, 4): {"bonus": 0.3, "description": "center"}
    }
    
    # Extended center squares
    extended_center: Dict[ExtendedSquare, SquareBonus] = {
        (2, 2): {"bonus": 0.1}, (2, 3): {"bonus": 0.1},
        (2, 4): {"bonus": 0.1}, (2, 5): {"bonus": 0.1},
        (3, 2): {"bonus": 0.1}, (3, 5): {"bonus": 0.1},
        (4, 2): {"bonus": 0.1}, (4, 5): {"bonus": 0.1},
        (5, 2): {"bonus": 0.1}, (5, 3): {"bonus": 0.1},
        (5, 4): {"bonus": 0.1}, (5, 5): {"bonus": 0.1}
    }
    
    score = 0.0
    
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece == '.':
                continue
                
            # Get piece value
            value = piece_values.get(piece.upper(), 0)
            
            # Add/subtract based on piece color
            if (color == 'white' and piece.isupper()) or \
               (color == 'black' and piece.islower()):
                # Piece belongs to evaluated color
                score += value
                
                # Add positional bonus for center control
                # Type cast to handle position tuples
                pos = (i, j)
                if pos in center_squares:
                    score += center_squares[pos]["bonus"]
                elif pos in extended_center:
                    score += extended_center[pos]["bonus"]
                    
                # Pawn structure bonus
                if piece.upper() == 'P':
                    # Bonus for advanced pawns
                    rank_bonus = (7 - i if color == 'white' else i) * 0.1
                    score += rank_bonus
                    
                    # Penalty for doubled pawns
                    file_pawns = sum(1 for row in board if row[j].upper() == 'P')
                    if file_pawns > 1:
                        score -= 0.5
            else:
                # Piece belongs to opponent
                score -= value
                
    return score

def get_opening_move(fen: str) -> Optional[Tuple[str, str]]:
    """Get move from opening book if position exists."""
    if fen in OPENING_BOOK:
        moves = OPENING_BOOK[fen]
        # For now, always return first move. Could be randomized.
        return moves[0]
    return None
