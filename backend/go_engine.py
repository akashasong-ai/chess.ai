import numpy as np

class GoBoard:
    def __init__(self, size=19):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.current_player = 1  # 1 for black, 2 for white
        self.captured_black = 0
        self.captured_white = 0
        
    def is_valid_move(self, x, y):
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False
        return self.board[x][y] == 0
        
    def make_move(self, x, y):
        if not self.is_valid_move(x, y):
            return False
        self.board[x][y] = self.current_player
        self.current_player = 3 - self.current_player  # Switch players
        return True
        
    def __str__(self):
        return str(self.board)