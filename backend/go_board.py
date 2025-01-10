class GoBoard:
    def __init__(self, size=19):
        self.size = size
        self.board = [['' for _ in range(size)] for _ in range(size)]
        self.current_player = 1  # 1 for black, 2 for white
        self.captured_black = 0
        self.captured_white = 0
        
    def make_move(self, x, y):
        if not self.is_valid_move(x, y):
            return False
            
        # Place stone
        self.board[y][x] = 'B' if self.current_player == 1 else 'W'
        
        # Check for captures
        captured = self.check_captures(x, y)
        if self.current_player == 1:
            self.captured_white += captured
        else:
            self.captured_black += captured
        
        # Switch current player
        self.current_player = 3 - self.current_player
        
        return True
        
    def is_valid_move(self, x, y):
        # Check if position is on board
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False
            
        # Check if position is empty
        if self.board[y][x]:
            return False
            
        return True
        
    def check_captures(self, x, y):
        # Implement capture rules here
        return 0
        
    def __str__(self):
        # Create board representation for printing
        rows = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                if self.board[i][j] == '':
                    row.append('.')
                else:
                    row.append(self.board[i][j])
            rows.append(' '.join(row))
        return '\n'.join(rows) 