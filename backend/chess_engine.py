from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

@dataclass
class Position:
    row: int
    col: int

    def __str__(self) -> str:
        return f"{chr(self.col + 97)}{8 - self.row}"

class ChessGame:
    def __init__(self, player1: str, player2: str):
        self.player1 = player1  # White
        self.player2 = player2  # Black
        self.current_player = 'white'
        self.board = self.initialize_board()
        self.move_history: List[Tuple[Position, Position]] = []
        self.castling_rights = {
            'white': {'kingside': True, 'queenside': True},
            'black': {'kingside': True, 'queenside': True}
        }
        self.en_passant_target: Optional[Position] = None
        self.is_check = False
        self.is_checkmate = False
        self.is_stalemate = False
        
    def initialize_board(self) -> List[List[str]]:
        """Initialize the chess board with pieces in starting positions."""
        board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        return board
        
    def is_valid_move(self, from_pos: Dict[str, int], to_pos: Dict[str, int]) -> bool:
        """Check if a move is valid according to chess rules."""
        # Convert dictionary positions to Position objects
        from_square = Position(from_pos['row'], from_pos['col'])
        to_square = Position(to_pos['row'], to_pos['col'])
        
        # Basic validation
        if not self._is_within_bounds(from_square) or not self._is_within_bounds(to_square):
            return False
            
        # Get the piece
        piece = self.board[from_square.row][from_square.col]
        
        # Check if there's actually a piece to move
        if piece == '.':
            return False
            
        # Check if piece belongs to current player
        if not self._is_current_players_piece(piece):
            return False
            
        # Check if destination has friendly piece
        dest_piece = self.board[to_square.row][to_square.col]
        if dest_piece != '.' and self._is_friendly_piece(dest_piece):
            return False
            
        # Get piece type and validate movement
        piece_type = piece.upper()
        
        # Check specific piece movement
        if not self._is_valid_piece_movement(piece_type, from_square, to_square):
            return False
            
        # Make temporary move to check for check
        self._make_temporary_move(from_square, to_square)
        in_check = self._is_in_check(self.current_player)
        self._undo_temporary_move(from_square, to_square)
        
        if in_check:
            return False
            
        return True
        
    def _is_within_bounds(self, pos: Position) -> bool:
        """Check if position is within board boundaries."""
        return 0 <= pos.row <= 7 and 0 <= pos.col <= 7
        
    def _is_current_players_piece(self, piece: str) -> bool:
        """Check if piece belongs to current player."""
        return (self.current_player == 'white' and piece.isupper()) or \
               (self.current_player == 'black' and piece.islower())
               
    def _is_friendly_piece(self, piece: str) -> bool:
        """Check if piece belongs to current player."""
        return (self.current_player == 'white' and piece.isupper()) or \
               (self.current_player == 'black' and piece.islower())
               
    def _is_valid_piece_movement(self, piece_type: str, from_pos: Position, to_pos: Position) -> bool:
        """Validate piece-specific movement patterns."""
        dx = to_pos.row - from_pos.row
        dy = to_pos.col - from_pos.col
        
        if piece_type == 'P':
            return self._is_valid_pawn_move(from_pos, to_pos)
        elif piece_type == 'R':
            return self._is_valid_rook_move(from_pos, to_pos)
        elif piece_type == 'N':
            return self._is_valid_knight_move(dx, dy)
        elif piece_type == 'B':
            return self._is_valid_bishop_move(from_pos, to_pos)
        elif piece_type == 'Q':
            return self._is_valid_queen_move(from_pos, to_pos)
        elif piece_type == 'K':
            return self._is_valid_king_move(from_pos, to_pos)
        return False
        
    def _is_valid_pawn_move(self, from_pos: Position, to_pos: Position) -> bool:
        """Validate pawn movement including captures and en passant."""
        direction = -1 if self.current_player == 'white' else 1
        start_row = 6 if self.current_player == 'white' else 1
        
        # Normal move
        if to_pos.col == from_pos.col:
            if from_pos.row + direction == to_pos.row:
                return self.board[to_pos.row][to_pos.col] == '.'
            # Initial two-square move
            if from_pos.row == start_row and from_pos.row + 2 * direction == to_pos.row:
                middle_row = from_pos.row + direction
                return (self.board[to_pos.row][to_pos.col] == '.' and 
                       self.board[middle_row][to_pos.col] == '.')
                       
        # Diagonal capture
        if abs(to_pos.col - from_pos.col) == 1 and to_pos.row == from_pos.row + direction:
            # Normal capture
            if self.board[to_pos.row][to_pos.col] != '.':
                return not self._is_friendly_piece(self.board[to_pos.row][to_pos.col])
            # En passant
            if self.en_passant_target and \
               self.en_passant_target.row == to_pos.row and \
               self.en_passant_target.col == to_pos.col:
                return True
                
        return False
        
    def _is_valid_rook_move(self, from_pos: Position, to_pos: Position) -> bool:
        """Validate rook movement."""
        if from_pos.row != to_pos.row and from_pos.col != to_pos.col:
            return False
        return self._is_path_clear(from_pos, to_pos)
        
    def _is_valid_knight_move(self, dx: int, dy: int) -> bool:
        """Validate knight movement."""
        return (abs(dx) == 2 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 2)
        
    def _is_valid_bishop_move(self, from_pos: Position, to_pos: Position) -> bool:
        """Validate bishop movement."""
        if abs(to_pos.row - from_pos.row) != abs(to_pos.col - from_pos.col):
            return False
        return self._is_path_clear(from_pos, to_pos)
        
    def _is_valid_queen_move(self, from_pos: Position, to_pos: Position) -> bool:
        """Validate queen movement."""
        is_diagonal = abs(to_pos.row - from_pos.row) == abs(to_pos.col - from_pos.col)
        is_straight = from_pos.row == to_pos.row or from_pos.col == to_pos.col
        return (is_diagonal or is_straight) and self._is_path_clear(from_pos, to_pos)
        
    def _is_valid_king_move(self, from_pos: Position, to_pos: Position) -> bool:
        """Validate king movement including castling."""
        dx = abs(to_pos.row - from_pos.row)
        dy = abs(to_pos.col - from_pos.col)
        
        # Normal king move
        if dx <= 1 and dy <= 1:
            return True
            
        # Castling
        if dx == 0 and dy == 2 and not self.is_check:
            if self.current_player == 'white':
                if from_pos.row == 7 and from_pos.col == 4:
                    # Kingside castling
                    if to_pos.col == 6 and self.castling_rights['white']['kingside']:
                        return self._can_castle_kingside('white')
                    # Queenside castling
                    if to_pos.col == 2 and self.castling_rights['white']['queenside']:
                        return self._can_castle_queenside('white')
            else:
                if from_pos.row == 0 and from_pos.col == 4:
                    # Kingside castling
                    if to_pos.col == 6 and self.castling_rights['black']['kingside']:
                        return self._can_castle_kingside('black')
                    # Queenside castling
                    if to_pos.col == 2 and self.castling_rights['black']['queenside']:
                        return self._can_castle_queenside('black')
                        
        return False
        
    def _is_path_clear(self, from_pos: Position, to_pos: Position) -> bool:
        """Check if path between two positions is clear of pieces."""
        dx = to_pos.row - from_pos.row
        dy = to_pos.col - from_pos.col
        
        if dx == 0 and dy == 0:
            return True
            
        step_x = 0 if dx == 0 else dx // abs(dx)
        step_y = 0 if dy == 0 else dy // abs(dy)
        
        current_x = from_pos.row + step_x
        current_y = from_pos.col + step_y
        
        while current_x != to_pos.row or current_y != to_pos.col:
            if self.board[current_x][current_y] != '.':
                return False
            current_x += step_x
            current_y += step_y
            
        return True
        
    def _can_castle_kingside(self, color: str) -> bool:
        """Check if kingside castling is possible."""
        row = 7 if color == 'white' else 0
        return (self.board[row][5] == '.' and 
                self.board[row][6] == '.' and 
                self.board[row][7] in 'Rr' and
                not self._is_square_attacked(Position(row, 4), color) and
                not self._is_square_attacked(Position(row, 5), color) and
                not self._is_square_attacked(Position(row, 6), color))
                
    def _can_castle_queenside(self, color: str) -> bool:
        """Check if queenside castling is possible."""
        row = 7 if color == 'white' else 0
        return (self.board[row][3] == '.' and 
                self.board[row][2] == '.' and 
                self.board[row][1] == '.' and
                self.board[row][0] in 'Rr' and
                not self._is_square_attacked(Position(row, 4), color) and
                not self._is_square_attacked(Position(row, 3), color) and
                not self._is_square_attacked(Position(row, 2), color))
                
    def _is_square_attacked(self, pos: Position, defending_color: str) -> bool:
        """Check if a square is attacked by any opponent piece."""
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece != '.' and self._is_opponent_piece(piece, defending_color):
                    from_pos = Position(i, j)
                    if self._is_valid_piece_movement(piece.upper(), from_pos, pos):
                        if self._is_path_clear(from_pos, pos):
                            return True
        return False
        
    def _is_opponent_piece(self, piece: str, defending_color: str) -> bool:
        """Check if piece belongs to opponent."""
        return (defending_color == 'white' and piece.islower()) or \
               (defending_color == 'black' and piece.isupper())
               
    def _is_in_check(self, color: str) -> bool:
        """Check if the specified color's king is in check."""
        # Find king position
        king_char = 'K' if color == 'white' else 'k'
        king_pos = None
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == king_char:
                    king_pos = Position(i, j)
                    break
            if king_pos:
                break
                
        if not king_pos:
            # This shouldn't happen in a valid game state
            return False
                
        return self._is_square_attacked(king_pos, color)
        
    def _make_temporary_move(self, from_pos: Position, to_pos: Position) -> None:
        """Make a temporary move to test for check."""
        self.temp_piece = self.board[to_pos.row][to_pos.col]
        self.board[to_pos.row][to_pos.col] = self.board[from_pos.row][from_pos.col]
        self.board[from_pos.row][from_pos.col] = '.'
        
    def _undo_temporary_move(self, from_pos: Position, to_pos: Position) -> None:
        """Undo a temporary move."""
        self.board[from_pos.row][from_pos.col] = self.board[to_pos.row][to_pos.col]
        self.board[to_pos.row][to_pos.col] = self.temp_piece
        
    def make_move(self, from_pos: Dict[str, int], to_pos: Dict[str, int]) -> Dict[str, bool]:
        """Make a move and update game state."""
        if not self.is_valid_move(from_pos, to_pos):
            return {'valid': False}
            
        from_square = Position(from_pos['row'], from_pos['col'])
        to_square = Position(to_pos['row'], to_pos['col'])
        
        # Store move for history
        self.move_history.append((from_square, to_square))
        
        piece = self.board[from_square.row][from_square.col]
        piece_type = piece.upper()
        
        # Handle castling
        if piece_type == 'K' and abs(to_square.col - from_square.col) == 2:
            self._handle_castling(from_square, to_square)
            
        # Handle en passant capture
        elif piece_type == 'P' and self.en_passant_target and \
             to_square.row == self.en_passant_target.row and \
             to_square.col == self.en_passant_target.col:
            self._handle_en_passant(from_square, to_square)
            
        # Normal move
        else:
            self.board[to_square.row][to_square.col] = piece
            self.board[from_square.row][from_square.col] = '.'
            
        # Update castling rights
        self._update_castling_rights(piece_type, from_square)
        
        # Update en passant target
        self._update_en_passant_target(piece_type, from_square, to_square)
        
        # Switch current player
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        # Update check status
        self.is_check = self._is_in_check(self.current_player)
        
        return {'valid': True}
        
    def _handle_castling(self, from_pos: Position, to_pos: Position) -> None:
        """Handle castling move."""
        # Move king
        self.board[to_pos.row][to_pos.col] = self.board[from_pos.row][from_pos.col]
        self.board[from_pos.row][from_pos.col] = '.'
        
        # Move rook
        if to_pos.col == 6:  # Kingside
            self.board[to_pos.row][5] = self.board[to_pos.row][7]
            self.board[to_pos.row][7] = '.'
        else:  # Queenside
            self.board[to_pos.row][3] = self.board[to_pos.row][0]
            self.board[to_pos.row][0] = '.'
            
    def _handle_en_passant(self, from_pos: Position, to_pos: Position) -> None:
        """Handle en passant capture."""
        # Move pawn
        self.board[to_pos.row][to_pos.col] = self.board[from_pos.row][from_pos.col]
        self.board[from_pos.row][from_pos.col] = '.'
        
        # Remove captured pawn
        capture_row = from_pos.row
        self.board[capture_row][to_pos.col] = '.'
        
    def _update_castling_rights(self, piece_type: str, from_pos: Position) -> None:
        """Update castling rights when king or rook moves."""
        if piece_type == 'K':
            if self.current_player == 'white':
                self.castling_rights['white'] = {'kingside': False, 'queenside': False}
            else:
                self.castling_rights['black'] = {'kingside': False, 'queenside': False}
        elif piece_type == 'R':
            if self.current_player == 'white':
                if from_pos.row == 7:
                    if from_pos.col == 0:
                        self.castling_rights['white']['queenside'] = False
                    elif from_pos.col == 7:
                        self.castling_rights['white']['kingside'] = False
            else:
                if from_pos.row == 0:
                    if from_pos.col == 0:
                        self.castling_rights['black']['queenside'] = False
                    elif from_pos.col == 7:
                        self.castling_rights['black']['kingside'] = False
                        
    def _update_en_passant_target(self, piece_type: str, from_pos: Position, to_pos: Position) -> None:
        """Update en passant target square when pawn moves two squares."""
        self.en_passant_target = None
        if piece_type == 'P' and abs(to_pos.row - from_pos.row) == 2:
            self.en_passant_target = Position(
                (from_pos.row + to_pos.row) // 2,
                to_pos.col
            )
            
    def get_board(self) -> List[List[str]]:
        """Get current board state."""
        return self.board
        
    def get_status(self) -> Dict:
        """Get current game status."""
        return {
            'board': self.board,
            'currentPlayer': self.current_player,
            'isCheck': self.is_check,
            'isCheckmate': self.is_checkmate,
            'isStalemate': self.is_stalemate,
            'enPassantTarget': self.en_passant_target,
            'castlingRights': self.castling_rights
        }
        
    def __str__(self) -> str:
        """Return string representation of the board."""
        display = "\n  a b c d e f g h\n"
        display += "  ---------------\n"
        for i in range(8):
            display += f"{8-i}|"
            for j in range(8):
                display += f"{self.board[i][j]}|"
            display += f"{8-i}\n"
        display += "  ---------------\n"
        display += "  a b c d e f g h\n"
        return display
