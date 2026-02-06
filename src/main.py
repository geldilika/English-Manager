import argparse

from src.db import init_db, SessionLocal, premier_league
from src.data.import_fpl import import_pl_from_fpl
from src.sim.fixtures import seed_pl_fixtures
from src.ui.menu import run_menu, pick_team, find_team

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", default="2024-25")
    parser.add_argument("--team", default=None, help='Team name e.g. "Chelsea"')
    args = parser.parse_args()

    season = args.season

    init_db()
    db = SessionLocal()

    import_pl_from_fpl(db, season)
    league = premier_league(db)
    seed_pl_fixtures(db, league.id, season)

    if args.team:
        managed = find_team(db, league.id, args.team)
        if managed is None:
            print("Team not found:", args.team)
            managed = pick_team(db, league.id)
    else:
        managed = pick_team(db, league.id)

    run_menu(db, league, season, managed)
    db.close()

if __name__ == "__main__":
    run()
