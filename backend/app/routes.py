from flask import Blueprint, jsonify, request
from app.models import LLM, Game
from app.game_logic import ChessGame
from app import db

main = Blueprint('main', __name__)

@main.route('/api/llms', methods=['GET'])
def get_llms():
    llms = LLM.query.all()
    return jsonify([{
        'id': llm.id,
        'name': llm.name,
        'elo_rating': llm.elo_rating,
        'games_played': llm.games_played
    } for llm in llms])

@main.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.json
    white_llm_id = data.get('white_llm_id')
    black_llm_id = data.get('black_llm_id')

    game = ChessGame(white_llm_id, black_llm_id)
    result = game.play_game()

    return jsonify({
        'game_id': game.game.id,
        'result': result,
        'moves': game.game.moves
    })

@main.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    llms = LLM.query.order_by(LLM.elo_rating.desc()).all()
    return jsonify([{
        'name': llm.name,
        'elo_rating': llm.elo_rating,
        'wins': llm.wins,
        'losses': llm.losses,
        'draws': llm.draws
    } for llm in llms])

@main.route('/api/llms', methods=['POST'])
def add_llm():
    data = request.json
    required_fields = ['name', 'api_type']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
        
    if data['api_type'] not in ['openai', 'gemini', 'claude']:
        return jsonify({'error': 'Invalid API type'}), 400
    
    llm = LLM(
        name=data['name'],
        api_type=data['api_type'],
        api_key=data.get('api_key')  # Optional, as we're using environment variables
    )
    
    db.session.add(llm)
    db.session.commit()
    
    return jsonify({
        'id': llm.id,
        'name': llm.name,
        'api_type': llm.api_type,
        'elo_rating': llm.elo_rating
    }) 