# crud.py

from sqlalchemy.orm import Session
from models import LLM, Game
from schemas import LLMCreate, GameCreate
import datetime

# CRUD Operations for LLM

def get_llm(db: Session, llm_id: int):
    return db.query(LLM).filter(LLM.id == llm_id).first()

def get_llms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(LLM).offset(skip).limit(limit).all()

def create_llm(db: Session, llm: LLMCreate):
    db_llm = LLM(
        name=llm.name,
        api_endpoint=llm.api_endpoint,
        description=llm.description,
        rating=llm.rating
    )
    db.add(db_llm)
    db.commit()
    db.refresh(db_llm)
    return db_llm

def delete_llm(db: Session, llm_id: int):
    llm = get_llm(db, llm_id)
    if llm:
        db.delete(llm)
        db.commit()
        return True
    return False

# CRUD Operations for Game

def get_game(db: Session, game_id: int):
    return db.query(Game).filter(Game.id == game_id).first()

def get_games(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Game).offset(skip).limit(limit).all()

def create_game(db: Session, game: GameCreate):
    db_game = Game(
        llm1_id=game.llm1_id,
        llm2_id=game.llm2_id,
        fen='startpos',
        pgn='',
        result=None,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

def delete_game(db: Session, game_id: int):
    game = get_game(db, game_id)
    if game:
        db.delete(game)
        db.commit()
        return True
    return False
