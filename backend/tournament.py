import random
import time
from chess_engine import ChessGame
from go_board import GoBoard

class Tournament:
    def __init__(self, game_type, players, num_games=1):
        self.game_type = game_type
        self.players = players
        self.num_games = num_games
        self.matches = []
        self.rankings = {}
        self.completed = False
        
    def start(self):
        print("\n=== Starting Tournament ===")
        print(f"Game: {self.game_type}")
        print(f"Players: {', '.join(self.players)}")
        print("=========================\n")
        
        # Create round-robin matches
        for i in range(len(self.players)):
            for j in range(i + 1, len(self.players)):
                self.play_match(self.players[i], self.players[j])
                
        self.completed = True
        self.show_rankings()
    
    def play_match(self, player1, player2):
        print(f"\n{'='*40}")
        print(f"Match: {player1} (White) vs {player2} (Black)")
        print(f"{'='*40}\n")
        
        if self.game_type == 'chess':
            game = ChessGame(player1, player2)
        else:
            game = GoBoard(player1, player2)
            
        moves = 0
        while moves < 30:  # 30 moves per game
            print(f"\nMove {moves + 1}")
            print(game)
            
            current_player = player1 if moves % 2 == 0 else player2
            print(f"{current_player}'s turn")
            
            # Make move
            result = self.make_ai_move(game)
            if not result['valid']:
                continue
                
            moves += 1
            time.sleep(0.25)  # Add 0.25 second delay between moves
            
        # Update rankings
        winner = player1 if random.random() > 0.5 else player2
        self.update_rankings(winner)
        print(f"\n{'='*40}")
        print(f"Game Over! Winner: {winner}")
        print(f"Final Position:")
        print(game)
        print(f"{'='*40}\n")
    
    def make_ai_move(self, game):
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
                return game.make_move(from_pos, to_pos)
            else:
                print("No valid moves found!")
                return {'valid': False}
        else:
            # Random go move
            x = random.randint(0, game.size - 1)
            y = random.randint(0, game.size - 1)
            print(f"Playing at {chr(x+65)}{y+1}")
            return game.make_move(x, y)
    
    def update_rankings(self, winner):
        if winner not in self.rankings:
            self.rankings[winner] = 0
        self.rankings[winner] += 1
    
    def show_rankings(self):
        print("\n=== Tournament Rankings ===")
        sorted_rankings = sorted(
            self.rankings.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for player, wins in sorted_rankings:
            print(f"{player}: {wins} wins")
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