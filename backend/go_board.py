class GoBoard:
    def __init__(self, size=9):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.current_player = 1  # 1 for black, 2 for white
        
    def get_state(self):
        return self.board
        
    def make_move(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size and self.board[y][x] == 0:
            self.board[y][x] = self.current_player
            # Switch player
            self.current_player = 2 if self.current_player == 1 else 1
            return True
        return False
        
    def __str__(self):
        """Convert board to string representation"""
        symbols = {0: '.', 1: '●', 2: '○'}
        rows = []
        # Add column labels
        cols = '   ' + ' '.join(chr(ord('A') + i) for i in range(self.size))
        rows.append(cols)
        # Add board rows with row numbers
        for i in range(self.size):
            row = f"{i+1:2d} " + ' '.join(symbols[cell] for cell in self.board[i])
            rows.append(row)
        return '\n'.join(rows) 