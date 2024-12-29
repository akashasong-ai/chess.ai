# models.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
import datetime
from pydantic import BaseModel, ConfigDict

Base = declarative_base()

class MyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class LLM(Base):
    __tablename__ = 'llms'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    api_endpoint = Column(String, nullable=False)
    description = Column(String, nullable=True)
    rating = Column(Float, default=1500.0)

    # Relationships
    games_as_white = relationship("Game", back_populates="white_llm", foreign_keys='Game.llm1_id')
    games_as_black = relationship("Game", back_populates="black_llm", foreign_keys='Game.llm2_id')

class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, index=True)
    llm1_id = Column(Integer, ForeignKey('llms.id'), nullable=False)  # White player
    llm2_id = Column(Integer, ForeignKey('llms.id'), nullable=False)  # Black player
    fen = Column(Text, nullable=False, default='startpos')  # Starting FEN
    pgn = Column(Text, nullable=True)
    result = Column(String, nullable=True)  # "1-0", "0-1", "1/2-1/2", or None
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    white_llm = relationship("LLM", foreign_keys=[llm1_id], back_populates="games_as_white")
    black_llm = relationship("LLM", foreign_keys=[llm2_id], back_populates="games_as_black")
