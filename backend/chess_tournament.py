import chess
import chess.engine
import openai
import anthropic
from google.ai import generativeai
import os
import asyncio
from datetime import datetime
from leaderboard import leaderboard
from typing import Optional, List, Dict

class ChessTournament:
    def __init__(self):
        self.players = ["OpenAI", "Anthropic", "Gemini"]
        self.matches = []
        self.rankings = {}
        
        # Initialize AI clients
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        generativeai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Initialize Stockfish
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")
    
    async def play_game(self, white, black, game_num):
        print(f"\nGame {game_num}: {white} (White) vs {black} (Black)")
        board = chess.Board()
        moves = 0
        
        while not board.is_game_over() and moves < 100:
            print(f"\nMove {moves + 1}")
            print(board)
            
            current = white if board.turn else black
            
            # Get move from LLM
            move_uci = await self.get_move(current, board)
            
            try:
                move = chess.Move.from_uci(move_uci)
                if move in board.legal_moves:
                    # Get Stockfish evaluation before move
                    info = await self.engine.analyse(board, chess.engine.Limit(time=0.1))
                    eval_before = info['score'].white().score()
                    
                    # Make the move
                    board.push(move)
                    print(f"{current} plays {move_uci}")
                    
                    # Get Stockfish evaluation after move
                    info = await self.engine.analyse(board, chess.engine.Limit(time=0.1))
                    eval_after = info['score'].white().score()
                    
                    # Print move quality
                    if board.turn:  # After White's move
                        quality = eval_after - eval_before
                    else:  # After Black's move
                        quality = eval_before - eval_after
                    
                    if quality > 50:
                        print("Excellent move!")
                    elif quality > 0:
                        print("Good move")
                    else:
                        print("Inaccurate move")
                    
                    moves += 1
                else:
                    print(f"Invalid move {move_uci}, trying again...")
            except:
                print(f"Invalid move format {move_uci}, trying again...")
        
        # Game over
        print("\nGame Over!")
        print(board)
        
        if board.is_checkmate():
            winner = black if board.turn else white
            print(f"Checkmate! {winner} wins!")
        else:
            winner = None
            print("Draw!")
        
        # Add to leaderboard
        leaderboard.add_game('chess', white, black, winner)
        self.update_rankings(winner)
        
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
            fen = board.fen()
            legal_moves = [move.uci() for move in board.legal_moves]
            
            if player == "OpenAI":
                try:
                    response = await openai.chat.completions.create(
                        model="gpt-4",
                        messages=[{
                            "role": "system",
                            "content": "You are a chess master. Given a board position in FEN notation, suggest the best move in UCI format (e.g., e2e4)."
                        }, {
                            "role": "user",
                            "content": f"Board position: {fen}\nLegal moves: {', '.join(legal_moves)}\nWhat's your move?"
                        }]
                    )
                    move = response.choices[0].message.content.strip()
                    return move if move in legal_moves else legal_moves[0]
                except Exception as e:
                    print(f"OpenAI API error: {e}")
                    return legal_moves[0]  # Fallback to first legal move
                
            elif player == "Anthropic":
                try:
                    response = await self.claude.messages.create(
                        model="claude-3-opus-20240229",
                        messages=[{
                            "role": "user",
                            "content": f"You are a chess master. Given this board position in FEN: {fen}\nLegal moves: {', '.join(legal_moves)}\nWhat's your move? Respond only with the move in UCI format (e.g., e2e4)"
                        }]
                    )
                    move = response.content.strip()
                    return move if move in legal_moves else legal_moves[0]
                except Exception as e:
                    print(f"Anthropic API error: {e}")
                    return legal_moves[0]
                
            else:  # Gemini
                try:
                    model = generativeai.GenerativeModel('gemini-pro')
                    response = await model.generate_content(
                        f"You are a chess master. For this board position in FEN: {fen}\nLegal moves: {', '.join(legal_moves)}\nWhat's your move? Respond only with the move in UCI format (e.g., e2e4)"
                    )
                    move = response.text.strip()
                    return move if move in legal_moves else legal_moves[0]
                except Exception as e:
                    print(f"Gemini API error: {e}")
                    return legal_moves[0]
                    
        except Exception as e:
            print(f"Error getting move: {e}")
            return list(board.legal_moves)[0].uci()  # Fallback to first legal move

if __name__ == '__main__':
    tournament = ChessTournament()
    asyncio.run(tournament.run_tournament()) 