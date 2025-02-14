import json
import os
import random
import logging
from typing import Dict, Optional, Any, List, Callable, Union
from functools import wraps
import chess
from flask import request, jsonify, make_response
from flask_socketio import emit
from backend.app_factory import app, socketio, redis_client
from backend.tournament import Tournament, TournamentStatus

logger = logging.getLogger(__name__)

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

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Environment variables
REDIS_URL = os.getenv('REDIS_URL', '')
if not REDIS_URL and os.getenv('FLASK_ENV') != 'production':
    REDIS_URL = 'redis://localhost:6379'
    logger.warning("No Redis URL provided, using localhost for development")

# Use redis_client from app_factory
if redis_client is None:
    logger.warning("Redis client not available, using in-memory state")
else:
    logger.info("Using Redis client from app_factory")

def get_game_state_from_redis(game_id: str) -> Dict[str, Any]:
    """Get game state from Redis with improved error handling and fallback"""
    default_state = {
        'status': 'inactive',
        'currentPlayer': 'white',
        'whiteAI': None,
        'blackAI': None,
        'winner': None
    }
    
    # Use in-memory state if Redis is not configured
    if redis_client is None:
        logger.warning("Redis not available, using in-memory state")
        return default_state
        
    try:
        # Attempt to get state from Redis with timeout
        state = redis_client.get(f'game:{game_id}')
        if not state:
            logger.info(f"No state found for game {game_id}, using default")
            return default_state
            
        try:
            parsed_state = json.loads(state)
            return parsed_state
        except json.JSONDecodeError as je:
            logger.error(f"Invalid JSON in Redis for game {game_id}: {je}")
            return default_state
            
    except Exception as e:
        logger.error(f"Redis error for game {game_id}: {e}")
        if os.getenv('FLASK_ENV') == 'production':
            # In production, propagate Redis errors for monitoring
            logger.error("Redis error in production environment")
            raise
        return default_state

def set_game_state(game_id: str, state: Dict[str, Any]) -> None:
    """Save game state to Redis"""
    if redis_client is None:
        logger.warning("Redis not available, state will not persist")
        return
    try:
        redis_client.set(f'game:{game_id}', json.dumps(state))
    except Exception as e:
        logger.error(f"Error saving game state to Redis: {e}")

def get_tournament_state() -> Dict[str, Any]:
    """Get tournament state from Redis"""
    default_state = {
        'active': False,
        'matches': [],
        'current_match': 0,
        'results': {},
        'participants': []
    }
    if redis_client is None:
        logger.warning("Redis not available, using in-memory state")
        return default_state
    try:
        state = redis_client.get('tournament')
        return json.loads(state) if state else default_state
    except Exception as e:
        logger.error(f"Error getting tournament state from Redis: {e}")
        return default_state

def set_tournament_state(state: Dict[str, Any]) -> None:
    """Save tournament state to Redis"""
    if redis_client is None:
        logger.warning("Redis not available, state will not persist")
        return
    try:
        redis_client.set('tournament', json.dumps(state))
    except Exception as e:
        logger.error(f"Error saving tournament state to Redis: {e}")

def get_leaderboard() -> Dict[str, Dict[str, int]]:
    """Get leaderboard from Redis"""
    default_board = {
        'GPT-4': {'wins': 5, 'losses': 2, 'draws': 1},
        'Claude 2': {'wins': 4, 'losses': 3, 'draws': 1},
        'Gemini Pro': {'wins': 3, 'losses': 4, 'draws': 0},
        'Perplexity': {'wins': 2, 'losses': 5, 'draws': 2}
    }
    if redis_client is None:
        logger.warning("Redis not available, using default leaderboard")
        return default_board
    try:
        board = redis_client.get('leaderboard')
        return json.loads(board) if board else default_board
    except Exception as e:
        logger.error(f"Error getting leaderboard from Redis: {e}")
        return default_board

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

@app.route('/api/tournament/start', methods=['POST', 'OPTIONS'])
@validate_request(['players', 'gameType'])
def start_tournament():
    try:
        data = request.get_json()
        players = data.get('players', [])
        game_type = data.get('gameType', 'chess')
        num_games = data.get('numGames', 1)
        time_control = data.get('timeControl', 600)

        if not players or len(players) < 2:
            return jsonify({'error': 'At least 2 players required'}), 400

        tournament = Tournament(game_type, players, num_games, time_control)
        tournament.start()
        
        # Store tournament state in Redis
        tournament_state = tournament.get_status()
        set_tournament_state(tournament_state)
        
        return jsonify({
            'success': True,
            'status': tournament_state
        })
    except Exception as e:
        logger.error(f"Error in start_tournament: {str(e)}")
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
    error_message = str(e)
    logger.error(f"WebSocket error: {error_message}")
    
    if "Redis" in error_message:
        if os.getenv('FLASK_ENV') == 'production':
            emit('error', {'message': 'Server error: Unable to access game state. Please try again later.'})
            raise  # Re-raise in production for monitoring
        else:
            emit('error', {'message': 'Development: Redis unavailable, using in-memory state'})
    elif "WebSocket" in error_message or "transport" in error_message:
        emit('error', {'message': 'Connection error. Attempting to reconnect...'})
    else:
        emit('error', {'message': 'An unexpected error occurred. Please try again.'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection with improved error handling"""
    try:
        logger.info('Client connected')
        # Verify Redis connection in production
        if os.getenv('FLASK_ENV') == 'production' and redis_client:
            try:
                redis_client.ping()
            except Exception as redis_error:
                logger.error(f"Redis health check failed on connect: {redis_error}")
                emit('error', {'message': 'Server error: Game state service unavailable'})
                return False
        emit('connected', {'status': 'success'})
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        emit('error', {'message': 'Failed to establish connection'})
        return False

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
