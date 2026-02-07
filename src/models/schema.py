from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

Base = declarative_base()

class League(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    tier = Column(Integer, nullable=False)

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)

    fpl_team_id = Column(Integer, unique=True, nullable=True)

    budget = Column(Integer, default=25_000_000)
    reputation = Column(Float, default=70.0) 

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    pos = Column(String, nullable=False)
    age = Column(Integer, nullable=False, default=24)

    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    fpl_player_id = Column(Integer, unique=True, nullable=True)

    # Game attributes (0-100)
    overall = Column(Float, nullable=False)
    attack  = Column(Float, nullable=False)
    defend  = Column(Float, nullable=False)
    stamina = Column(Float, nullable=False)

    minutes = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    now_cost = Column(Integer, default=0)
    
    value = Column(Integer, nullable=False, default=0)

class Fixture(Base):
    __tablename__ = "fixtures"
    id = Column(Integer, primary_key=True)
    season = Column(String, nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    matchday = Column(Integer, nullable=False)

    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), unique=True, nullable=False)

    home_goals = Column(Integer, nullable=False)
    away_goals = Column(Integer, nullable=False)

    home_xg = Column(Float, nullable=False)
    away_xg = Column(Float, nullable=False)

    home_shots = Column(Integer, nullable=False)
    away_shots = Column(Integer, nullable=False)
    
class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True)
    
    season = Column(String, nullable=False)
    matchday = Column(Integer, nullable = False)
    
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    from_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    to_team_id = Column(Integer, ForeignKey("teams.id"), nullable = False)
    
    fee = Column(Integer, nullable = False)
    
class Shortlist(Base):
    __tablename__ = "shortlist"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("team_id", "player_id", name="uq_shortlist_team_player"),
    )
    
class TransferList(Base):
    __tablename__ = "transfer_list"

    id = Column(Integer, primary_key=True)
    season = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False) 
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    asking_price = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("season", "player_id", name="uq_transfer_list_season_player"),
    )
    
class TransferBid(Base):
        __tablename__ = "transfer_bids"

        id = Column(Integer, primary_key=True)
        season = Column(String, nullable=False)
        matchday = Column(Integer, nullable=False)

        player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
        from_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
        to_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

        fee = Column(Integer, nullable=False)
        status = Column(String, nullable=False, default="PENDING")
        created_at = Column(DateTime, server_default=func.now(), nullable=False)