def calculate_elo(rating_a, rating_b, score_a, k=32):
    """Calculate new ELO ratings for two players."""
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    new_rating_a = rating_a + k * (score_a - expected_a)
    new_rating_b = rating_b + k * ((1 - score_a) - (1 - expected_a))
    return round(new_rating_a), round(new_rating_b)

def validate_move(game_type, board, move):
    """Validate a move based on game type and current board state."""
    if game_type == 'chess':
        return validate_chess_move(board, move)
    else:
        return validate_go_move(board, move)

def validate_chess_move(board, move):
    """Validate a chess move."""
    # Basic validation - implement full chess rules here
    from_pos = move['from']
    to_pos = move['to']
    
    # Check if positions are within board
    if not (0 <= from_pos['row'] <= 7 and 0 <= from_pos['col'] <= 7 and
            0 <= to_pos['row'] <= 7 and 0 <= to_pos['col'] <= 7):
        return False
    
    return True

def validate_go_move(board, move):
    """Validate a go move."""
    x, y = move['x'], move['y']
    
    # Check if position is within board
    if not (0 <= x < len(board) and 0 <= y < len(board)):
        return False
    
    # Check if position is empty
    if board[y][x]:
        return False
    
    return True 