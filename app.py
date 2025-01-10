from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import random
import time
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5174"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Global variables to store game state
current_game = None
game_board = chess.Board()
leaderboard = []
current_players = {'white': None, 'black': None}
game_status = "not_started"
last_move_time = None
thinking_start_time = None

@app.route('/api/game/start', methods=['POST'])
def start_game():
    global current_game, game_board, current_players, game_status, thinking_start_time
    
    data = request.get_json()
    white_player = data.get('whitePlayer')
    black_player = data.get('blackPlayer')
    
    game_board = chess.Board()
    current_players = {'white': white_player, 'black': black_player}
    game_status = "in_progress"
    thinking_start_time = datetime.now()
    
    return jsonify({
        'status': 'success',
        'message': 'Game started',
        'board': str(game_board)
    })

@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    global game_board, current_players, game_status
    
    if game_status == "not_started":
        return jsonify({
            'status': 'not_started',
            'message': 'No game in progress'
        })
    
    return jsonify({
        'status': game_status,
        'board': str(game_board),
        'currentPlayer': 'white' if game_board.turn else 'black',
        'isCheck': game_board.is_check(),
        'isCheckmate': game_board.is_checkmate(),
        'isStalemate': game_board.is_stalemate(),
        'whiteAI': current_players['white'],
        'blackAI': current_players['black']
    })

@app.route('/api/game/move/wait', methods=['GET'])
def wait_for_ai_move():
    global game_board, thinking_start_time, last_move_time
    
    if game_status != "in_progress":
        return jsonify({
            'status': 'error',
            'message': 'No game in progress'
        })

    # Simulate AI thinking time (2-4 seconds)
    thinking_time = random.uniform(2, 4)
    time.sleep(thinking_time)
    
    # Get legal moves
    legal_moves = list(game_board.legal_moves)
    if not legal_moves:
        return jsonify({
            'status': 'error',
            'message': 'No legal moves available'
        })
    
    # Make a random move
    move = random.choice(legal_moves)
    game_board.push(move)
    
    # Update timestamps
    last_move_time = datetime.now()
    thinking_start_time = datetime.now()
    
    return jsonify({
        'status': 'success',
        'move': move.uci(),
        'board': str(game_board)
    })

@app.route('/api/game/stop', methods=['POST'])
def stop_game():
    global game_status, current_players
    game_status = "not_started"
    current_players = {'white': None, 'black': None}
    return jsonify({'status': 'success', 'message': 'Game stopped'})

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    # Placeholder leaderboard data
    return jsonify([
        {'model': 'GPT-4', 'wins': 0, 'losses': 0, 'draws': 0},
        {'model': 'Claude 2', 'wins': 0, 'losses': 0, 'draws': 0},
        {'model': 'Gemini Pro', 'wins': 0, 'losses': 0, 'draws': 0}
    ])

if __name__ == '__main__':
    app.run(port=5001, debug=True)