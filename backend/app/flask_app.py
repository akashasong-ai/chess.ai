from flask import request, jsonify
from flask_socketio import SocketIO, emit
import chess
import random
import logging
import os
from itertools import combinations
import time
from pathlib import Path
from typing import Dict, Optional, Any
from backend.app import app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
