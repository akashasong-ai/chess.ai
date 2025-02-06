from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import chess
import random
import logging
import os
from itertools import combinations
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5174"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize Socket.IO
socketio = SocketIO(app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=True,
    ping_timeout=60000,
    ping_interval=25000,
    allow_credentials=False,
    transports=['polling', 'websocket']
)

# Initialize global game state
chess_games: Dict[str, chess.Board] = {}
go_games: Dict[str, Any] = {}
game_state: Dict[str, Any] = {
    'status': 'inactive',
    'currentPlayer': 'white',
    'whiteAI': None,
    'blackAI': None,
    'winner': None
}

# Initialize tournament state
tournament_state = {
    'active': False,
    'matches': [],
    'current_match': 0,
    'results': {},
    'participants': []
}

# Initialize leaderboard
leaderboard = {
    'GPT-4': {'wins': 5, 'losses': 2, 'draws': 1},
    'Claude 2': {'wins': 4, 'losses': 3, 'draws': 1},
    'Gemini Pro': {'wins': 3, 'losses': 4, 'draws': 0},
    'Perplexity': {'wins': 2, 'losses': 5, 'draws': 2}
}

@app.route('/api/game/start', methods=['POST', 'OPTIONS'])
def start_game():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        logger.info("Starting new game...")
        data = request.get_json()
        white_ai = data.get('whiteAI')
        black_ai = data.get('blackAI')
        logger.info(f"Selected players - White: {white_ai}, Black: {black_ai}")
        
        success = start_new_game(white_ai, black_ai)
        if success:
            logger.info("Game started successfully")
            # Create a new game ID and add it to chess_games
            game_id = str(random.randint(1000, 9999))
            chess_games[game_id] = chess.Board()
            logger.info(f"Created new game with ID: {game_id}")
            return jsonify({'success': True, 'gameId': game_id})
        else:
            logger.error("Failed to start game")
            return jsonify({'error': 'Failed to start game'}), 400
    except Exception as e:
        logger.error(f"Error in start_game: {str(e)}")
        return jsonify({'error': str(e)}), 400

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
        board = chess.Board()  # Reset to new board
        game_state.update({
            'status': 'inactive',
            'currentPlayer': 'white',
            'whiteAI': None,
            'blackAI': None,
            'winner': None
        })
        tournament_state['active'] = False
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error in stop_game: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/leaderboard', methods=['GET', 'OPTIONS'])
def get_leaderboard():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        return jsonify([
            {
                'player': player,
                'score': stats['wins'] * 2 + (stats.get('draws', 0)),  # 2 points for win, 1 for draw
                'wins': stats['wins'],
                'losses': stats['losses'],
                'draws': stats.get('draws', 0),
                'winRate': round(stats['wins'] / (stats['wins'] + stats['losses'] + stats.get('draws', 0)) * 100, 1) if (stats['wins'] + stats['losses'] + stats.get('draws', 0)) > 0 else 0
            }
            for player, stats in leaderboard.items()
        ])
    except Exception as e:
        logging.error(f"Error in get_leaderboard: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'status': 'success'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('joinGame')
def handle_join_game(data):
    """Handle client joining a game"""
    try:
        if not isinstance(data, dict):
            game_id = str(data)  # Handle case where only game_id is sent
            game_type = 'chess'  # Default to chess
        else:
            game_id = str(data.get('gameId'))
            game_type = data.get('gameType', 'chess')

        logger.info(f'Client joined {game_type} game {game_id}')
        
        current_state = get_game_state_update(game_id, game_type)
        if current_state:
            emit('gameUpdate', current_state)
        else:
            logger.error(f"Game {game_id} not found")
            emit('error', {'message': f'Game {game_id} not found'})
    except Exception as e:
        logger.error(f"Error in handle_join_game: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('leaveGame')
def handle_leave_game():
    logger.info('Client left game')

@socketio.on('move')
def handle_move(data):
    """Handle game moves for both chess and go games"""
    try:
        global chess_games, go_games, game_state
        game_id = str(data.get('gameId', ''))
        move = data.get('move', {})
        game_type = data.get('gameType', 'chess')

        if not game_id:
            logger.error("No game_id provided")
            emit('error', {'message': 'No game_id provided'})
            return

        # Get current game state
        current_state = get_game_state_update(game_id, game_type)
        if not current_state:
            logger.error(f"{game_type.capitalize()} game {game_id} not found")
            emit('error', {'message': f'Game {game_id} not found'})
            return

        if game_type == 'chess':
            if not move or 'from' not in move or 'to' not in move:
                logger.error("Invalid chess move format")
                emit('error', {'message': 'Invalid move format'})
                return

            game = chess_games[game_id]
            try:
                chess_move = chess.Move.from_uci(f"{move['from']}{move['to']}")
                if chess_move in game.legal_moves:
                    game.push(chess_move)
                    
                    # Update game state
                    game_state['currentPlayer'] = 'black' if game_state['currentPlayer'] == 'white' else 'white'
                    if game.is_game_over():
                        game_state['status'] = 'finished'
                        if game.is_checkmate():
                            game_state['winner'] = 'black' if game_state['currentPlayer'] == 'white' else 'white'
                    
                    # Get updated state
                    updated_state = get_game_state_update(game_id, 'chess')
                    emit('gameUpdate', updated_state, broadcast=True)
                else:
                    emit('error', {'message': 'Invalid move'})
            except ValueError as ve:
                logger.error(f"Invalid chess move: {str(ve)}")
                emit('error', {'message': 'Invalid move format'})

        else:  # go game
            if not move or 'x' not in move or 'y' not in move:
                logger.error("Invalid go move format")
                emit('error', {'message': 'Invalid move format'})
                return

            game = go_games[game_id]
            try:
                x, y = int(move['x']), int(move['y'])
                if 0 <= x < 19 and 0 <= y < 19:  # Valid board coordinates
                    if game.make_move(x, y):
                        updated_state = get_game_state_update(game_id, 'go')
                        emit('gameUpdate', updated_state, broadcast=True)
                    else:
                        emit('error', {'message': 'Invalid move'})
                else:
                    emit('error', {'message': 'Invalid board position'})
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid go move coordinates: {str(e)}")
                emit('error', {'message': 'Invalid move coordinates'})

    except Exception as e:
        logger.error(f"Error in handle_move: {str(e)}")
        emit('error', {'message': 'Internal server error'})

def get_game_state_update(game_id: str, game_type: str = 'chess') -> Optional[dict]:
    """Helper function to get current game state"""
    try:
        if game_type == 'chess' and game_id in chess_games:
            game = chess_games[game_id]
            return {
                'board': [[str(game.piece_at(chess.square(col, row))) if game.piece_at(chess.square(col, row)) else ' '
                          for col in range(8)] for row in range(7, -1, -1)],
                'currentPlayer': game_state['currentPlayer'],
                'status': 'finished' if game.is_game_over() else 'active',
                'winner': game_state.get('winner'),
                'gameType': 'chess'
            }
        elif game_type == 'go' and game_id in go_games:
            game = go_games[game_id]
            return {
                'board': game.get_board(),
                'lastMove': None,
                'gameOver': game.is_game_over(),
                'gameType': 'go'
            }
    except Exception as e:
        logger.error(f"Error getting game state: {str(e)}")
    return None

def start_new_game(white_ai=None, black_ai=None):
    global board, game_state
    try:
        logger.info("Initializing new game state...")
        board = chess.Board()
        game_state = {
            'status': 'active',
            'currentPlayer': 'white',
            'whiteAI': white_ai,
            'blackAI': black_ai,
            'winner': None,
            'isCheck': False,
            'isCheckmate': False,
            'isStalemate': False
        }
        logger.info("Game state initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error in start_new_game: {str(e)}")
        return False

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

def get_ai_move(ai_name, current_board):
    try:
        legal_moves = list(current_board.legal_moves)
        if not legal_moves:
            return None
            
        # Simple AI strategy for now - just random moves
        return random.choice(legal_moves)
        
    except Exception as e:
        logger.error(f"Error in get_ai_move: {str(e)}")
        return None

if __name__ == '__main__':
    socketio.run(app, port=5001, debug=True)
