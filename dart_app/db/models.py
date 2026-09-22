from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    matches = relationship("MatchResult", back_populates="player")

class MatchResult(Base):
    __tablename__ = 'match_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    game_mode = Column(String(50), default="501")
    three_dart_avg = Column(Float, nullable=False)
    highest_turn_score = Column(Integer, default=0)
    won = Column(Integer, default=0)  # 1 for Win, 0 for Loss
    played_at = Column(DateTime, default=datetime.utcnow)
    
    player = relationship("Player", back_populates="matches")

def initialize_database(db_url: str = "sqlite:///dart_app.db"):
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
