from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add parent directory to Python path to import Flask app
sys.path.append(str(Path(__file__).parent.parent))
from app import app as flask_app

# Create FastAPI app
app = FastAPI(title="Chess AI Game")

# Configure CORS to match Flask app settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://*.devinapps.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create wrapper route to forward requests to Flask app
@app.api_route("/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def catch_all(request: Request, path: str):
    """
    Catch-all route that forwards all requests to the Flask app
    """
    # Forward the request to Flask app
    # Note: This is a placeholder until we get FastAPI dependencies
    # and implement the actual request forwarding logic
    return {"message": "Flask app wrapper - implementation pending"}

# WebSocket endpoint placeholder
# Note: Will be implemented once we have the required dependencies
@app.websocket("/{path:path}")
async def websocket_endpoint(websocket: str, path: str):
    """
    WebSocket endpoint that forwards socket connections to Flask-SocketIO
    """
    pass  # Implementation pending FastAPI WebSocket dependencies
