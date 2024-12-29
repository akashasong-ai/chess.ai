from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import chess

# Base schema for LLM
class LLMBase(BaseModel):
    name: str
    api_endpoint: str
    description: Optional[str] = None
    rating: float = 1500.0

# Schema for creating an LLM
class LLMCreate(LLMBase):
    pass

# Schema for reading an LLM
class LLMRead(LLMBase):
    id: int

    class Config:
        orm_mode = True  # Ensure compatibility with SQLAlchemy models

# Base schema for Game
class GameBase(BaseModel):
    llm1_id: int
    llm2_id: int
    fen: Optional[str] = chess.STARTING_FEN  # Defaults to the starting FEN position
    pgn: Optional[str] = None
    result: Optional[str] = None  # "1-0", "0-1", "1/2-1/2", or None
    timestamp: Optional[datetime] = None

# Schema for creating a Game
class GameCreate(BaseModel):
    llm1_id: int
    llm2_id: int
    fen: Optional[str] = "startpos"  # Defaults to "startpos" for initial position

# Schema for reading a Game
class GameRead(GameBase):
    id: int

    class Config:
        orm_mode = True  # Ensure compatibility with SQLAlchemy models

# Schema for Moves
class Move(BaseModel):
    move: str = "e2e4"  # Default move in UCI format

    class Config:
        orm_mode = True  # Ensure compatibility with SQLAlchemy models

# Optional additional configurations
class MyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
