import json
import os

class Leaderboard:
    def __init__(self):
        self.filename = 'leaderboard.json'
        self.data = self.load_data()
        
    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {
            'chess': {
                'games': [],
                'rankings': {}
            },
            'go': {
                'games': [],
                'rankings': {}
            }
        }
    
    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_game(self, game_type, black, white, winner, score=None):
        game = {
            'black': black,
            'white': white,
            'winner': winner,
            'score': score
        }
        self.data[game_type]['games'].append(game)
        
        # Update rankings
        if winner not in self.data[game_type]['rankings']:
            self.data[game_type]['rankings'][winner] = {'wins': 0, 'total_games': 0}
        
        # Update both players' total games
        for player in [black, white]:
            if player not in self.data[game_type]['rankings']:
                self.data[game_type]['rankings'][player] = {'wins': 0, 'total_games': 0}
            self.data[game_type]['rankings'][player]['total_games'] += 1
        
        # Update winner's wins
        self.data[game_type]['rankings'][winner]['wins'] += 1
        
        self.save_data()
    
    def show_rankings(self, game_type=None):
        if game_type:
            print(f"\n=== {game_type.upper()} Rankings ===")
            rankings = self.data[game_type]['rankings']
            sorted_rankings = sorted(
                rankings.items(),
                key=lambda x: (x[1]['wins'], -x[1]['total_games']),
                reverse=True
            )
            for player, stats in sorted_rankings:
                print(f"{player}: {stats['wins']} wins / {stats['total_games']} games")
        else:
            print("\n=== Overall Rankings ===")
            # Combine stats from both games
            overall = {}
            for game_type in ['chess', 'go']:
                for player, stats in self.data[game_type]['rankings'].items():
                    if player not in overall:
                        overall[player] = {'wins': 0, 'total_games': 0}
                    overall[player]['wins'] += stats['wins']
                    overall[player]['total_games'] += stats['total_games']
            
            sorted_overall = sorted(
                overall.items(),
                key=lambda x: (x[1]['wins'], -x[1]['total_games']),
                reverse=True
            )
            for player, stats in sorted_overall:
                print(f"{player}: {stats['wins']} wins / {stats['total_games']} games")
        print("=====================\n")
    
    def get_total_games(self):
        chess_games = len(self.data['chess']['games'])
        go_games = len(self.data['go']['games'])
        return {
            'chess': chess_games,
            'go': go_games,
            'total': chess_games + go_games
        }

# Create global leaderboard instance
leaderboard = Leaderboard()