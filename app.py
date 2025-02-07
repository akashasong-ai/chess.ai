import json
import os
import random
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List, Callable
from itertools import combinations
from functools import wraps

import chess
from gevent import monkey; monkey.patch_all()
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from redis import Redis

def validate_request(required_fields: Optional[List[str]] = None):
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'OPTIONS':
                return '', 200
            if required_fields and request.is_json:
                data = request.get_json()
                missing = [field for field in required_fields if not data.get(field)]
                if missing:
                    return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Environment variables
CORS_ORIGIN = os.getenv('CORS_ORIGIN', 'https://ai-arena-frontend.onrender.com')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
PORT = int(os.environ.get('PORT', 5000))
PING_TIMEOUT = 300000  # 5 minutes to match Render.com free tier
PING_INTERVAL = 25000

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, 
    resources={r"/*": {
        "origins": [os.getenv('CORS_ORIGIN', 'https://ai-arena-frontend.onrender.com')],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True,
        "send_wildcard": False,
        "max_age": 86400
    }},
    allow_credentials=True
)

# Initialize Socket.IO with Redis and eventlet
socketio = SocketIO(
    app,
    cors_allowed_origins=[
        os.getenv('CORS_ORIGIN', 'https://ai-arena-frontend.onrender.com'),
        'http://localhost:5173',  # Vite dev server
        'http://127.0.0.1:5173'
    ],
    message_queue=REDIS_URL if os.getenv('FLASK_ENV') == 'production' else None,
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=PING_TIMEOUT,
    ping_interval=PING_INTERVAL,
    allow_credentials=True,
    transports=['polling', 'websocket'],
    upgrade_timeout=20000,
    max_http_buffer_size=1e8,
    always_connect=True
)

# Initialize Redis connection with robust error handling and fallback
redis_client = None
in_memory_state = {}

def init_redis():
    global redis_client
    try:
        client = Redis.from_url(REDIS_URL)
        client.ping()  # Test connection
        logger.info("Redis connection successful")
        redis_client = client
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        redis_client = None
        if os.getenv('FLASK_ENV') == 'production':
            # Retry connection in production
            for i in range(3):
                try:
                    time.sleep(2 ** i)  # Exponential backoff
                    client = Redis.from_url(REDIS_URL)
                    client.ping()
                    logger.info(f"Redis connection successful after {i+1} retries")
                    redis_client = client
                    return True
                except Exception as retry_error:
                    logger.error(f"Redis retry {i+1} failed: {retry_error}")
            raise  # All retries failed in production
        return False

# Initialize Redis with retries
init_redis()

def get_game_state_from_redis(game_id: str) -> Dict[str, Any]:
    """Get game state from Redis with fallback to in-memory state"""
    default_state = {
        'status': 'inactive',
        'currentPlayer': 'white',
        'whiteAI': None,
        'blackAI': None,
        'winner': None
    }
    
    # Try to reconnect if Redis is down
    if redis_client is None and os.getenv('FLASK_ENV') == 'production':
        init_redis()
    
    key = f'game:{game_id}'
    try:
        if redis_client is not None:
            state = redis_client.get(key)
            if state:
                return json.loads(state)
    except Exception as e:
        logger.error(f"Error getting game state from Redis: {e}")
        if os.getenv('FLASK_ENV') == 'production':
            init_redis()  # Try to reconnect
    
    # Fallback to in-memory state
    logger.warning(f"Using in-memory state for game {game_id}")
    return in_memory_state.get(key, default_state)

def set_game_state(game_id: str, state: Dict[str, Any]) -> None:
    """Save game state to Redis with fallback to in-memory state"""
    key = f'game:{game_id}'
    
    # Always update in-memory state as fallback
    in_memory_state[key] = state
    
    # Try to reconnect if Redis is down
    if redis_client is None and os.getenv('FLASK_ENV') == 'production':
        init_redis()
    
    if redis_client is not None:
        try:
            redis_client.set(key, json.dumps(state))
        except Exception as e:
            logger.error(f"Error saving game state to Redis: {e}")
            if os.getenv('FLASK_ENV') == 'production':
                init_redis()  # Try to reconnect

def get_tournament_state() -> Dict[str, Any]:
    """Get tournament state from Redis with fallback to in-memory state"""
    default_state = {
        'active': False,
        'matches': [],
        'current_match': 0,
        'results': {},
        'participants': []
    }
    
    # Try to reconnect if Redis is down
    if redis_client is None and os.getenv('FLASK_ENV') == 'production':
        init_redis()
    
    key = 'tournament'
    try:
        if redis_client is not None:
            state = redis_client.get(key)
            if state:
                return json.loads(state)
    except Exception as e:
        logger.error(f"Error getting tournament state from Redis: {e}")
        if os.getenv('FLASK_ENV') == 'production':
            init_redis()  # Try to reconnect
    
    # Fallback to in-memory state
    logger.warning("Using in-memory tournament state")
    return in_memory_state.get(key, default_state)

def set_tournament_state(state: Dict[str, Any]) -> None:
    """Save tournament state to Redis with fallback to in-memory state"""
    key = 'tournament'
    
    # Always update in-memory state as fallback
    in_memory_state[key] = state
    
    # Try to reconnect if Redis is down
    if redis_client is None and os.getenv('FLASK_ENV') == 'production':
        init_redis()
    
    if redis_client is not None:
        try:
            redis_client.set(key, json.dumps(state))
        except Exception as e:
            logger.error(f"Error saving tournament state to Redis: {e}")
            if os.getenv('FLASK_ENV') == 'production':
                init_redis()  # Try to reconnect

def get_leaderboard() -> Dict[str, Dict[str, int]]:
    """Get leaderboard from Redis with fallback to in-memory state"""
    default_board = {
        'GPT-4': {'wins': 5, 'losses': 2, 'draws': 1},
        'Claude 2': {'wins': 4, 'losses': 3, 'draws': 1},
        'Gemini Pro': {'wins': 3, 'losses': 4, 'draws': 0},
        'Perplexity': {'wins': 2, 'losses': 5, 'draws': 2}
    }
    
    # Try to reconnect if Redis is down
    if redis_client is None and os.getenv('FLASK_ENV') == 'production':
        init_redis()
    
    key = 'leaderboard'
    try:
        if redis_client is not None:
            board = redis_client.get(key)
            if board:
                return json.loads(board)
    except Exception as e:
        logger.error(f"Error getting leaderboard from Redis: {e}")
        if os.getenv('FLASK_ENV') == 'production':
            init_redis()  # Try to reconnect
    
    # Fallback to in-memory state
    logger.warning("Using in-memory leaderboard")
    return in_memory_state.get(key, default_board)

@app.route('/api/game/start', methods=['POST', 'OPTIONS'])
@validate_request(['whiteAI', 'blackAI'])
def start_game():
        
    try:
        logger.info("Starting new game...")
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
            
        white_ai = data.get('whiteAI')
        black_ai = data.get('blackAI')
        if not white_ai or not black_ai:
            return jsonify({'error': 'Missing required fields: whiteAI and blackAI'}), 400
            
        logger.info(f"Selected players - White: {white_ai}, Black: {black_ai}")
        
        game_id = str(random.randint(1000, 9999))
        board = chess.Board()
        game_state = {
            'status': 'active',
            'currentPlayer': 'white',
            'whiteAI': white_ai,
            'blackAI': black_ai,
            'winner': None,
            'board': board.fen()
        }
        
        set_game_state(game_id, game_state)
        logger.info(f"Created new game with ID: {game_id}")
        return jsonify({'success': True, 'gameId': game_id})
    except Exception as e:
        logger.error(f"Error in start_game: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/game/state', methods=['GET', 'OPTIONS'])
@validate_request(['gameId'])
def get_game_state_route():
    try:
        game_id = request.args.get('gameId')
        if not game_id:
            return jsonify({'error': 'No game ID provided'}), 400
            
        state = get_game_state_from_redis(game_id)
        if not state:
            return jsonify({'error': 'No active game found'}), 400
            
        board = chess.Board(state.get('board', chess.STARTING_FEN))
        board_array = []
        for row in range(7, -1, -1):
            board_row = []
            for col in range(8):
                piece = board.piece_at(chess.square(col, row))
                if piece:
                    symbol = piece.symbol().upper() if piece.color else piece.symbol().lower()
                    board_row.append(symbol)
                else:
                    board_row.append(' ')
            board_array.append(board_row)
            
        logger.debug(f"Current board state for game {game_id}: {board_array}")
            
        return jsonify({
            'board': board_array,
            'gameState': {
                'status': 'finished' if board.is_game_over() else 'active',
                'currentPlayer': state.get('currentPlayer', 'white'),
                'whiteAI': state.get('whiteAI'),
                'blackAI': state.get('blackAI'),
                'winner': state.get('winner'),
                'fen': board.fen()
            }
        })
    except Exception as e:
        logging.error(f"Error in get_game_state_route: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/game/move', methods=['POST', 'OPTIONS'])
@validate_request(['gameId', 'move'])
def make_move():
    try:
        data = request.get_json()
        game_id = data.get('gameId')
        move = data.get('move')
        
        if not game_id:
            return jsonify({'error': 'No game ID provided'}), 400
        if not move:
            return jsonify({'error': 'No move provided'}), 400
            
        state = get_game_state_from_redis(game_id)
        if not state:
            return jsonify({'error': 'No active game found'}), 400
            
        board = chess.Board(state.get('board', chess.STARTING_FEN))
        chess_move = chess.Move.from_uci(move)
        
        if chess_move in board.legal_moves:
            board.push(chess_move)
            current_player = state.get('currentPlayer', 'white')
            state['currentPlayer'] = 'black' if current_player == 'white' else 'white'
            state['board'] = board.fen()
            
            if board.is_game_over():
                state['status'] = 'finished'
                if board.is_checkmate():
                    winner = 'black' if current_player == 'white' else 'white'
                    white_ai = state.get('whiteAI')
                    black_ai = state.get('blackAI')
                    state['winner'] = white_ai if winner == 'white' else black_ai
            
            set_game_state(game_id, state)
            board_array = [[str(board.piece_at(chess.square(col, row))) if board.piece_at(chess.square(col, row)) else ' '
                          for col in range(8)] for row in range(7, -1, -1)]
                
            return jsonify({
                'success': True,
                'board': board_array,
                'gameState': state
            })
        else:
            return jsonify({'error': 'Invalid move'}), 400
            
    except Exception as e:
        logger.error(f"Error in make_move: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/game/stop', methods=['POST', 'OPTIONS'])
@validate_request(['gameId'])
def stop_game():
    try:
        data = request.get_json()
        game_id = data.get('gameId')
        
        if not game_id:
            return jsonify({'error': 'No game ID provided'}), 400
            
        state = {
            'status': 'inactive',
            'currentPlayer': 'white',
            'whiteAI': None,
            'blackAI': None,
            'winner': None,
            'board': chess.Board().fen()
        }
        set_game_state(game_id, state)
        
        tournament_state = get_tournament_state()
        tournament_state['active'] = False
        set_tournament_state(tournament_state)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error in stop_game: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/leaderboard', methods=['GET', 'OPTIONS'])
@validate_request()
def get_leaderboard_route():
        
    try:
        board = get_leaderboard()
        return jsonify([
            {
                'player': player,
                'score': stats['wins'] * 2 + (stats.get('draws', 0)),  # 2 points for win, 1 for draw
                'wins': stats['wins'],
                'losses': stats['losses'],
                'draws': stats.get('draws', 0),
                'winRate': round(stats['wins'] / (stats['wins'] + stats['losses'] + stats.get('draws', 0)) * 100, 1) if (stats['wins'] + stats['losses'] + stats.get('draws', 0)) > 0 else 0
            }
            for player, stats in board.items()
        ])
    except Exception as e:
        logger.error(f"Error in get_leaderboard: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Socket.IO event handlers
@socketio.on_error_default
def default_error_handler(e):
    logger.error(f"WebSocket error: {str(e)}")
    emit('error', {'message': 'Internal server error'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        logger.info('Client connected')
        emit('connected', {'status': 'success'})
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return False  # Reject connection on error

@socketio.on('connect_error')
def handle_connect_error(error):
    """Handle connection errors"""
    logger.error(f"Connection error: {str(error)}")
    emit('error', {'message': 'Connection failed'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        logger.info('Client disconnected')
    except Exception as e:
        logger.error(f"Disconnect error: {str(e)}")
        emit('error', {'message': 'Error during disconnect'})

@socketio.on('joinGame')
def handle_join_game(data):
    """Handle client joining a game"""
    try:
        # Validate input data
        if not data:
            logger.error("No data provided for joinGame")
            emit('error', {'message': 'No game data provided'})
            return

        if not isinstance(data, dict):
            game_id = str(data)  # Handle case where only game_id is sent
            game_type = 'chess'  # Default to chess
        else:
            game_id = str(data.get('gameId'))
            if not game_id:
                logger.error("No game ID provided")
                emit('error', {'message': 'Game ID is required'})
                return
            game_type = data.get('gameType', 'chess')

        logger.info(f'Client joining {game_type} game {game_id}')
        
        # Get game state with error handling
        try:
            state = get_game_state_from_redis(game_id)
        except Exception as redis_error:
            logger.error(f"Redis error while getting game state: {str(redis_error)}")
            emit('error', {'message': 'Failed to retrieve game state'})
            return

        if not state:
            logger.error(f"Game {game_id} not found")
            emit('error', {'message': f'Game {game_id} not found'})
            return

        # Set up game board with error handling
        try:
            board = chess.Board(state.get('board', chess.STARTING_FEN))
            board_array = [[str(board.piece_at(chess.square(col, row))) if board.piece_at(chess.square(col, row)) else ' '
                          for col in range(8)] for row in range(7, -1, -1)]
            
            emit('gameUpdate', {
                'board': board_array,
                'currentPlayer': state['currentPlayer'],
                'status': state['status'],
                'winner': state.get('winner'),
                'gameType': game_type
            })
            logger.info(f'Successfully joined game {game_id}')
        except Exception as chess_error:
            logger.error(f"Chess error while setting up board: {str(chess_error)}")
            emit('error', {'message': 'Failed to set up game board'})
            return

    except Exception as e:
        logger.error(f"Error in handle_join_game: {str(e)}")
        emit('error', {'message': 'Internal server error while joining game'})

@socketio.on('leaveGame')
def handle_leave_game():
    """Handle client leaving a game"""
    try:
        logger.info('Client left game')
    except Exception as e:
        logger.error(f"Error in handle_leave_game: {str(e)}")
        emit('error', {'message': 'Error leaving game'})

@socketio.on('move')
def handle_move(data):
    """Handle game moves for both chess and go games"""
    try:
        # Validate input data
        if not isinstance(data, dict):
            logger.error("Invalid move data format")
            emit('error', {'message': 'Invalid move data format'})
            return

        game_id = str(data.get('gameId', ''))
        move = data.get('move', {})
        game_type = data.get('gameType', 'chess')

        if not game_id:
            logger.error("No game_id provided")
            emit('error', {'message': 'Game ID is required'})
            return

        # Get game state with error handling
        try:
            state = get_game_state_from_redis(game_id)
        except Exception as redis_error:
            logger.error(f"Redis error while getting game state: {str(redis_error)}")
            emit('error', {'message': 'Failed to retrieve game state'})
            return

        if not state:
            logger.error(f"{game_type.capitalize()} game {game_id} not found")
            emit('error', {'message': f'Game {game_id} not found'})
            return

        if game_type == 'chess':
            # Validate chess move format
            if not isinstance(move, dict) or 'from' not in move or 'to' not in move:
                logger.error("Invalid chess move format")
                emit('error', {'message': 'Invalid move format - requires "from" and "to" positions'})
                return

            try:
                board = chess.Board(state.get('board', chess.STARTING_FEN))
            except Exception as board_error:
                logger.error(f"Error creating chess board: {str(board_error)}")
                emit('error', {'message': 'Failed to set up game board'})
                return

            try:
                # Validate and make move
                chess_move = chess.Move.from_uci(f"{move['from']}{move['to']}")
                if chess_move not in board.legal_moves:
                    emit('error', {'message': 'Invalid move - not a legal chess move'})
                    return

                # Make the move
                board.push(chess_move)
                state['currentPlayer'] = 'black' if state['currentPlayer'] == 'white' else 'white'
                state['board'] = board.fen()
                
                # Check game over conditions
                if board.is_game_over():
                    state['status'] = 'finished'
                    if board.is_checkmate():
                        winner = 'black' if state['currentPlayer'] == 'white' else 'white'
                        state['winner'] = state['whiteAI'] if winner == 'white' else state['blackAI']
                        
                        try:
                            # Update leaderboard
                            leaderboard = get_leaderboard()
                            winner_ai = state['whiteAI'] if winner == 'white' else state['blackAI']
                            loser_ai = state['blackAI'] if winner == 'white' else state['whiteAI']
                            if winner_ai in leaderboard:
                                leaderboard[winner_ai]['wins'] += 1
                            if loser_ai in leaderboard:
                                leaderboard[loser_ai]['losses'] += 1
                            if redis_client is not None:
                                try:
                                    redis_client.set('leaderboard', json.dumps(leaderboard))
                                except Exception as leaderboard_error:
                                    logger.error(f"Error updating leaderboard: {str(leaderboard_error)}")
                            else:
                                logger.warning("Redis not available, leaderboard will not persist")
                        except Exception as e:
                            logger.error(f"Error updating game outcome: {str(e)}")
                
                # Save game state
                try:
                    set_game_state(game_id, state)
                except Exception as e:
                    logger.error(f"Error saving game state: {str(e)}")
                    emit('error', {'message': 'Failed to save game state'})
                    return

                # Prepare and send game update
                try:
                    game_update = {
                        'board': [[str(board.piece_at(chess.square(col, row))) if board.piece_at(chess.square(col, row)) else ' '
                                for col in range(8)] for row in range(7, -1, -1)],
                        'currentPlayer': state['currentPlayer'],
                        'status': state['status'],
                        'winner': state.get('winner'),
                        'gameType': 'chess'
                    }
                    socketio.emit('gameUpdate', game_update, to=None)
                    
                    if state['status'] == 'finished':
                        socketio.emit('leaderboardUpdate', get_leaderboard(), to=None)
                except Exception as emit_error:
                    logger.error(f"Error emitting game update: {str(emit_error)}")
                    emit('error', {'message': 'Failed to send game update'})
                    return

            except ValueError as ve:
                logger.error(f"Invalid chess move format: {str(ve)}")
                emit('error', {'message': 'Invalid move format - must be valid chess notation'})
            except Exception as chess_error:
                logger.error(f"Chess error: {str(chess_error)}")
                emit('error', {'message': 'Error processing chess move'})

    except Exception as e:
        logger.error(f"Error in handle_move: {str(e)}")
        emit('error', {'message': 'Internal server error while processing move'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, use_reloader=False, log_output=True, server_class='gevent')
