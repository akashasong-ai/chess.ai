import json
import os
import random
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from itertools import combinations

import chess
import eventlet
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from redis import Redis

# Initialize eventlet for async support
eventlet.monkey_patch()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://ai-arena-frontend.onrender.com", "http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Initialize Socket.IO with Redis and eventlet
socketio = SocketIO(
    app,
    cors_allowed_origins="https://ai-arena-frontend.onrender.com",
    message_queue=os.getenv('REDIS_URL', 'redis://localhost:6379'),
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=300000,  # 5 minutes to match Render.com free tier timeout
    ping_interval=25000,
    allow_credentials=True,
    transports=['websocket', 'polling']
)

# Initialize Redis client
redis_client = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

def get_game_state(game_id: str) -> Dict[str, Any]:
    """Get game state from Redis"""
    state = redis_client.get(f'game:{game_id}')
    return json.loads(state) if state else {
        'status': 'inactive',
        'currentPlayer': 'white',
        'whiteAI': None,
        'blackAI': None,
        'winner': None
    }

def set_game_state(game_id: str, state: Dict[str, Any]) -> None:
    """Save game state to Redis"""
    redis_client.set(f'game:{game_id}', json.dumps(state))

def get_tournament_state() -> Dict[str, Any]:
    """Get tournament state from Redis"""
    state = redis_client.get('tournament')
    return json.loads(state) if state else {
        'active': False,
        'matches': [],
        'current_match': 0,
        'results': {},
        'participants': []
    }

def set_tournament_state(state: Dict[str, Any]) -> None:
    """Save tournament state to Redis"""
    redis_client.set('tournament', json.dumps(state))

def get_leaderboard() -> Dict[str, Dict[str, int]]:
    """Get leaderboard from Redis"""
    board = redis_client.get('leaderboard')
    return json.loads(board) if board else {
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

@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    try:
        game_id = request.args.get('gameId')
        if not game_id:
            return jsonify({'error': 'No game ID provided'}), 400
            
        state = get_game_state(game_id)
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
        logging.error(f"Error in get_game_state: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/game/move', methods=['POST'])
def make_move():
    try:
        data = request.get_json()
        game_id = data.get('gameId')
        move = data.get('move')
        
        if not game_id:
            return jsonify({'error': 'No game ID provided'}), 400
        if not move:
            return jsonify({'error': 'No move provided'}), 400
            
        state = get_game_state(game_id)
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

@app.route('/api/game/stop', methods=['POST'])
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
def get_leaderboard_route():
    if request.method == 'OPTIONS':
        return '', 200
        
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
        
        state = get_game_state(game_id)
        if state:
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
        game_id = str(data.get('gameId', ''))
        move = data.get('move', {})
        game_type = data.get('gameType', 'chess')

        if not game_id:
            logger.error("No game_id provided")
            emit('error', {'message': 'No game_id provided'})
            return

        state = get_game_state(game_id)
        if not state:
            logger.error(f"{game_type.capitalize()} game {game_id} not found")
            emit('error', {'message': f'Game {game_id} not found'})
            return

        if game_type == 'chess':
            if not move or 'from' not in move or 'to' not in move:
                logger.error("Invalid chess move format")
                emit('error', {'message': 'Invalid move format'})
                return

            board = chess.Board(state.get('board', chess.STARTING_FEN))
            try:
                chess_move = chess.Move.from_uci(f"{move['from']}{move['to']}")
                if chess_move in board.legal_moves:
                    board.push(chess_move)
                    state['currentPlayer'] = 'black' if state['currentPlayer'] == 'white' else 'white'
                    state['board'] = board.fen()
                    
                    if board.is_game_over():
                        state['status'] = 'finished'
                        if board.is_checkmate():
                            winner = 'black' if state['currentPlayer'] == 'white' else 'white'
                            state['winner'] = state['whiteAI'] if winner == 'white' else state['blackAI']
                            
                            # Update leaderboard
                            leaderboard = get_leaderboard()
                            winner_ai = state['whiteAI'] if winner == 'white' else state['blackAI']
                            loser_ai = state['blackAI'] if winner == 'white' else state['whiteAI']
                            if winner_ai in leaderboard:
                                leaderboard[winner_ai]['wins'] += 1
                            if loser_ai in leaderboard:
                                leaderboard[loser_ai]['losses'] += 1
                            redis_client.set('leaderboard', json.dumps(leaderboard))
                    
                    set_game_state(game_id, state)
                    game_update = {
                        'board': [[str(board.piece_at(chess.square(col, row))) if board.piece_at(chess.square(col, row)) else ' '
                                for col in range(8)] for row in range(7, -1, -1)],
                        'currentPlayer': state['currentPlayer'],
                        'status': state['status'],
                        'winner': state.get('winner'),
                        'gameType': 'chess'
                    }
                    socketio.emit('gameUpdate', game_update, broadcast=True)
                    
                    if state['status'] == 'finished':
                        socketio.emit('leaderboardUpdate', get_leaderboard(), broadcast=True)
                else:
                    emit('error', {'message': 'Invalid move'})
            except ValueError as ve:
                logger.error(f"Invalid chess move: {str(ve)}")
                emit('error', {'message': 'Invalid move format'})

    except Exception as e:
        logger.error(f"Error in handle_move: {str(e)}")
        emit('error', {'message': 'Internal server error'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, server='eventlet')
