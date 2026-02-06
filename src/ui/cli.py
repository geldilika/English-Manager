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

def league_table(db, league_id, season, up_to_matchday=None):
    teams = db.query(Team).filter_by(league_id=league_id).all()
    name = {}
    for t in teams:
        name[t.id] = t.name
        
    stats = {}
    for t in teams:
        stats[t.id] = {
            "P": 0,
            "W": 0,
            "D": 0,
            "L": 0,
            "GF": 0,
            "GA": 0,
            "Pts": 0
        }
        
    query = (
        db.query(Result, Fixture)
        .join(Fixture, Result.fixture_id == Fixture.id)
        .filter(
            Fixture.league_id == league_id,
            Fixture.season == season
        )
    )
    
    if up_to_matchday is not None:
        query = query.filter(Fixture.matchday <= up_to_matchday)
    
    rows = query.all()

    for result, fixture in rows:
        home = fixture.home_team_id
        away = fixture.away_team_id

        stats[home]["P"] += 1
        stats[away]["P"] += 1

        stats[home]["GF"] += result.home_goals
        stats[home]["GA"] += result.away_goals
        stats[away]["GF"] += result.away_goals
        stats[away]["GA"] += result.home_goals
        
        if result.home_goals > result.away_goals:
            stats[home]["W"] += 1
            stats[home]["Pts"] += 3
            stats[away]["L"] += 1
        elif result.home_goals < result.away_goals:
            stats[away]["W"] += 1
            stats[away]["Pts"] += 3
            stats[home]["L"] += 1
        else:
            stats[home]["D"] += 1
            stats[away]["D"] += 1
            stats[home]["Pts"] += 1
            stats[away]["Pts"] += 1
            
    order = []
    for team_id in stats:
        s = stats[team_id]
        goal_diff = s["GF"] - s["GA"]
        order.append((s["Pts"], goal_diff, s["GF"], team_id))

    order.sort(reverse=True)
    
    table = Table(title="Premier League Table")
    table.add_column("Pos", justify="right")
    table.add_column("Team")
    table.add_column("P", justify="right")
    table.add_column("W", justify="right")
    table.add_column("D", justify="right")
    table.add_column("L", justify="right")
    table.add_column("GF", justify="right")
    table.add_column("GA", justify="right")
    table.add_column("Pts", justify="right")
    
    pos = 1
    
    for _, _, _, team_id in order:
        s = stats[team_id]
        table.add_row(
            str(pos),
            name[team_id],
            str(s["P"]),
            str(s["W"]),
            str(s["D"]),
            str(s["L"]),
            str(s["GF"]),
            str(s["GA"]),
            str(s["Pts"])
        )
        pos += 1

    console.print(table)