from src.models.schema import Team, Fixture

def round_robin(team_ids):
    ids = list(team_ids)
    
    if len(ids) % 2 == 1:
        ids.append(None) # bye week
        
    n = len(ids)
    matches = n // 2
    rounds = n - 1
    
    schedule = []
    
    for _ in range(rounds):
        pairs = []
        
        for i in range(matches):
            a = ids[i]
            b = ids[n - 1 - i]
            if a is not None and b is not None:
                pairs.append((a,b))
                
        schedule.append(pairs)
            
        ids = [ids[0]] + [ids[-1]] + ids[1:-1]
            
    return schedule

def seed_pl_fixtures(db, league_id, season):
    teams = db.query(Team).filter_by(league_id = league_id).all()
    team_ids = []
    for t in teams:
        team_ids.append(t.id)
        
    deleted = db.query(Fixture).filter(
        Fixture.league_id == league_id,
        Fixture.season == season
    ).delete(synchronize_session=False)

    db.commit()
    
    first_half = round_robin(team_ids)
    
    second_half = []
    for matchday in first_half:
        match = []
        for home, away in matchday:
            match.append((away, home))
        second_half.append(match)
        
    full_schedule = first_half + second_half
    
    matchday_number = 1
    for matchday in full_schedule:
        for home_id, away_id in matchday:
            db.add(Fixture(
                season=season,
                league_id=league_id,
                matchday=matchday_number,
                home_team_id=home_id,
                away_team_id=away_id
            ))
        matchday_number += 1
        
    db.commit()