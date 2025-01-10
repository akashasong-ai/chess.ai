from go_engine import GoBoard
from llm_interface import LLMInterface
from leaderboard import Leaderboard
import time
import random

def simulate_go_game():
    # Initialize the game and AIs
    board = GoBoard(size=9)  # Using 9x9 board for faster games
    ai_black = LLMInterface("openai")
    ai_white = LLMInterface("anthropic")
    leaderboard = Leaderboard()
    
    print("Starting Go Game: OpenAI (Black) vs Anthropic (White)")
    print("Initial board:")
    print(board)
    print("\n")
    
    move_count = 0
    passes = 0
    
    while passes < 2 and move_count < 100:  # Game ends after 2 consecutive passes
        current_ai = ai_black if board.current_player == 1 else ai_white
        player_name = "Black (OpenAI)" if board.current_player == 1 else "White (Anthropic)"
        
        print(f"\n{player_name}'s turn...")
        
        # Get all valid moves
        valid_moves = []
        for i in range(board.size):
            for j in range(board.size):
                if board.is_valid_move(i, j):
                    valid_moves.append((i, j))
        
        if not valid_moves:
            print(f"{player_name} passes")
            passes += 1
            board.current_player = 3 - board.current_player
            continue
            
        # Make a random valid move
        x, y = random.choice(valid_moves)
        if board.make_move(x, y):
            print(f"{player_name} plays at {chr(65+y)}{x}")
            move_count += 1
            passes = 0
            print(board)
            print(f"Captures - Black: {board.captured_black}, White: {board.captured_white}")
        else:
            print(f"Invalid move attempted by {player_name}")
            continue
            
        time.sleep(0.5)  # Reduced delay to make the game faster
    
    # Game ended, calculate score (simple version)
    black_score = board.captured_white
    white_score = board.captured_black + 6.5  # komi
    
    winner = "Black" if black_score > white_score else "White"
    
    print("\nGame Over!")
    print(f"Final Score:")
    print(f"Black (OpenAI): {black_score}")
    print(f"White (Anthropic): {white_score}")
    print(f"Winner: {winner}")
    
    # Record game in leaderboard
    leaderboard.add_game(
        white="Anthropic",
        black="OpenAI",
        winner=winner,
        moves=move_count,
        game_type="Go"
    )

if __name__ == "__main__":
    simulate_go_game() 