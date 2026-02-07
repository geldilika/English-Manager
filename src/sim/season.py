from src.models.schema import Fixture
from src.sim.match_engine import simulate_fixture

def simulate_matchday(db, league_id, season, matchday):
    fixtures = db.query(Fixture).filter_by(
        league_id=league_id,
        season=season,
        matchday=matchday
    ).all()
    
    for f in fixtures:
        simulate_fixture(db, season, f)

    db.commit()