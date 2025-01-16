from flask_socketio import SocketIO, emit
from flask import request

# Create socketio instance without app - we'll init it later
socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('move')
def handle_move(data):
    game_type = data['gameType']
    game_id = data['gameId']
    move = data['move']
    
    if game_type == 'chess':
        game = app.chess_games[game_id]
        result = game.make_move(move['from'], move['to'])
    else:
        game = app.go_games[game_id]
        result = game.make_move(move['x'], move['y'])
    
    emit('game_update', result, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
