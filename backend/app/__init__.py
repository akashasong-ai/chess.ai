from flask import Flask

# Create Flask app
flask_app = Flask(__name__)

# Import game state first
from .flask_app import board, game_state, tournament_state, leaderboard

# Then import FastAPI app
from .main import app

__all__ = [
    'app',
    'flask_app',
    'board',
    'game_state',
    'tournament_state',
    'leaderboard'
]
