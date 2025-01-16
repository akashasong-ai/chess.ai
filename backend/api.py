from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os
from chess_engine import ChessGame
from go_board import GoBoard
from tournament import Tournament
from leaderboard import Leaderboard
from utils import validate_move, calculate_elo

# Load environment variables
load_dotenv()

# Get API keys
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')
GOOGLE_KEY = os.getenv('GOOGLE_API_KEY')

if not all([OPENAI_KEY, ANTHROPIC_KEY, GOOGLE_KEY]):
    raise ValueError("Missing required API keys in .env file")

# Add this after the API key checks
print("API Keys loaded successfully:")
print(f"OpenAI: {OPENAI_KEY[:8]}...")  # Only print first 8 chars
print(f"Anthropic: {ANTHROPIC_KEY[:8]}...")
print(f"Google: {GOOGLE_KEY[:8]}...")

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize game storage
chess_games = {}
go_games = {}
tournaments = {}
chess_leaderboard = Leaderboard('chess')
go_leaderboard = Leaderboard('go')

# Store games in app context
app.chess_games = chess_games
app.go_games = go_games

@app.route('/chess/start', methods=['POST'])
def start_chess_game():
    data = request.json
    game_id = len(chess_games)
    chess_games[game_id] = ChessGame(data['player1'], data['player2'])
    return jsonify({'gameId': game_id, 'board': chess_games[game_id].get_board()})

@app.route('/chess/move', methods=['POST'])
def make_chess_move():
    data = request.json
    game = chess_games[data['gameId']]
    move = data['move']
    
    if not validate_move('chess', game.get_board(), move):
        return jsonify({'valid': False, 'message': 'Invalid move'})
        
    result = game.make_move(move['from'], move['to'])
    return jsonify({
        'valid': result['valid'],
        'board': game.get_board(),
        'status': game.get_status()
    })

@app.route('/go/start', methods=['POST'])
def start_go_game():
    data = request.json
    game_id = len(go_games)
    go_games[game_id] = GoBoard(data['player1'], data['player2'])
    return jsonify({'gameId': game_id, 'board': go_games[game_id].get_board()})

@app.route('/go/move', methods=['POST'])
def make_go_move():
    data = request.json
    game = go_games[data['gameId']]
    move = data['move']
    
    if not validate_move('go', game.get_board(), move):
        return jsonify({'valid': False, 'message': 'Invalid move'})
        
    result = game.make_move(move['x'], move['y'])
    return jsonify({
        'valid': result,
        'board': game.get_board(),
        'currentPlayer': game.current_player
    })

@app.route('/<game_type>/tournament', methods=['POST'])
def start_tournament(game_type):
    data = request.json
    tournament_id = len(tournaments)
    tournaments[tournament_id] = Tournament(game_type, data['players'])
    tournaments[tournament_id].start()
    return jsonify({
        'id': tournament_id,
        'status': tournaments[tournament_id].get_status()
    })

@app.route('/<game_type>/tournament/<int:tournament_id>', methods=['GET'])
def get_tournament_status(game_type, tournament_id):
    tournament = tournaments[tournament_id]
    return jsonify(tournament.get_status())

@app.route('/<game_type>/leaderboard', methods=['GET'])
def get_leaderboard(game_type):
    if game_type == 'chess':
        return jsonify(chess_leaderboard.get_rankings())
    else:
        return jsonify(go_leaderboard.get_rankings())

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('joinGame')
def handle_join_game(game_id):
    print(f'Client joined game {game_id}')

@socketio.on('leaveGame')
def handle_leave_game():
    print('Client left game')

@socketio.on('move')
def handle_move(data):
    game_id = data.get('gameId')
    move = data.get('move')
    if game_id in chess_games:
        game = chess_games[game_id]
        result = game.make_move(move['from'], move['to'])
        if result['valid']:
            emit('gameUpdate', game.get_status(), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)
