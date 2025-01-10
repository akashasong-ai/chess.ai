import openai
import anthropic
from google.ai import generativeai
import os
import asyncio
from datetime import datetime
import subprocess
import json
from go_board import GoBoard
from leaderboard import leaderboard
from typing import Optional, List, Dict, Tuple

class GoTournament:
    def __init__(self):
        self.players = ["OpenAI", "Anthropic", "Gemini"]
        self.matches = []
        self.rankings = {}
        self.board_size = 9
        
        # Initialize AI clients
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        generativeai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Initialize KataGo
        self.katago_process = subprocess.Popen(
            ['katago', 'gtp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    async def get_move(self, player, board_state):
        try:
            board_str = self.board_to_string(board_state)
            
            if player == "OpenAI":
                try:
                    response = await openai.chat.completions.create(
                        model="gpt-4",
                        messages=[{
                            "role": "system",
                            "content": "You are a Go master. Given a board position, suggest the best move in GTP format (e.g., D4)."
                        }, {
                            "role": "user",
                            "content": f"Board position:\n{board_str}\nWhat's your move?"
                        }]
                    )
                    return self.clean_move_response(response.choices[0].message.content)
                except Exception as e:
                    print(f"OpenAI API error: {e}")
                    return self.get_random_valid_move(board_state)
                
            elif player == "Anthropic":
                try:
                    response = await self.claude.messages.create(
                        model="claude-3-opus-20240229",
                        messages=[{
                            "role": "user",
                            "content": f"You are a Go master. Given this board position:\n{board_str}\nWhat's your move? Respond only with the move in GTP format (e.g., D4)"
                        }]
                    )
                    return self.clean_move_response(response.content)
                except Exception as e:
                    print(f"Anthropic API error: {e}")
                    return self.get_random_valid_move(board_state)
                
            else:  # Gemini
                try:
                    model = generativeai.GenerativeModel('gemini-pro')
                    response = await model.generate_content(
                        f"You are a Go master. For this board position:\n{board_str}\nWhat's your move? Respond only with the move in GTP format (e.g., D4)"
                    )
                    return self.clean_move_response(response.text)
                except Exception as e:
                    print(f"Gemini API error: {e}")
                    return self.get_random_valid_move(board_state)
                    
        except Exception as e:
            print(f"Error getting move: {e}")
            return self.get_random_valid_move(board_state)
    
    def clean_move_response(self, move: str) -> str:
        """Clean and validate the move response from LLMs"""
        # Remove any extra text, keep only the move coordinates
        move = move.strip().upper()
        # Extract first occurrence of valid move format (e.g., "D4")
        import re
        match = re.search(r'[A-HJ][1-9]', move)
        return match.group(0) if match else "PASS"
    
    def get_random_valid_move(self, board_state) -> str:
        """Generate a random valid move as fallback"""
        import random
        empty_positions = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board_state[i][j] == 0:
                    empty_positions.append((i, j))
        
        if not empty_positions:
            return "PASS"
            
        row, col = random.choice(empty_positions)
        col_letter = chr(ord('A') + (col + 1 if col >= 8 else col))
        return f"{col_letter}{row + 1}"
    
    async def play_game(self, black, white, game_num):
        print(f"\nGame {game_num}: {black} (Black) vs {white} (White)")
        board = GoBoard(size=self.board_size)
        moves = 0
        passes = 0
        
        while passes < 2 and moves < 150:
            print(f"\nMove {moves + 1}")
            print(board)
            
            current = black if board.current_player == 1 else white
            
            # Get move from LLM
            move = await self.get_move(current, board.get_state())
            
            # Validate and make move
            if self.validate_move(move, board.get_state()):
                x, y = self.parse_move(move)
                if board.make_move(x, y):
                    print(f"{current} plays at {move}")
                    moves += 1
                    passes = 0
                else:
                    passes += 1
                    print(f"{current} passes")
            else:
                print(f"Invalid move {move}, trying again...")
        
        # Calculate score
        black_score = board.captured_white
        white_score = board.captured_black + 6.5  # komi
        
        winner = black if black_score > white_score else white
        print(f"\nGame Over! Winner: {winner}")
        print(f"Final Score - Black: {black_score:.1f}, White: {white_score:.1f}")
        
        # Add to leaderboard
        leaderboard.add_game('go', black, white, winner, {
            'black_score': black_score,
            'white_score': white_score
        })
        
        self.update_rankings(winner)
        return winner
    
    async def run_tournament(self):
        print("\n=== Go AI Tournament ===")
        print(f"Board Size: {self.board_size}x{self.board_size}")
        print(f"Players: {', '.join(self.players)}")
        print("======================\n")
        
        # Each player plays 4 games against each opponent
        for i in range(len(self.players)):
            for j in range(i + 1, len(self.players)):
                player1, player2 = self.players[i], self.players[j]
                print(f"\n{player1} vs {player2} Series:")
                
                # Play 4 games
                for game in range(4):
                    if game % 2 == 0:
                        await self.play_game(player1, player2, game + 1)
                    else:
                        await self.play_game(player2, player1, game + 1)
        
        self.show_rankings()
        self.katago_process.terminate()
    
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
        print("====================\n")
        
        # Show overall leaderboard
        leaderboard.show_rankings('go')
        leaderboard.show_rankings()
    
    def board_to_string(self, board_state):
        # Convert board state to string representation
        symbols = {0: '.', 1: 'X', 2: 'O'}
        result = "  A B C D E F G H J\n"
        for i in range(self.board_size):
            result += f"{i+1} "
            for j in range(self.board_size):
                result += f"{symbols[board_state[i][j]]} "
            result += f"{i+1}\n"
        result += "  A B C D E F G H J\n"
        return result
    
    def parse_move(self, move):
        # Convert GTP format move (e.g., "D4") to coordinates
        col = ord(move[0].upper()) - ord('A')
        if col >= 8:  # Skip 'I' in GTP format
            col -= 1
        row = int(move[1:]) - 1
        return row, col
    
    def validate_move(self, move, board_state):
        # Basic validation of move format
        if not move or len(move) < 2:
            return False
            
        try:
            row, col = self.parse_move(move)
            if not (0 <= row < self.board_size and 0 <= col < self.board_size):
                return False
                
            # Check if position is empty
            if board_state[row][col] != 0:
                return False
                
            return True
            
        except:
            return False

if __name__ == '__main__':
    tournament = GoTournament()
    asyncio.run(tournament.run_tournament())