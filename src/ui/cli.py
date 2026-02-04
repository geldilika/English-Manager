from collections import defaultdict
from rich.console import Console
from rich.table import Table

from src.models.schema import Team, Fixture, Result

console = Console()

def print_matchday(db, league_id, season, matchday):
    teams = db.query(Team).filter_by(league_id=league_id).all()
    name = {}
    for t in teams:
        name[t.id] = t.name

    fixtures = db.query(Fixture).filter_by(
        league_id=league_id,
        season=season,
        matchday=matchday
    ).all()

    table = Table(title="Matchday " + str(matchday))
    table.add_column("Home")
    table.add_column("Score", justify="center")
    table.add_column("Away")

    for f in fixtures:
        r = db.query(Result).filter_by(fixture_id=f.id).first()
        score = "vs"
        if r:
            score = str(r.home_goals) + "-" + str(r.away_goals)
        table.add_row(name[f.home_team_id], score, name[f.away_team_id])

    console.print(table)
