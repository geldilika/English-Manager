from src.models.schema import Fixture
from src.sim.match_engine import simulate_fixture

def simulate_matchday(db, league_id, season, matchday):
    fixtures = (
        db.query(Fixture)
        .filter(Fixture.league_id == league_id)
        .filter(Fixture.season == season)
        .filter(Fixture.matchday == matchday)
        .all()
    )

    events = []

    i = 0
    while i < len(fixtures):
        simulate_fixture(db, season, matchday, fixtures[i], events)
        i += 1

    db.commit()
    return events