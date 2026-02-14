import random
from src.models.schema import PlayerCondition, Player

def get_condition(db, season, team_id, player_id):
    row = (
        db.query(PlayerCondition)
        .filter(PlayerCondition.season == season)
        .filter(PlayerCondition.team_id == team_id)
        .filter(PlayerCondition.player_id == player_id)
        .first()
    )
    if row:
        return row

    row = PlayerCondition(
        season=season,
        team_id=team_id,
        player_id=player_id,
        fatigue=0.0,
        injured_until=0
    )
    db.add(row)
    return row

def is_injured(db, season, team_id, player_id, matchday):
    condition = get_condition(db, season, team_id, player_id)
    return int(condition.injured_until) >= int(matchday)

def remove_injured(db, season, team_id, players, matchday):
    out = []
    i = 0
    
    while i < len(players):
        p = players[i]
        if not is_injured(db, season, team_id, p.id, matchday):
            out.append(p)
        i += 1
    return out

def maybe_injure_team(db, season, team_id, players_used, matchday, intensity=1.0):
    chance = 0.05 + (float(intensity) - 1.0) * 0.01
    if chance < 0.01:
        chance = 0.01
    if chance > 0.05:
        chance = 0.05
        
    if random.random() > chance:
        return None
    
    if not players_used:
        return None
    
    victim = random.choice(players_used)
    weeks = random.randint(1,3)
    
    condition = get_condition(db, season, team_id, victim.id)
    condition.injured_until = int(matchday) + int(weeks)
    
    return (victim.name, weeks)

def get_injury_list(db, season, team_id, matchday):
    rows = (
        db.query(PlayerCondition)
        .filter(PlayerCondition.season == season)
        .filter(PlayerCondition.team_id == team_id)
        .filter(PlayerCondition.injured_until >= matchday)
        .all()
    )
    
    out = []
    i = 0
    while i < len(rows):
        c = rows[i]
        p = db.get(Player, c.player_id)
        if p:
            out.append((p, c))
        i += 1
        
    return out