from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import sys
from pathlib import Path
import asyncio
from typing import Dict, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

# Import Flask app after FastAPI app is created
from app import app as flask_app

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

async def forward_request_to_flask(request: Request, path: str) -> Response:
    """
    Forward HTTP request to Flask app and return response
    """
    try:
        # Get request data
        method = request.method
        headers = dict(request.headers)
        query_params = str(request.query_params)
        
        # Get body for POST requests
        body = b""
        if method == "POST":
            body = await request.body()
            
        # Create test client for Flask app
        with flask_app.test_client() as client:
            # Forward request to Flask
            response = client.open(
                f"/api/{path}",
                method=method,
                headers=headers,
                query_string=query_params,
                data=body
            )
            
            # Convert Flask response to FastAPI response
            try:
                # Try to parse JSON response
                content = response.get_json()
                return JSONResponse(
                    content=content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            except Exception:
                # If not JSON, return raw response
                return Response(
                    content=response.get_data(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            
    except Exception as e:
        logger.error(f"Error forwarding request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@app.api_route("/api/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def catch_all(request: Request, path: str):
    """
    Catch-all route that forwards all requests to the Flask app
    """
    return await forward_request_to_flask(request, path)

@app.websocket("/socket.io/{path:path}")
async def websocket_endpoint(websocket: WebSocket, path: str):
    """
    WebSocket endpoint that handles game state updates
    """
    try:
        await websocket.accept()
        client_id = str(id(websocket))
        active_connections[client_id] = websocket
        
        # Send initial game state if available
        try:
            # Get latest game state from Redis
            from app import get_game_state_from_redis
            game_state = get_game_state_from_redis("current")  # Default game ID
            if game_state and isinstance(game_state, dict):
                await websocket.send_json({
                    "type": "gameUpdate",
                    "data": game_state
                })
        except Exception as e:
            logger.error(f"Error sending initial game state: {str(e)}")
            
        # Listen for messages
        while True:
            try:
                message = await websocket.receive_json()
                
                # Handle different message types
                if message.get("type") == "move":
                    try:
                        # Forward move to Flask app using test client
                        with flask_app.test_client() as client:
                            move_data = message.get("data", {})
                            response = client.post(
                                "/api/game/move",
                                json=move_data
                            )
                            if response.status_code == 200:
                                # Broadcast successful move to all clients
                                # Get latest game state from Redis
                                game_state = get_game_state_from_redis("current")  # Default game ID
                                if game_state and isinstance(game_state, dict):
                                    for conn in active_connections.values():
                                        try:
                                            await conn.send_json({
                                                "type": "gameUpdate",
                                                "data": game_state
                                            })
                                        except Exception as e:
                                            logger.error(f"Error broadcasting to client: {str(e)}")
                            else:
                                # Send error back to client
                                await websocket.send_json({
                                    "type": "error",
                                    "data": response.get_json()
                                })
                    except Exception as e:
                        logger.error(f"Error processing move: {str(e)}")
                        await websocket.send_json({
                            "type": "error",
                            "data": {"error": "Failed to process move"}
                        })
                        
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        
    finally:
        # Clean up connection
        if client_id in active_connections:
            del active_connections[client_id]
