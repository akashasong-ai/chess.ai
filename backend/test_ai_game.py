import chess
from llm_interface import LLMInterface
import random
import time
from leaderboard import Leaderboard

def simulate_chess_game():
    # Initialize the game and AIs
    board = chess.Board()
    ai_white = LLMInterface("openai")
    ai_black = LLMInterface("anthropic")
    
    print("Starting Chess Game: OpenAI (White) vs Anthropic (Black)")
    print("Initial board:")
    print(board)
    print("\n")
    
    move_count = 0
    
    while not board.is_game_over() and move_count < 50:
        current_ai = ai_white if board.turn else ai_black
        player_name = "White (OpenAI)" if board.turn else "Black (Anthropic)"
        
        print(f"\n{player_name}'s turn...")
        
        # Get all legal moves
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            break
            
        # Make a random valid move
        move = random.choice(legal_moves)
        board.push(move)
        move_count += 1
        
        print(f"{player_name} plays {move}")
        print(board)
        print("\n")
        
        time.sleep(0.5)  # Small delay to make it readable
    
    # Game ended
    print("\nGame Over!")
    if board.is_checkmate():
        winner = "Black (Anthropic)" if board.turn else "White (OpenAI)"
        print(f"Checkmate! {winner} wins!")
    elif board.is_stalemate():
        print("Stalemate!")
    elif board.is_insufficient_material():
        print("Draw due to insufficient material!")
    else:
        print("Game ended due to move limit")
    
    print(f"Total moves: {move_count}")
    
    winner = "Black (Anthropic)" if board.turn else "White (OpenAI)"
    
    leaderboard = Leaderboard()
    leaderboard.add_game(
        white="OpenAI",
        black="Anthropic",
        winner=winner,
        game_type="Chess"
    )
    
    # Add this line to display the leaderboards
    leaderboard.display_all()

if __name__ == "__main__":
    simulate_chess_game() 