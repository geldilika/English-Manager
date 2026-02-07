from operator import attrgetter
from src.models.schema import Lineup, Player, TeamTactics

Formations = {
    "3-5-2": {"GK": 1, "DEF": 3, "MID": 5, "FWD": 2},
    "3-4-3": {"GK": 1, "DEF": 3, "MID": 4, "FWD": 3},
    "3-1-4-2": {"GK": 1, "DEF": 3, "MID": 5, "FWD": 2},
    "3-4-1-2": {"GK": 1, "DEF": 3, "MID": 5, "FWD": 2},
    "3-3-3-1": {"GK": 1, "DEF": 3, "MID": 6, "FWD": 1},
    "3-2-4-1": {"GK": 1, "DEF": 3, "MID": 6, "FWD": 1},
    "3-6-1": {"GK": 1, "DEF": 3, "MID": 6, "FWD": 1},
    
    "4-4-2": {"GK": 1, "DEF": 4, "MID": 4, "FWD": 2},
    "4-3-3": {"GK": 1, "DEF": 4, "MID": 3, "FWD": 3},
    "4-2-3-1": {"GK": 1, "DEF": 4, "MID": 5, "FWD": 1},
    "4-1-4-1": {"GK": 1, "DEF": 4, "MID": 5, "FWD": 1},
    "4-3-1-2": {"GK": 1, "DEF": 4, "MID": 4, "FWD": 2},
    "4-2-2-2": {"GK": 1, "DEF": 4, "MID": 4, "FWD": 2},
    "4-5-1": {"GK": 1, "DEF": 4, "MID": 5, "FWD": 1},
    "4-1-2-1-2": {"GK": 1, "DEF": 4, "MID": 4, "FWD": 2},
    "4-2-4": {"GK": 1, "DEF": 4, "MID": 2, "FWD": 4},
    "4-3-2-1": {"GK": 1, "DEF": 4, "MID": 5, "FWD": 1},
    "4-6-0": {"GK": 1, "DEF": 4, "MID": 6, "FWD": 0},
    
    "5-3-2": {"GK": 1, "DEF": 5, "MID": 3, "FWD": 2},
    "5-4-1": {"GK": 1, "DEF": 5, "MID": 4, "FWD": 1},
    "5-2-3": {"GK": 1, "DEF": 5, "MID": 2, "FWD": 3},
    "5-3-1-1": {"GK": 1, "DEF": 5, "MID": 4, "FWD": 1},
    "5-4-1-0": {"GK": 1, "DEF": 5, "MID": 5, "FWD": 0}
}

def set_starting_xi(db, season, team_id, player_ids):
    if len(player_ids) != 11:
        return False, "You must select exactly 11 players"
    
    db.query(Lineup).filter(
        Lineup.season == season,
        Lineup.team_id == team_id
    ). delete()
    
    for pid in player_ids:
        db.add(Lineup(
            season = season,
            team_id = team_id,
            player_id = pid,
            is_starting = True
        ))
        
    db.commit()
    return True, "Starting XI saved"

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
        if p and p.team_id == team_id:
            players.append(p)
            
    players.sort(key=attrgetter("overall"), reverse = True)
    return players

def get_team_formation(db, season, team_id):
    row = (
        db.query(TeamTactics)
        .filter(TeamTactics.season == season)
        .filter(TeamTactics.team_id == team_id)
        .first()
    )
    if row:
        return row.formation
    return "4-3-3"

def set_team_formation(db, season, team_id, formation):
    if formation not in Formations:
        return False, "Invalid formation"
    
    row = (
        db.query(TeamTactics)
        .filter(TeamTactics.season == season)
        .filter(TeamTactics.team_id == team_id)
        .first()
    )
    
    if row:
        row.formation = formation
    else:
        db.add(TeamTactics(season = season, team_id=team_id, formation=formation))
        
    db.commit()
    return True, f"Formation set to {formation}"