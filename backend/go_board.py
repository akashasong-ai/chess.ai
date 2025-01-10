class GoBoard:
    def __init__(self, size=9):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.current_player = 1  # 1 for black, 2 for white
        
    def get_state(self):
        return self.board
        
    def make_move(self, row, col, color):
        if 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == 0:
            self.board[row][col] = color
            self.current_player = 3 - self.current_player  # Switch between 1 and 2
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