import os
import logging
from gevent import monkey
monkey.patch_all(subprocess=True, thread=False)

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Initialize logging before anything else
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Environment variables
CORS_ORIGIN = os.getenv('CORS_ORIGIN', 'https://ai-arena-frontend.onrender.com')
REDIS_URL = os.getenv('REDIS_URL', '')
PORT = int(os.environ.get('PORT', 5000))
PING_TIMEOUT = 300000  # 5 minutes to match Render.com free tier
PING_INTERVAL = 25000

# Redis configuration with proper error handling
if not REDIS_URL:
    if os.getenv('FLASK_ENV') == 'production':
        logger.error("Redis URL is required in production")
        raise ValueError("Redis URL is required in production")
    else:
        REDIS_URL = 'redis://localhost:6379'
        logger.warning("No Redis URL provided, using localhost for development")

# Initialize Flask app
app = Flask(__name__)
CORS(app, 
    resources={
        r"/api/*": {
            "origins": [CORS_ORIGIN],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True,
            "max_age": 86400
        },
        r"/socket.io/*": {
            "origins": [CORS_ORIGIN],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True,
            "max_age": 86400
        }
    },
    allow_credentials=True
)

# Initialize Socket.IO with proper transport and connection settings
socketio = SocketIO(
    app,
    cors_allowed_origins=[CORS_ORIGIN],
    message_queue=REDIS_URL if os.getenv('FLASK_ENV') == 'production' else None,
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=PING_TIMEOUT,
    ping_interval=PING_INTERVAL,
    allow_credentials=True,
    transports=['polling', 'websocket'],
    always_connect=True,
    max_http_buffer_size=1e8,
    cors_credentials=True,
    manage_session=True,
    websocket_ping_timeout=PING_TIMEOUT,
    websocket_ping_interval=PING_INTERVAL,
    upgrade_timeout=20000,
    cookie_path='/socket.io/',
    cookie_samesite='Strict',
    path='/socket.io/',
    reconnection=True,
    reconnection_attempts=5,
    reconnection_delay=1000,
    reconnection_delay_max=5000
)

# Import Tournament class after app initialization to avoid circular imports
from backend.tournament import Tournament

__all__ = ['app', 'socketio', 'Tournament']
