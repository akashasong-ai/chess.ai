from app import db
from datetime import datetime

class LLM(db.Model):
    __tablename__ = 'llm'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    api_type = db.Column(db.String(20), nullable=False)  # e.g., 'openai', 'custom'
    api_key = db.Column(db.String(100))
    elo_rating = db.Column(db.Integer, default=1500)
    games_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)

    # Add relationships
    white_games = db.relationship('Game', foreign_keys='Game.white_llm_id', backref='white_llm', lazy=True)
    black_games = db.relationship('Game', foreign_keys='Game.black_llm_id', backref='black_llm', lazy=True)

class Game(db.Model):
    __tablename__ = 'game'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    white_llm_id = db.Column(db.Integer, db.ForeignKey('llm.id', ondelete='CASCADE'), nullable=False)
    black_llm_id = db.Column(db.Integer, db.ForeignKey('llm.id', ondelete='CASCADE'), nullable=False)
    moves = db.Column(db.Text, default='')
    result = db.Column(db.String(10))  # '1-0', '0-1', '1/2-1/2'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime) 