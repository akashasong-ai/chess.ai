"""
Chess.ai backend package
"""
from backend.app import app
from backend.app.flask_app import socketio

__all__ = ['app', 'socketio']
