import json
import os

class Leaderboard:
    def __init__(self):
        self.games = []  # Keep original list
        self.data = {    # Add organized structure
            'Chess': {'games': []},
            'Go': {'games': []}
        }
        
    def add_game(self, white, black, winner, game_type):
        game_data = {
            'white': white,
            'black': black,
            'winner': winner,
            'game_type': game_type
        }
        
        # Add to both structures
        self.games.append(game_data)
        self.data[game_type]['games'].append(game_data)
    
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
    
    def display_all(self):
        print("\n=== Complete Game History ===")
        for game in self.games:
            print(f"{game['game_type']}: {game['white']} vs {game['black']} - Winner: {game['winner']}")
            
        print("\n=== Chess Games ===")
        for game in self.data['Chess']['games']:
            print(f"{game['white']} vs {game['black']} - Winner: {game['winner']}")
            
        print("\n=== Go Games ===")
        for game in self.data['Go']['games']:
            print(f"{game['white']} vs {game['black']} - Winner: {game['winner']}")

# Create global leaderboard instance
leaderboard = Leaderboard()
leaderboard.display_all()