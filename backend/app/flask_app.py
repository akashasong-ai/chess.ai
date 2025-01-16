from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import random
import logging
from itertools import combinations
import time
import os
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
logging.basicConfig(level=logging.DEBUG)

# Global variables
board = None
game_state = None
tournament_state = {
    'active': False,
    'matches': [],
    'current_match': 0,
    'results': {},
    'participants': []
}

# Add global leaderboard variable
leaderboard = {
    'GPT-4': {'wins': 0, 'losses': 0},
    'CLAUDE': {'wins': 0, 'losses': 0},
    'GEMINI': {'wins': 0, 'losses': 0}
}

def start_new_game(white_ai=None, black_ai=None):
    global board, game_state
    board = chess.Board()
    game_state = {
        'status': 'active',
        'currentPlayer': 'white',
        'whiteAI': white_ai,
        'blackAI': black_ai
    }
    return True

# Add these helper functions at the top
def get_next_ai_move(board, ai_name):
    try:
        if board is None:
            logger.error("Board is None in get_next_ai_move")
            return None
            
        if board.is_game_over():
            return None
            
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
            
        # Use the improved AI logic we added earlier
        best_move = get_ai_move(ai_name, board)
        return best_move if best_move else random.choice(legal_moves)
        
    except Exception as e:
        logger.error(f"Error getting AI move: {str(e)}")
        return None

def process_tournament_move():
    try:
        global board, game_state
        if not tournament_state['active'] or not game_state or board is None:
            logger.debug("Tournament not active, game state None, or board None")
            return
            
        current_match = tournament_state['matches'][tournament_state['current_match']]
        current_player = game_state.get('currentPlayer')
        if not current_player:
            logger.error("Current player not set in game state")
            return
            
        ai_name = current_match['white'] if current_player == 'white' else current_match['black']
        
        # Add delay to make moves visible
        time.sleep(0.5)  # 500ms delay between moves
        
        move = get_next_ai_move(board, ai_name)
        if move:
            logger.debug(f"{ai_name} making move: {move}")
            board.push(move)
            game_state['currentPlayer'] = 'black' if current_player == 'white' else 'white'
            
            if board.is_game_over():
                winner = None
                if board.is_checkmate():
                    winner = current_match['white'] if current_player == 'white' else current_match['black']
                game_state['status'] = 'finished'
                game_state['winner'] = winner
                handle_game_over(winner)
                
    except Exception as e:
        logger.error(f"Error in process_tournament_move: {str(e)}")

# Tournament endpoints
@app.route('/api/tournament/start', methods=['POST'])
def start_tournament():
    try:
        global tournament_state, board, game_state
        data = request.get_json()
        participants = data.get('participants', ['GPT-4', 'CLAUDE', 'GEMINI'])
        num_matches = data.get('matches', 3)
        
        if len(participants) < 2:
            return jsonify({'error': 'Need at least 2 participants'}), 400
            
        pairs = list(combinations(participants, 2))
        matches = []
        
        for _ in range(num_matches):
            for white, black in pairs:
                matches.append({
                    'white': white,
                    'black': black,
                    'result': None
                })
                
        random.shuffle(matches)
        
        tournament_state = {
            'active': True,
            'matches': matches,
            'current_match': 0,
            'results': {p: {'wins': 0, 'losses': 0} for p in participants},
            'participants': participants
        }
        
        # Start first match
        current_match = matches[0]
        start_new_game(current_match['white'], current_match['black'])
        
        return jsonify({
            'success': True,
            'tournamentStatus': {
                'currentMatch': 1,
                'totalMatches': len(matches),
                'matches': matches,
                'currentGame': {
                    'white': current_match['white'],
                    'black': current_match['black']
                }
            }
        })
        
    except Exception as e:
        logging.error(f"Error in start_tournament: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/tournament/status', methods=['GET'])
def get_tournament_status():
    try:
        if not tournament_state['active']:
            return jsonify({'error': 'No active tournament'}), 404
            
        return jsonify({
            'success': True,
            'tournamentStatus': {
                'currentMatch': tournament_state['current_match'] + 1,
                'totalMatches': len(tournament_state['matches']),
                'matches': tournament_state['matches'],
                'results': tournament_state['results']
            }
        })
    except Exception as e:
        logging.error(f"Error in get_tournament_status: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/tournament/stop', methods=['POST'])
def stop_tournament():
    try:
        global tournament_state
        tournament_state = {
            'active': False,
            'matches': [],
            'current_match': 0,
            'results': {},
            'participants': []
        }
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error in stop_tournament: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Game endpoints
@app.route('/api/game/start', methods=['POST', 'OPTIONS'])
def start_game():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        white_ai = data.get('whiteAI')
        black_ai = data.get('blackAI')
        success = start_new_game(white_ai, black_ai)
        return jsonify({'success': success})
    except Exception as e:
        logging.error(f"Error in start_game: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Add this helper function to convert board to FEN (Forsyth–Edwards Notation)
def get_board_fen():
    global board
    return board.fen() if board else None

@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    try:
        if board is None:
            return jsonify({'error': 'No active game'}), 400
        if game_state is None:
            return jsonify({'error': 'No active game state'}), 400
            
        # Convert board to 2D array with proper piece case preservation
        board_array = []
        for row in range(7, -1, -1):
            board_row = []
            for col in range(8):
                piece = board.piece_at(chess.square(col, row))
                if piece:
                    # Preserve case: uppercase for white, lowercase for black
                    symbol = piece.symbol().upper() if piece.color else piece.symbol().lower()
                    board_row.append(symbol)
                else:
                    board_row.append(' ')
            board_array.append(board_row)
            
        # Log the board state for debugging
        logger.debug(f"Current board state: {board_array}")
            
        return jsonify({
            'board': board_array,
            'gameState': {
                'status': 'finished' if board.is_game_over() else 'active',
                'currentPlayer': game_state.get('currentPlayer', 'white'),
                'whiteAI': game_state.get('whiteAI'),
                'blackAI': game_state.get('blackAI'),
                'winner': game_state.get('winner'),
                'fen': board.fen() if board else None  # Include FEN for debugging
            }
        })
    except Exception as e:
        logging.error(f"Error in get_game_state: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/game/move', methods=['POST'])
def make_move():
    try:
        global board, game_state
        if board is None or game_state is None:
            return jsonify({'error': 'No active game'}), 400

        data = request.get_json()
        move = data.get('move')
        
        if move is None:
            return jsonify({'error': 'No move provided'}), 400
            
        # Convert move to chess.Move object
        chess_move = chess.Move.from_uci(move)
        
        if chess_move in board.legal_moves:
            board.push(chess_move)
            current_player = game_state.get('currentPlayer', 'white')
            game_state['currentPlayer'] = 'black' if current_player == 'white' else 'white'
            
            # Check for game over conditions
            if board.is_game_over():
                game_state['status'] = 'finished'
                if board.is_checkmate():
                    winner = 'black' if current_player == 'white' else 'white'
                    white_ai = game_state.get('whiteAI')
                    black_ai = game_state.get('blackAI')
                    game_state['winner'] = white_ai if winner == 'white' else black_ai
                
            return jsonify({
                'success': True,
                'board': [[str(board.piece_at(chess.square(col, row))) if board.piece_at(chess.square(col, row)) else ' '
                          for col in range(8)] for row in range(7, -1, -1)],
                'gameState': game_state
            })
        else:
            return jsonify({'error': 'Invalid move'}), 400
            
    except Exception as e:
        logging.error(f"Error in make_move: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/game/stop', methods=['POST'])
def stop_game():
    try:
        global board, game_state, tournament_state
        board = None
        game_state = None
        tournament_state['active'] = False
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error in stop_game: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Add leaderboard endpoint
@app.route('/api/leaderboard', methods=['GET', 'OPTIONS'])
def get_leaderboard():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        return jsonify({
            'success': True,
            'leaderboard': [
                {
                    'name': player,
                    'wins': stats['wins'],
                    'losses': stats['losses'],
                    'winRate': round(stats['wins'] / (stats['wins'] + stats['losses']) * 100, 1) if (stats['wins'] + stats['losses']) > 0 else 0
                }
                for player, stats in leaderboard.items()
            ]
        })
    except Exception as e:
        logging.error(f"Error in get_leaderboard: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Update handle_game_over to update leaderboard
def handle_game_over(winner):
    global tournament_state, leaderboard
    if tournament_state['active']:
        current_match = tournament_state['matches'][tournament_state['current_match']]
        current_match['result'] = winner
        
        if winner:
            # Update leaderboard
            leaderboard[winner]['wins'] += 1
            loser = current_match['black'] if winner == current_match['white'] else current_match['white']
            leaderboard[loser]['losses'] += 1
            
            # Update tournament results
            tournament_state['results'][winner]['wins'] += 1
            tournament_state['results'][loser]['losses'] += 1
        
        # Move to next match
        tournament_state['current_match'] += 1
        if tournament_state['current_match'] < len(tournament_state['matches']):
            next_match = tournament_state['matches'][tournament_state['current_match']]
            start_new_game(next_match['white'], next_match['black'])
        else:
            tournament_state['active'] = False

# Add this AI move function at the top with other functions
def get_ai_move(ai_name, current_board):
    try:
        legal_moves = list(current_board.legal_moves)
        if not legal_moves:
            return None
            
        # Simple AI strategy for now - just random moves
        # You can enhance this later with actual AI logic
        return random.choice(legal_moves)
        
    except Exception as e:
        logging.error(f"Error in get_ai_move: {str(e)}")
        return None

# Add this after the other game endpoints
@app.route('/api/game/ai-move', methods=['POST', 'OPTIONS'])
def request_ai_move():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        global board, game_state
        if board is None or game_state is None:
            return jsonify({'error': 'No active game'}), 400

        current_player = game_state.get('currentPlayer', 'white')
        white_ai = game_state.get('whiteAI')
        black_ai = game_state.get('blackAI')
        current_ai = white_ai if current_player == 'white' else black_ai
        
        # Get AI move using the existing get_next_ai_move function
        ai_move = get_next_ai_move(board, current_ai)
        
        if ai_move is None:
            return jsonify({'error': 'No valid moves available'}), 400
            
        # Make the move
        board.push(ai_move)
        game_state['currentPlayer'] = 'black' if current_player == 'white' else 'white'
        
        # Convert board to 2D array with proper piece case preservation
        board_array = []
        for row in range(7, -1, -1):
            board_row = []
            for col in range(8):
                piece = board.piece_at(chess.square(col, row))
                if piece:
                    # Preserve case: uppercase for white, lowercase for black
                    symbol = piece.symbol().upper() if piece.color else piece.symbol().lower()
                    board_row.append(symbol)
                else:
                    board_row.append(' ')
            board_array.append(board_row)
        
        # Check for game over
        if board.is_game_over():
            game_state['status'] = 'finished'
            if board.is_checkmate():
                winner = 'black' if current_player == 'white' else 'white'
                game_state['winner'] = game_state['whiteAI'] if winner == 'white' else game_state['blackAI']
        
        # Log the board state for debugging
        logging.debug(f"Board state after move: {board_array}")
        
        return jsonify({
            'success': True,
            'move': ai_move.uci(),
            'board': board_array,
            'gameState': game_state
        })
        
    except Exception as e:
        logging.error(f"Error in request_ai_move: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5001, debug=True)            