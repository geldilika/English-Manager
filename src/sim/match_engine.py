import random

from sqlalchemy import desc
from src.models.schema import Player, Result, Lineup

def team_strength(db, season, team_id):
    players = get_starting_xi(db, season, team_id)
    if not players:
        return 50.0, 50.0

    atk_total = 0.0
    def_total = 0.0

    for p in players:
        atk_total += float(p.attack)
        def_total += float(p.defend)

    attack = atk_total / len(players)
    defend = def_total / len(players)
    return attack, defend

def goals_from_xg(xg):
    chances = max(1, int(xg * 6))
    p = min(0.50, xg / chances)

    goals = 0
    for _ in range(chances):
        if random.random() < p:
            goals += 1
    return goals

def simulate_fixture(db, season, fixture):
    existing = db.query(Result).filter_by(fixture_id=fixture.id).first()
    if existing:
        return existing
    
    home_atk, home_def = team_strength(db, season, fixture.home_team_id)
    away_atk, away_def = team_strength(db, season, fixture.away_team_id)
    
    home_xg = 1.25 + (home_atk - away_def) * 0.015 + random.gauss(0, 0.12)
    away_xg = 1.10 + (away_atk - home_def) * 0.015 + random.gauss(0, 0.12)
    
    if home_xg < 0.2:
        home_xg = 0.2
    if away_xg < 0.2:
        away_xg = 0.2
        
    home_goals = goals_from_xg(home_xg)
    away_goals = goals_from_xg(away_xg)

    home_shots = max(1, int(random.gauss(home_xg * 8, 2)))
    away_shots = max(1, int(random.gauss(away_xg * 8, 2)))
    
    result = Result(
        fixture_id=fixture.id,
        home_goals=home_goals,
        away_goals=away_goals,
        home_xg=float(home_xg),
        away_xg=float(away_xg),
        home_shots=home_shots,
        away_shots=away_shots
    )

    db.add(result)
    return result

def get_starting_xi(db, season, team_id):
    rows = (
        db.query(Lineup)
        .filter(Lineup.season == season)
        .filter(Lineup.team_id == team_id)
        .filter(Lineup.is_starting == True)
        .all()
    )
    
    players = []
    for r in rows:
        p = db.get(Player, r.player_id)
        if p is not None and p.team_id == team_id:
            players.append(p)
            
    if len(players) != 11:
        players = (
            db.query(Player)
            .filter(Player.team_id == team_id)
            .order_by(Player.overall,desc())
            .limit(11)
            .all()
        )
        
    return players