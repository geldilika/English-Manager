from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.schema import Base, League

DB_PATH = Path("data/game.db")

def get_engine():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{DB_PATH}", future=True)

SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    
def premier_league(db):
    league = db.query(League).filter_by(name="Premier League").first()
    if not league:
        league = League(name = "Premier League", tier=1)
        db.add(league)
        db.commit()
    return league