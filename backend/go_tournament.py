from dotenv import load_dotenv
import os
import random
import asyncio
import openai
import anthropic
import google.generativeai as generativeai
import subprocess
from datetime import datetime
from go_board import GoBoard
from leaderboard import leaderboard
from typing import Optional, List, Dict, Tuple

# Load environment variables from .env file
load_dotenv()

class GoTournament:
    def __init__(self):
        self.players = ["OpenAI", "Anthropic", "Gemini"]
        self.matches = []
        self.rankings = {}
        self.board_size = 9
        
        # Initialize AI clients
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        generativeai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Initialize KataGo
        try:
            self.katago = subprocess.Popen(
                ['katago', 'gtp'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("KataGo engine initialized successfully")
        except Exception as e:
            print(f"Could not initialize KataGo: {e}")
            self.katago = None
    
    async def get_move(self, player, board_state):
        try:
            # Create list of valid moves
            valid_moves = []
            occupied_moves = []
            for i in range(self.board_size):
                for j in range(self.board_size):
                    col = chr(ord('A') + j)
                    if col >= 'I':
                        continue
                    row = str(i + 1)
                    move = f"{col}{row}"
                    if board_state[i][j] == 0:
                        valid_moves.append(move)
                    else:
                        occupied_moves.append(move)
            
            if not valid_moves:
                return "PASS"
                
            # Create board visualization
            header = '   A B C D E F G H'
            rows = []
            for i in range(self.board_size):
                row = f"{i+1:2d} " + ' '.join(['.' if cell == 0 else '●' if cell == 1 else '○' for cell in board_state[i]])
                rows.append(row)
            board_str = header + '\n' + '\n'.join(rows)
            
            prompt = f"""You are playing Go. Current board:
            {board_str}
            
            IMPORTANT: Your last move was invalid. Choose a different move.
            
            OCCUPIED POSITIONS (DO NOT PLAY HERE): {', '.join(occupied_moves)}
            VALID MOVES (CHOOSE ONE OF THESE): {', '.join(valid_moves)}
            
            Rules:
            1. You MUST choose exactly ONE move from the VALID MOVES list
            2. DO NOT choose from the OCCUPIED POSITIONS list
            3. DO NOT repeat invalid moves
            4. Respond with ONLY the move (e.g., 'D4')
            
            Your move:"""
                
            if player == "OpenAI":
                completion = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    temperature=0.1,  # Low temperature for consistent, focused moves
                    max_tokens=2,
                    messages=[
                        {"role": "system", "content": "You are playing Go. Be strategic and avoid invalid moves."},
                        {"role": "user", "content": prompt}
                    ]
                )
                move = completion.choices[0].message.content.strip().upper()
                
            elif player == "Anthropic":
                response = self.claude.messages.create(
                    model="claude-3-opus-20240229",
                    temperature=0.1,  # Low temperature for consistent, focused moves
                    max_tokens=2,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                move = response.content[0].text.strip().upper()
                
            elif player == "Perplexity":
                import requests

                if not os.getenv('PERPLEXITY_API_KEY'):
                    print("Perplexity API key not found, using random move")
                    return random.choice(valid_moves)

                api_key = os.getenv('PERPLEXITY_API_KEY')
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are playing Go. Be strategic and avoid invalid moves."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 2,
                    "temperature": 0.1  # Consistent with other LLMs
                }
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=data
                )
                result_json = response.json()
                move = result_json["choices"][0]["message"]["content"].strip().upper()
                
            else:  # Gemini
                model = generativeai.GenerativeModel('gemini-pro')
                chat = model.start_chat(temperature=0.1)  # Low temperature for consistent, focused moves
                response = await chat.send_message_async(prompt)
                move = response.text.strip().upper()
                
            # Clean and validate move
            move = ''.join(c for c in move if c.isalnum()).upper()
            if move in valid_moves:
                print(f"{player} plays: {move}")
                return move
                
            print(f"{player} suggested invalid move: {move}")
            print(f"Occupied positions: {', '.join(occupied_moves)}")
            print(f"Valid moves: {', '.join(valid_moves)}")
            
            # Choose a strategic move when LLM fails
            center = ['D4', 'D5', 'E4', 'E5']
            corners = ['A1', 'A9', 'H1', 'H9']
            strategic_moves = [m for m in (center + corners) if m in valid_moves]
            if strategic_moves:
                move = random.choice(strategic_moves)
                print(f"Choosing strategic move: {move}")
                return move
            
            return random.choice(valid_moves)
                
        except Exception as e:
            print(f"Error in get_move for {player}: {e}")
            return random.choice(valid_moves)
            
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
    
    async def play_game(self, black, white, game_number):
        print(f"\nGame {game_number}: {black} (Black) vs {white} (White)\n")
        board = GoBoard(self.board_size)
        move_count = 1
        
        while move_count <= 81:  # Maximum moves for 9x9 board
            print(f"\nMove {move_count}")
            print(board)  # This will now use the __str__ method
            
            current_player = black if board.current_player == 1 else white
            try:
                move = await self.get_move(current_player, board.get_state())
                if move == "PASS":
                    break
                    
                # Convert GTP format (e.g., "D4") to board coordinates
                col = ord(move[0]) - ord('A')
                if col >= 8:  # Adjust for skipped 'I'
                    col -= 1
                row = int(move[1:]) - 1
                
                if board.make_move(row, col, board.current_player):
                    print(f"{current_player} plays: {move}")
                    move_count += 1
                else:
                    print(f"Invalid move {move}")
                    
            except Exception as e:
                print(f"Error during move: {e}")
                # Make a random valid move
                valid_moves = []
                for i in range(self.board_size):
                    for j in range(self.board_size):
                        if board.board[i][j] == 0:
                            valid_moves.append((i, j))
                if valid_moves:
                    row, col = random.choice(valid_moves)
                    board.make_move(row, col, board.current_player)
                    col_letter = chr(ord('A') + (col + 1 if col >= 8 else col))
                    print(f"Random move: {col_letter}{row + 1}")
                    move_count += 1
                else:
                    break
        
        # Determine winner (in a real game, we'd count territory)
        black_stones = sum(row.count(1) for row in board.board)
        white_stones = sum(row.count(2) for row in board.board)
        
        if black_stones > white_stones:
            print(f"\n{black} (Black) wins with {black_stones} stones vs {white_stones}!")
            return black
        elif white_stones > black_stones:
            print(f"\n{white} (White) wins with {white_stones} stones vs {black_stones}!")
            return white
        else:
            print("\nGame drawn!")
            return None
    
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
        self.katago.terminate()
    
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
        """Convert board state to ASCII representation"""
        symbols = {0: '.', 1: '●', 2: '○'}
        rows = []
        # Add column labels
        cols = '   ' + ' '.join(chr(ord('A') + i) for i in range(self.board_size))
        rows.append(cols)
        # Add board rows with row numbers
        for i in range(self.board_size):
            row = f"{i+1:2d} " + ' '.join(symbols[cell] for cell in board_state[i])
            rows.append(row)
        return '\n'.join(rows)
    
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
    
    def get_katago_move(self, board_state, color='B'):
        """Get best move suggestion from KataGo"""
        if not self.katago:
            return None
            
        try:
            # Send current position to KataGo
            board_setup = self.board_to_gtp(board_state)
            self.katago.stdin.write(f"clear_board\n{board_setup}\ngenmove {color}\n")
            self.katago.stdin.flush()
            
            # Read KataGo's response
            response = self.katago.stdout.readline().strip()
            best_move = response.split()[-1] if response else None
            
            return best_move
        except Exception as e:
            print(f"KataGo error: {e}")
            return None
    
    def board_to_gtp(self, board_state):
        """Convert board state to GTP format"""
        commands = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board_state[i][j] != 0:
                    color = 'B' if board_state[i][j] == 1 else 'W'
                    col = chr(ord('A') + j)
                    if col >= 'I':  # Skip 'I' in GTP
                        col = chr(ord(col) + 1)
                    row = str(i + 1)
                    commands.append(f"play {color} {col}{row}")
        return '\n'.join(commands)

if __name__ == '__main__':
    tournament = GoTournament()
    asyncio.run(tournament.run_tournament())
