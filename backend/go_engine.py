import numpy as np
from typing import List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Position:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

class GoBoard:
    def __init__(self, size=19):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.current_player = 1  # 1 for black, 2 for white
        self.captured_black = 0
        self.captured_white = 0
        self.move_history = []  # For ko rule checking
        self.territory_black = 0
        self.territory_white = 0
        
    def is_valid_move(self, x: int, y: int) -> bool:
        """Check if a move is valid according to Go rules."""
        # Basic boundary and occupation checks
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False
        if self.board[x][y] != 0:
            return False
            
        # Make temporary move to check captures and suicide rule
        self.board[x][y] = self.current_player
        
        # Check for captures
        opponent = 3 - self.current_player
        captured_groups = []
        for nx, ny in self._get_neighbors(x, y):
            if self.board[nx][ny] == opponent:
                group = self._get_group(nx, ny)
                if self._count_liberties(group) == 0:
                    captured_groups.append(group)
        
        # If no captures, check for suicide rule
        if not captured_groups:
            own_group = self._get_group(x, y)
            if self._count_liberties(own_group) == 0:
                self.board[x][y] = 0  # Undo temporary move
                return False
                
        # Check ko rule
        if len(self.move_history) >= 2:
            potential_board = self.board.copy()
            for group in captured_groups:
                for pos in group:
                    potential_board[pos.x][pos.y] = 0
            if any(np.array_equal(potential_board, prev_board) for prev_board in self.move_history[-2:]):
                self.board[x][y] = 0  # Undo temporary move
                return False
        
        self.board[x][y] = 0  # Undo temporary move
        return True
        
    def make_move(self, x: int, y: int) -> bool:
        """Make a move and handle captures."""
        if not self.is_valid_move(x, y):
            return False
            
        # Store previous board state for ko rule
        self.move_history.append(self.board.copy())
        if len(self.move_history) > 2:
            self.move_history.pop(0)
            
        # Place stone
        self.board[x][y] = self.current_player
        
        # Handle captures
        opponent = 3 - self.current_player
        for nx, ny in self._get_neighbors(x, y):
            if self.board[nx][ny] == opponent:
                group = self._get_group(nx, ny)
                if self._count_liberties(group) == 0:
                    self._remove_group(group)
                    
        # Switch players
        self.current_player = opponent
        return True
        
    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring positions."""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors
        
    def _get_group(self, x: int, y: int) -> Set[Position]:
        """Find all connected stones of the same color."""
        color = self.board[x][y]
        if color == 0:
            return set()
            
        group = set()
        to_check = {Position(x, y)}
        
        while to_check:
            pos = to_check.pop()
            if pos in group:
                continue
            group.add(pos)
            
            for nx, ny in self._get_neighbors(pos.x, pos.y):
                if self.board[nx][ny] == color:
                    new_pos = Position(nx, ny)
                    if new_pos not in group:
                        to_check.add(new_pos)
        
        return group
        
    def _count_liberties(self, group: Set[Position]) -> int:
        """Count the number of liberties for a group of stones."""
        liberties = set()
        for pos in group:
            for nx, ny in self._get_neighbors(pos.x, pos.y):
                if self.board[nx][ny] == 0:
                    liberties.add(Position(nx, ny))
        return len(liberties)
        
    def _remove_group(self, group: Set[Position]) -> None:
        """Remove a captured group and update capture counts."""
        first_stone = next(iter(group))
        captured_color = self.board[first_stone.x][first_stone.y]
        
        for pos in group:
            self.board[pos.x][pos.y] = 0
            
        if captured_color == 1:  # Black
            self.captured_black += len(group)
        else:  # White
            self.captured_white += len(group)
            
    def calculate_territory(self) -> Tuple[int, int]:
        """Calculate territory control at the end of the game."""
        territory = np.zeros((self.size, self.size), dtype=int)
        visited = set()
        
        for x in range(self.size):
            for y in range(self.size):
                if Position(x, y) in visited or self.board[x][y] != 0:
                    continue
                    
                # Find empty region
                region = self._get_empty_region(x, y)
                visited.update(region)
                
                # Determine territory owner
                owner = self._get_territory_owner(region)
                if owner:
                    for pos in region:
                        territory[pos.x][pos.y] = owner
                        
        self.territory_black = np.sum(territory == 1)
        self.territory_white = np.sum(territory == 2)
        return self.territory_black, self.territory_white
        
    def _get_empty_region(self, x: int, y: int) -> Set[Position]:
        """Find connected empty positions."""
        region = set()
        to_check = {Position(x, y)}
        
        while to_check:
            pos = to_check.pop()
            if pos in region:
                continue
            region.add(pos)
            
            for nx, ny in self._get_neighbors(pos.x, pos.y):
                if self.board[nx][ny] == 0:
                    new_pos = Position(nx, ny)
                    if new_pos not in region:
                        to_check.add(new_pos)
        
        return region
        
    def _get_territory_owner(self, region: Set[Position]) -> Optional[int]:
        """Determine if a region is territory of either player."""
        borders = set()
        for pos in region:
            for nx, ny in self._get_neighbors(pos.x, pos.y):
                if self.board[nx][ny] != 0:
                    borders.add(self.board[nx][ny])
                    
        if len(borders) == 1:  # Region is surrounded by one color
            return borders.pop()
        return None
        
    def get_score(self) -> Tuple[float, float]:
        """Get final score (territory + captures)."""
        territory_black, territory_white = self.calculate_territory()
        black_score = territory_black + self.captured_white
        white_score = territory_white + self.captured_black + 6.5  # Komi
        return black_score, white_score
        
    def __str__(self) -> str:
        """Return string representation of the board."""
        symbols = {0: '.', 1: '●', 2: '○'}
        rows = []
        for i in range(self.size):
            row = ' '.join(symbols[self.board[i][j]] for j in range(self.size))
            rows.append(f"{19-i:2d} {row}")
        
        # Add column coordinates
        columns = '    ' + ' '.join(chr(ord('A') + i) for i in range(self.size))
        return columns + '\n' + '\n'.join(rows)
