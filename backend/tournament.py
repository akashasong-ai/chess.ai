import random
import time
from chess_engine import ChessGame
from go_board import GoBoard

from typing import List, Dict, Optional, Literal, TypedDict, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random

class MoveResult(TypedDict, total=False):
    valid: bool
    move: Dict[str, str]
    checkmate: bool
    resignation: bool
    draw: bool
    message: str

@dataclass
class Match:
    player1: str
    player2: str
    game_type: Literal['chess', 'go']
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    winner: Optional[str] = None
    moves: List[Dict[str, str]] = field(default_factory=list)  # List of move dictionaries
    time_control: int = 600  # Time in seconds per player (default 10 minutes)
    board_size: int = 19  # Board size for Go games (default 19x19)

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.moves is None:
            self.moves = []
        if self.time_control <= 0:
            self.time_control = 600
        if self.board_size < 9:  # Minimum Go board size
            self.board_size = 19

class Tournament:
    def __init__(self, game_type: str, players: List[str], 
                 num_games: int = 1, time_control: int = 600):  # Default 10 minutes per player
        self.game_type = game_type
        self.players = players
        self.num_games = num_games
        self.time_control = time_control
        self.matches: List[Match] = []
        self.rankings: Dict[str, Dict[str, int]] = {
            player: {'wins': 0, 'draws': 0, 'losses': 0, 'score': 0}
            for player in players
        }
        self.completed = False
        self.current_round = 0
        
    def create_round_robin_matches(self) -> List[Match]:
        """Generate round-robin tournament pairings."""
        matches = []
        for i in range(len(self.players)):
            for j in range(i + 1, len(self.players)):
                for _ in range(self.num_games):
                    # Randomly assign colors/sides
                    if random.random() > 0.5:
                        player1, player2 = self.players[i], self.players[j]
                    else:
                        player1, player2 = self.players[j], self.players[i]
                    
                    match = Match(
                        player1=player1,
                        player2=player2,
                        game_type=self.game_type,
                        time_control=self.time_control
                    )
                    matches.append(match)
        return matches

    def start(self):
        """Start the tournament and create match schedule."""
        print("\n=== Starting Tournament ===")
        print(f"Game: {self.game_type}")
        print(f"Players: {', '.join(self.players)}")
        print(f"Time Control: {self.time_control} seconds per player")
        print("=========================\n")
        
        # Create round-robin matches
        self.matches = self.create_round_robin_matches()
        
        # Start first match
        if self.matches:
            self.current_round = 1
            return self.get_next_match()
        
        self.completed = True
        self.show_rankings()
    
    def play_match(self, match: Match) -> None:
        """Play a match between two AI players with time control."""
        print(f"\n{'='*40}")
        print(f"Match: {match.player1} (White) vs {match.player2} (Black)")
        print(f"Time Control: {match.time_control} seconds per player")
        print(f"{'='*40}\n")
        
        if match.game_type == 'chess':
            game = ChessGame(match.player1, match.player2)
        else:
            game = GoBoard(size=match.board_size)
            
        # Initialize time tracking
        # Initialize time control with type safety
        time_left: Dict[str, float] = {
            match.player1: float(match.time_control),
            match.player2: float(match.time_control)
        }
        
        moves = 0
        while moves < 100:  # Maximum 100 moves per game
            print(f"\nMove {moves + 1}")
            print(game)
            
            current_player = match.player1 if moves % 2 == 0 else match.player2
            print(f"{current_player}'s turn (Time left: {time_left[current_player]}s)")
            
            # Record move start time
            move_start = datetime.now()
            
            # Make move
            result = self.make_ai_move(game)
            
            # Update time control
            move_duration = (datetime.now() - move_start).total_seconds()
            time_left[current_player] -= move_duration
            
            # Check for time forfeit
            if time_left[current_player] <= 0:
                print(f"{current_player} lost on time!")
                match.winner = match.player2 if current_player == match.player1 else match.player1
                match.end_time = datetime.now()
                self.update_rankings(match, 'loss' if current_player == match.player1 else 'win')
                return
            
            # Type guard for result validation
            if not isinstance(result, dict) or not result.get('valid', False):
                print("Invalid move result")
                continue
                
            # Record move with validation
            move_data = result.get('move')
            if isinstance(move_data, dict) and all(
                isinstance(k, str) and isinstance(v, str) 
                for k, v in move_data.items()
            ):
                match.moves.append(move_data)
                moves += 1
            else:
                print(f"Invalid move format: {move_data}")
                continue
            
            # Check for game end conditions with type safety
            is_checkmate = bool(result.get('checkmate', False))
            is_resignation = bool(result.get('resignation', False))
            is_draw = bool(result.get('draw', False))
            
            if is_checkmate or is_resignation:
                match.winner = current_player
                match.end_time = datetime.now()
                self.update_rankings(match, 'win' if current_player == match.player1 else 'loss')
                return
            elif is_draw:
                match.end_time = datetime.now()
                self.update_rankings(match, 'draw')
                return
            
            time.sleep(0.25)  # Add 0.25 second delay between moves
            
        # Game drawn by move limit
        match.end_time = datetime.now()
        self.update_rankings(match, 'draw')
    
    def make_ai_move(self, game) -> MoveResult:
        """Generate and validate AI move."""
        try:
            if self.game_type == 'chess':
                # Get the current board state
                board = game.get_board()
                
                # Find pieces that can be moved
                valid_moves = []
                for i in range(8):
                    for j in range(8):
                        piece = board[i][j]
                        if piece and ((game.current_player == 'white' and piece.isupper()) or 
                                    (game.current_player == 'black' and piece.islower())):
                            from_pos = {'row': i, 'col': j}
                            # Try all possible destinations
                            for x in range(8):
                                for y in range(8):
                                    to_pos = {'row': x, 'col': y}
                                    if game.is_valid_move(from_pos, to_pos):
                                        valid_moves.append((from_pos, to_pos, piece))
                
                if valid_moves:
                    # Choose a random valid move
                    from_pos, to_pos, piece = random.choice(valid_moves)
                    piece_name = {
                        'P': 'Pawn', 'N': 'Knight', 'B': 'Bishop',
                        'R': 'Rook', 'Q': 'Queen', 'K': 'King'
                    }.get(piece.upper(), 'Piece')
                    
                    move_desc = f"{piece_name} from {chr(from_pos['col']+97)}{8-from_pos['row']} to {chr(to_pos['col']+97)}{8-to_pos['row']}"
                    print(f"Moving {move_desc}")
                    
                    result = game.make_move(from_pos, to_pos)
                    if isinstance(result, dict) and result.get('valid'):
                        return {
                            'valid': True,
                            'move': {
                                'from': f"{chr(from_pos['col']+97)}{8-from_pos['row']}",
                                'to': f"{chr(to_pos['col']+97)}{8-to_pos['row']}",
                                'piece': piece_name
                            }
                        }
                    
                print("No valid moves found!")
                return {'valid': False, 'message': 'No valid moves available'}
            else:
                # Random go move
                x = random.randint(0, game.size - 1)
                y = random.randint(0, game.size - 1)
                move_desc = f"{chr(x+65)}{y+1}"
                print(f"Playing at {move_desc}")
                
                result = game.make_move(x, y)
                if result:
                    return {
                        'valid': True,
                        'move': {
                            'x': str(x),
                            'y': str(y),
                            'position': move_desc
                        }
                    }
                return {'valid': False, 'message': 'Invalid move'}
                
        except Exception as e:
            print(f"Error making move: {str(e)}")
            return {'valid': False, 'message': str(e)}
    
    def get_next_match(self) -> Optional[Match]:
        """Get the next unplayed match."""
        for match in self.matches:
            if match.start_time is None:
                match.start_time = datetime.now()
                return match
        return None

    def update_rankings(self, match: Match, result: Literal['win', 'draw', 'loss']):
        """Update rankings based on match result."""
        if result == 'win':
            self.rankings[match.player1]['wins'] += 1
            self.rankings[match.player1]['score'] += 2
            self.rankings[match.player2]['losses'] += 1
        elif result == 'draw':
            self.rankings[match.player1]['draws'] += 1
            self.rankings[match.player1]['score'] += 1
            self.rankings[match.player2]['draws'] += 1
            self.rankings[match.player2]['score'] += 1
        else:  # loss
            self.rankings[match.player2]['wins'] += 1
            self.rankings[match.player2]['score'] += 2
            self.rankings[match.player1]['losses'] += 1
    
    def show_rankings(self):
        print("\n=== Tournament Rankings ===")
        sorted_rankings = sorted(
            self.rankings.items(),
            key=lambda x: (x[1]['score'], x[1]['wins'], -x[1]['losses']),
            reverse=True
        )
        for player, stats in sorted_rankings:
            print(f"{player}: {stats['wins']}W/{stats['draws']}D/{stats['losses']}L ({stats['score']} points)")
        print("=========================\n")
    
    def get_status(self):
        return {
            'completed': self.completed,
            'matches': self.matches,
            'rankings': [
                {'name': p, 'wins': w}
                for p, w in self.rankings.items()
            ]
        }

if __name__ == '__main__':
    # Available players
    available_players = ["OpenAI", "Anthropic", "Gemini", "Claude", "GPT4"]
    
    # Get user input
    print("\nWelcome to the AI Game Tournament!")
    print("==================================")
    
    # Select game type
    print("\nSelect game type:")
    print("1. Chess")
    print("2. Go")
    game_choice = input("Enter your choice (1 or 2): ")
    game_type = 'chess' if game_choice == '1' else 'go'
    
    # Select players
    print("\nAvailable players:", ", ".join(available_players))
    print("Enter player names one at a time (or press Enter to finish):")
    selected_players = []
    while True:
        player = input(f"Player {len(selected_players) + 1}: ")
        if not player:
            break
        if player in available_players:
            selected_players.append(player)
        else:
            print("Invalid player name. Please choose from the available players.")
    
    if len(selected_players) < 2:
        print("Need at least 2 players. Adding OpenAI and Anthropic...")
        selected_players = ["OpenAI", "Anthropic"]
    
    # Number of games
    num_games = input("\nHow many games should each pair play? (default: 1): ")
    num_games = int(num_games) if num_games.isdigit() and int(num_games) > 0 else 1
    
    # Start tournament
    print(f"\nStarting {game_type.upper()} tournament with {len(selected_players)} players...")
    print(f"Each pair will play {num_games} games")
    tournament = Tournament(game_type, selected_players, num_games)
    tournament.start()
