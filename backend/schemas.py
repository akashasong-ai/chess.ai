# schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import chess

class LLMBase(BaseModel):
    name: str
    api_endpoint: str
    description: Optional[str] = None
    rating: float = 1500.0

class LLMCreate(LLMBase):
    pass

class LLMRead(LLMBase):
    id: int

    class Config:
        from_attributes = True  # Updated from orm_mode

class GameBase(BaseModel):
    llm1_id: int
    llm2_id: int
    fen: Optional[str] = chess.STARTING_FEN
    pgn: Optional[str] = None
    result: Optional[str] = None  # "1-0", "0-1", "1/2-1/2", or None
    timestamp: Optional[datetime] = None

class GameCreate(BaseModel):
    llm1_id: int
    llm2_id: int

class GameRead(GameBase):
    id: int

    class Config:
        from_attributes = True  # Updated from orm_mode

class Move(BaseModel):
    move: str = "e2e4"

    class Config:
        from_attributes = True  # Updated from orm_mode

class MyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)