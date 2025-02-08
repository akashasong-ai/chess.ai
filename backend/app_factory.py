import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import os
import eventlet
import json
from redis import Redis
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Initialize Redis first
eventlet.monkey_patch()

# Environment variables
CORS_ORIGIN = os.getenv('CORS_ORIGIN', 'https://chess-ai-frontend.onrender.com')
REDIS_URL = os.getenv('REDIS_URL', '')
PORT = int(os.environ.get('PORT', 5000))
PING_TIMEOUT = 300000  # 5 minutes to match Render.com free tier
PING_INTERVAL = 25000

# Redis configuration
redis_client = None

try:
    if REDIS_URL:
        redis_client = Redis.from_url(REDIS_URL, socket_timeout=5)
        redis_client.ping()
        logger.info("Redis connection successful")
    elif os.getenv('FLASK_ENV') == 'production':
        raise ValueError("Redis URL is required in production")
    else:
        logger.warning("No Redis URL provided, using in-memory state for development")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    if os.getenv('FLASK_ENV') == 'production':
        raise
    redis_client = None

# Initialize Redis client early to catch connection issues
from redis import Redis
redis_client = None
try:
    if REDIS_URL:
        redis_client = Redis.from_url(REDIS_URL, socket_timeout=5)
        redis_client.ping()
        logger.info("Redis connection successful")
    elif os.getenv('FLASK_ENV') == 'production':
        raise ValueError("Redis URL is required in production")
    else:
        logger.warning("No Redis URL provided, using in-memory state for development")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    if os.getenv('FLASK_ENV') == 'production':
        raise
    redis_client = None

# Initialize Flask app after Redis
app = Flask(__name__)

# Configure CORS
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

# Initialize Socket.IO with Redis message queue
socketio = SocketIO(
    app,
    cors_allowed_origins=[CORS_ORIGIN],
    message_queue=REDIS_URL if redis_client else None,
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=PING_TIMEOUT,
    ping_interval=PING_INTERVAL,
    allow_credentials=True,
    transports=['polling', 'websocket'],
    always_connect=True,
    max_http_buffer_size=1e8,
    manage_session=True,
    websocket_ping_timeout=PING_TIMEOUT,
    websocket_ping_interval=PING_INTERVAL,
    upgrade_timeout=20000,
    cookie_path='/socket.io/',
    cookie_samesite='Strict',
    path='/socket.io/',
    cors_credentials=True,
    reconnection=True,
    reconnection_attempts=5,
    reconnection_delay=1000,
    reconnection_delay_max=5000,
    async_handlers=True
)

# Export app, socketio, and redis_client
__all__ = ['app', 'socketio', 'redis_client']
