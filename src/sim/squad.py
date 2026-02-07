from operator import attrgetter
from src.models.schema import Lineup, Player

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