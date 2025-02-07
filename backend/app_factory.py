from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import logging

logger = logging.getLogger(__name__)

# Environment variables
CORS_ORIGIN = os.getenv('CORS_ORIGIN', 'https://ai-arena-frontend.onrender.com')
REDIS_URL = os.getenv('REDIS_URL', '')
if not REDIS_URL and os.getenv('FLASK_ENV') != 'production':
    REDIS_URL = 'redis://localhost:6379'
    logger.warning("No Redis URL provided, using localhost for development")
PORT = int(os.environ.get('PORT', 5000))
PING_TIMEOUT = 300000  # 5 minutes to match Render.com free tier
PING_INTERVAL = 25000

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

# Initialize Socket.IO
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
    upgrade_timeout=10000,
    cookie_path='/socket.io/',
    cookie_samesite='Strict'
)
