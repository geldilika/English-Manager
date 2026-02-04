from src.db import init_db, SessionLocal, premier_league
from src.data.import_fpl import import_pl_from_fpl
from src.sim.fixtures import seed_pl_fixtures
from src.sim.match_engine import simulate_fixture
from src.models.schema import Fixture
from src.ui.cli import print_matchday, league_table

def run():
    season = "2024-25"

    init_db()
    db = SessionLocal()

    import_pl_from_fpl(db, season)

    league = premier_league(db)
    seed_pl_fixtures(db, league.id, season)

    for md in range(1, 6):
        fixtures = db.query(Fixture).filter_by(
            league_id=league.id,
            season=season,
            matchday=md
        ).all()

        for f in fixtures:
            simulate_fixture(db, f)

        db.commit()
        print_matchday(db, league.id, season, md)

    league_table(db, league.id, season)

    db.close()

if __name__ == "__main__":
    run()
