from src.models.schema import Lineup

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
