import json
import os

class Leaderboard:
    def __init__(self, game_type):
        self.game_type = game_type.lower()
        self.games = []
        self.rankings = {}
        
    def add_game(self, white, black, winner):
        game_data = {
            'white': white,
            'black': black,
            'winner': winner
        }
        self.games.append(game_data)
        
        # Update rankings
        for player in [white, black]:
            if player not in self.rankings:
                self.rankings[player] = {
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'total_games': 0
                }
            self.rankings[player]['total_games'] += 1
            
        if winner:
            if winner == 'draw':
                self.rankings[white]['draws'] += 1
                self.rankings[black]['draws'] += 1
            else:
                self.rankings[winner]['wins'] += 1
                self.rankings[white if winner == black else black]['losses'] += 1
    
    def get_rankings(self):
        rankings_list = []
        for player, stats in self.rankings.items():
            rankings_list.append({
                'id': player,
                'name': player,
                'wins': stats['wins'],
                'draws': stats['draws'],
                'losses': stats['losses'],
                'winRate': self._calculate_win_rate(stats)
            })
        return sorted(rankings_list, key=lambda x: (x['wins'], -x['losses']), reverse=True)
    
    def _calculate_win_rate(self, stats):
        total_games = stats['total_games']
        if total_games == 0:
            return 0
        return round((stats['wins'] + 0.5 * stats['draws']) / total_games * 100)
    
    def display_all(self):
        print(f"\n=== {self.game_type.upper()} Game History ===")
        for game in self.games:
            print(f"{game['white']} vs {game['black']} - Winner: {game['winner']}")
        print("=====================\n")
