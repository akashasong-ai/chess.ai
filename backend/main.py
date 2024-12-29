# main.py

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, LLM, Game  # Import Base from models.py
from schemas import LLMCreate, LLMRead, GameCreate, GameRead, Move
import crud
import chess
import chess.pgn
import datetime
from typing import List
from dotenv import load_dotenv
import os
from databases import Database  # Import Database if using 'databases' library
from .gemini_adapter import GeminiAdapter
from openai_adapter import OpenAIAdapter
from llm_interface import LLMInterface
from backend.models import Base, LLM, Game  # Import Base from backend.models
from backend.gemini_adapter import GeminiAdapter

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Load LLMs
LLM_PROVIDERS = {
    "gemini": GeminiAdapter(api_key="your_gemini_api_key", base_url="https://gemini.api"),
    "openai": OpenAIAdapter(api_key="your_openai_api_key")
}

# Retrieve the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g., "sqlite+aiosqlite:///./chess.db"
if not DATABASE_URL:
    print("Warning: DATABASE_URL is not set. Defaulting to an in-memory SQLite database for testing.")
    DATABASE_URL = "sqlite:///test.db"  # Use an in-memory SQLite database for tests.

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the Database instance (if using 'databases' library)
database = Database(DATABASE_URL)

# Create the SQLAlchemy engine
# If using 'databases' with SQLAlchemy, ensure compatibility
engine = create_engine(
    DATABASE_URL.replace("sqlite+aiosqlite", "sqlite"),
    connect_args={"check_same_thread": False}  # For SQLite
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the database (if they don't exist)
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI(title="Chess LLM Backend")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility method to convert model instances to dictionaries
def model_to_dict(model_instance):
    return {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}

# Add the to_dict method to LLM and Game models
LLM.to_dict = model_to_dict
Game.to_dict = model_to_dict

# Startup and shutdown events for the Database connection
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    yield
    # Shutdown code here

app = FastAPI(lifespan=lifespan)

# Define routes below


# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Chess LLM Backend"}

# CRUD Endpoints for LLMs

@app.post("/get-move/")
async def get_move(provider: str, game_state: str):
    llm: LLMInterface = LLM_PROVIDERS.get(provider)
    if not llm:
        raise HTTPException(status_code=400, detail="Invalid LLM provider")

    move = await llm.generate_move(game_state)
    return {"move": move}

@app.post("/llms/", response_model=LLMRead)
async def create_llm_endpoint(llm: LLMCreate, db: Session = Depends(get_db)):
    return model_to_dict(crud.create_llm(db, llm))

@app.get("/llms/", response_model=List[LLMRead])
async def read_llms_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    llms = crud.get_llms(db, skip=skip, limit=limit)
    return [model_to_dict(llm) for llm in llms]

@app.get("/llms/{llm_id}", response_model=LLMRead)
async def read_llm_endpoint(llm_id: int, db: Session = Depends(get_db)):
    llm = crud.get_llm(db, llm_id)
    if llm is None:
        raise HTTPException(status_code=404, detail="LLM not found")
    return model_to_dict(llm)

@app.put("/llms/{llm_id}", response_model=LLMRead)
async def update_llm_endpoint(llm_id: int, updated_llm: LLMCreate, db: Session = Depends(get_db)):
    llm = crud.get_llm(db, llm_id)
    if llm is None:
        raise HTTPException(status_code=404, detail="LLM not found")
    llm.name = updated_llm.name
    llm.api_endpoint = updated_llm.api_endpoint
    llm.description = updated_llm.description
    llm.rating = updated_llm.rating
    db.commit()
    db.refresh(llm)
    return model_to_dict(llm)

@app.delete("/llms/{llm_id}", response_model=dict)
async def delete_llm_endpoint(llm_id: int, db: Session = Depends(get_db)):
    success = crud.delete_llm(db, llm_id)
    if not success:
        raise HTTPException(status_code=404, detail="LLM not found")
    return {"detail": "LLM deleted successfully"}

# CRUD Endpoints for Games

@app.post("/games/", response_model=GameRead)
async def create_game_endpoint(game: GameCreate, db: Session = Depends(get_db)):
    return model_to_dict(crud.create_game(db, game))

@app.get("/games/", response_model=List[GameRead])
async def read_games_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    games = crud.get_games(db, skip=skip, limit=limit)
    return [model_to_dict(game) for game in games]

@app.get("/games/{game_id}", response_model=GameRead)
async def read_game_endpoint(game_id: int, db: Session = Depends(get_db)):
    game = crud.get_game(db, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return model_to_dict(game)

@app.put("/games/{game_id}", response_model=GameRead)
async def update_game_endpoint(game_id: int, updated_game: GameCreate, db: Session = Depends(get_db)):
    game = crud.get_game(db, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    game.llm1_id = updated_game.llm1_id
    game.llm2_id = updated_game.llm2_id
    db.commit()
    db.refresh(game)
    return model_to_dict(game)

@app.delete("/games/{game_id}", response_model=dict)
async def delete_game_endpoint(game_id: int, db: Session = Depends(get_db)):
    success = crud.delete_game(db, game_id)
    if not success:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"detail": "Game deleted successfully"}

# Endpoint to make a move
@app.post("/games/{game_id}/move/", response_model=GameRead)
async def make_game_move(game_id: int, move: Move, db: Session = Depends(get_db)):
    """
    Applies a move to an ongoing game.
    
    Args:
        game_id (int): The ID of the game.
        move (Move): The move in UCI format.
    
    Returns:
        GameRead: The updated game details.
    """
    try:
        game = crud.get_game(db, game_id)
        if game is None:
            raise HTTPException(status_code=404, detail="Game not found.")

        if game.result is not None:
            raise HTTPException(status_code=400, detail="Game has already concluded.")

        # Apply the move using the utility function
        make_move(game, move.move)

        db.commit()
        db.refresh(game)
        return model_to_dict(game)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Utility function to apply a move
def make_move(game: Game, move_uci: str) -> None:
    """
    Applies a move to the game using UCI format.
    
    Args:
        game (Game): The game instance to update.
        move_uci (str): The move in UCI format (e.g., 'e2e4').
    
    Raises:
        HTTPException: If the move format is invalid or the move is illegal.
    """
    board = chess.Board(game.fen)
    try:
        move = board.parse_uci(move_uci)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid move format. Use UCI format like 'e2e4'."
        )

    if move not in board.legal_moves:
        raise HTTPException(
            status_code=400,
            detail="Illegal move."
        )

    board.push(move)

    # Update FEN
    game.fen = board.fen()

    # Update PGN
    pgn_game = chess.pgn.Game.from_board(board)
    exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
    game.pgn = pgn_game.accept(exporter)

    # Check for game termination
    if board.is_game_over():
        game.result = board.result()
    else:
        game.result = None  # Game is ongoing
