from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import chess
import chess.engine
import openai
import anthropic
import google.generativeai as generativeai
import asyncio
from datetime import datetime
from leaderboard import leaderboard
from typing import Optional, List, Dict
import random

class ChessTournament:
    def __init__(self):
        self.players = ["OpenAI", "Anthropic", "Gemini"]
        self.matches = []
        self.rankings = {}
        
        # Initialize AI clients
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        generativeai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Initialize Stockfish
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")
    
    async def play_game(self, white_player, black_player, game_number):
        print(f"\nGame {game_number}: {white_player} (White) vs {black_player} (Black)\n")
        board = chess.Board()
        move_count = 1
        
        while not board.is_game_over():
            print(f"\nMove {move_count}")
            print(board)
            
            current = white_player if board.turn == chess.WHITE else black_player
            try:
                move_uci = await self.get_move(current, board)
                if move_uci is None:
                    break
                    
                # Convert UCI string to chess.Move object
                move = chess.Move.from_uci(move_uci)
                if move in board.legal_moves:
                    board.push(move)
                    print(f"{current} plays: {move_uci}")
                else:
                    # Use first legal move as fallback
                    fallback = list(board.legal_moves)[0]
                    board.push(fallback)
                    print(f"Invalid move {move_uci}, using {fallback.uci()}")
                    
                if board.turn == chess.WHITE:
                    move_count += 1
                    
            except Exception as e:
                print(f"Error during move: {e}")
                fallback = list(board.legal_moves)[0]
                board.push(fallback)
                print(f"Using fallback move: {fallback.uci()}")
                
                if board.turn == chess.WHITE:
                    move_count += 1
        
        # Game over - determine winner
        if board.is_checkmate():
            winner = black_player if board.turn == chess.WHITE else white_player
            print(f"\nCheckmate! {winner} wins!")
        else:
            print("\nGame drawn!")
            winner = None
            
        return winner
    
    async def run_tournament(self):
        print("\n=== Chess AI Tournament ===")
        print(f"Players: {', '.join(self.players)}")
        print("=========================\n")
        
        # Each player plays 4 games against each opponent (2 as white, 2 as black)
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
        self.engine.quit()

    def update_rankings(self, winner):
        if winner:
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
        leaderboard.show_rankings('chess')
        leaderboard.show_rankings()

    async def get_move(self, player, board):
        try:
            legal_moves = [move.uci() for move in board.legal_moves]
            if not legal_moves:
                return None
                
            # Get Stockfish evaluation for current position
            info = self.engine.analyse(board, chess.engine.Limit(time=0.1))
            eval_score = info["score"].relative.score()
            
            prompt = f"""You are a chess master. Current position evaluation: {eval_score/100} pawns.
            Choose the best move from these legal moves: {', '.join(legal_moves)}
            Avoid repetitive moves. Think strategically about piece development and king safety.
            Respond with ONLY the chosen move in UCI format."""
                
            if player == "OpenAI":
                completion = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    temperature=0.2,
                    max_tokens=10,
                    messages=[{
                        "role": "system",
                        "content": prompt
                    }]
                )
                move = completion.choices[0].message.content.strip().lower()
                
            elif player == "Anthropic":
                response = self.claude.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=10,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                move = response.content[0].text.strip().lower()
                
            elif player == "Perplexity":
                import requests

                if not os.getenv('PERPLEXITY_API_KEY'):
                    print("Perplexity API key not found, using Stockfish fallback")
                    result = self.engine.play(board, chess.engine.Limit(time=0.1))
                    return result.move.uci()

                api_key = os.getenv('PERPLEXITY_API_KEY')
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [{
                        "role": "system",
                        "content": prompt
                    }],
                    "max_tokens": 10,
                    "temperature": 0.1  # Consistent with other LLMs
                }
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=data
                )
                result_json = response.json()
                move = result_json["choices"][0]["message"]["content"].strip().lower()
                
            else:  # Gemini
                model = generativeai.GenerativeModel('gemini-pro')
                response = await model.generate_content(prompt)
                move = response.text.strip().lower()
                
            # Clean and validate move
            move = ''.join(c for c in move if c.isalnum())
            if move in legal_moves:
                # Get evaluation after potential move
                test_board = board.copy()
                test_board.push(chess.Move.from_uci(move))
                info = self.engine.analyse(test_board, chess.engine.Limit(time=0.1))
                new_eval = info["score"].relative.score()
                
                print(f"{player} plays: {move} (position change: {(new_eval - eval_score)/100:.2f} pawns)")
                return move
                
            print(f"Invalid move {move}, using best move")
            # Use Stockfish's best move as fallback
            result = self.engine.play(board, chess.engine.Limit(time=0.1))
            return result.move.uci()
                
        except Exception as e:
            print(f"Error in get_move for {player}: {e}")
            result = self.engine.play(board, chess.engine.Limit(time=0.1))
            return result.move.uci()

    def board_to_ascii(self, board):
        """Convert chess board to ASCII representation"""
        return str(board)

if __name__ == '__main__':
    tournament = ChessTournament()
    asyncio.run(tournament.run_tournament())      