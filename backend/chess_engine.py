class ChessGame:
    def __init__(self, player1, player2):
        self.player1 = player1  # White
        self.player2 = player2  # Black
        self.current_player = 'white'
        self.board = self.initialize_board()
        
    def initialize_board(self):
        # Capital letters for white pieces, lowercase for black
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
        
    def __str__(self):
        # Create the board display with coordinates
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
        
    def is_valid_move(self, from_pos, to_pos):
        # Basic validation
        if not (0 <= from_pos['row'] <= 7 and 0 <= from_pos['col'] <= 7):
            return False
        if not (0 <= to_pos['row'] <= 7 and 0 <= to_pos['col'] <= 7):
            return False
            
        # Get the piece
        piece = self.board[from_pos['row']][from_pos['col']]
        
        # Check if there's actually a piece to move
        if piece == '.':
            return False
            
        # Check if piece belongs to current player
        if self.current_player == 'white' and not piece.isupper():
            return False
        if self.current_player == 'black' and not piece.islower():
            return False
            
        # Check if destination has friendly piece
        dest_piece = self.board[to_pos['row']][to_pos['col']]
        if dest_piece != '.':
            if self.current_player == 'white' and dest_piece.isupper():
                return False
            if self.current_player == 'black' and dest_piece.islower():
                return False
                
        # Get piece type
        piece_type = piece.upper()
        
        # Pawn movement
        if piece_type == 'P':
            if self.current_player == 'white':
                # Normal move
                if from_pos['row'] - to_pos['row'] == 1 and from_pos['col'] == to_pos['col']:
                    return self.board[to_pos['row']][to_pos['col']] == '.'
                # Initial two-square move
                if from_pos['row'] == 6 and from_pos['row'] - to_pos['row'] == 2 and from_pos['col'] == to_pos['col']:
                    return (self.board[to_pos['row']][to_pos['col']] == '.' and 
                           self.board[to_pos['row']+1][to_pos['col']] == '.')
            else:
                # Normal move
                if to_pos['row'] - from_pos['row'] == 1 and from_pos['col'] == to_pos['col']:
                    return self.board[to_pos['row']][to_pos['col']] == '.'
                # Initial two-square move
                if from_pos['row'] == 1 and to_pos['row'] - from_pos['row'] == 2 and from_pos['col'] == to_pos['col']:
                    return (self.board[to_pos['row']][to_pos['col']] == '.' and 
                           self.board[to_pos['row']-1][to_pos['col']] == '.')
                           
        return True  # Temporarily allow other pieces to move anywhere
        
    def make_move(self, from_pos, to_pos):
        if not self.is_valid_move(from_pos, to_pos):
            return {'valid': False}
            
        # Make the move
        piece = self.board[from_pos['row']][from_pos['col']]
        self.board[from_pos['row']][from_pos['col']] = '.'
        self.board[to_pos['row']][to_pos['col']] = piece
        
        # Switch current player
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        return {'valid': True}
        
    def get_board(self):
        return self.board
        
    def get_status(self):
        return {
            'board': self.board,
            'currentPlayer': self.current_player
        }