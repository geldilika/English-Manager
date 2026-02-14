import random
from operator import attrgetter

from sqlalchemy import desc
from src.models.schema import Player, Result, Lineup
from src.sim.tactics_engine import get_team_tactics, compute_mode, apply_style_matchup
from src.sim.injuries import remove_injured, maybe_injure_team

def team_strength(db, season, team_id):
    rows = (
        db.query(Lineup)
        .filter(Lineup.season == season)
        .filter(Lineup.team_id == team_id)
        .filter(Lineup.role == "START")
        .all()
    )
    
    players = []
    for r in rows:
        p = db.get(Player, r.player_id)
        if p and p.team_id == team_id:
            players.append(p)
            
    if not players:
        players = get_starting_xi(db, season, team_id)

    atk_total = 0.0
    def_total = 0.0

    for p in players:
        atk_total += float(p.attack)
        def_total += float(p.defend)

    attack = atk_total / float(len(players))
    defend = def_total / float(len(players))
    
    return attack, defend

def goals_from_xg(xg):
    chances = max(1, int(xg * 6))
    p = min(0.50, xg / chances)

    goals = 0
    for _ in range(chances):
        if random.random() < p:
            goals += 1
    return goals

def strength_from_players(players):
    if not players:
        return 50.0, 50.0

    atk_total = 0.0
    def_total = 0.0

    i = 0
    while i < len(players):
        p = players[i]
        atk_total += float(p.attack)
        def_total += float(p.defend)
        i += 1

    return atk_total / float(len(players)), def_total / float(len(players))

def get_lineup_players(db, season, team_id, role):
    rows = (
        db.query(Lineup)
        .filter(Lineup.season == season)
        .filter(Lineup.team_id == team_id)
        .filter(Lineup.role == role)
        .all()
    )

    players = []
    i = 0
    while i < len(rows):
        r = rows[i]
        p = db.get(Player, r.player_id)
        if p is not None and int(p.team_id) == int(team_id):
            players.append(p)
        i += 1

    return players

def fill_to_11(starters, bench):
    bench_sorted = []
    i = 0
    while i < len(bench):
        bench_sorted.append(bench[i])
        i += 1

    bench_sorted.sort(key=attrgetter("overall"), reverse=True)

    used = []
    i = 0
    while i < len(starters):
        used.append(starters[i])
        i += 1

    j = 0
    while len(used) < 11 and j < len(bench_sorted):
        used.append(bench_sorted[j])
        j += 1

    return used

def simulate_fixture(db, season, matchday, fixture, events=None):
    existing = db.query(Result).filter_by(fixture_id=fixture.id).first()
    if existing:
        return existing
    
    home_row = get_team_tactics(db, season, fixture.home_team_id)
    away_row = get_team_tactics(db, season, fixture.away_team_id)

    home_mode = compute_mode(home_row)
    away_mode = compute_mode(away_row)
    
    home_mode, away_mode = apply_style_matchup(home_mode, away_mode)
    
    home_start = get_lineup_players(db, season, fixture.home_team_id, "START")
    home_bench = get_lineup_players(db, season, fixture.home_team_id, "BENCH")
    away_start = get_lineup_players(db, season, fixture.away_team_id, "START")
    away_bench = get_lineup_players(db, season, fixture.away_team_id, "BENCH")
    
    home_start = remove_injured(db, season, fixture.home_team_id, home_start, matchday)
    home_bench = remove_injured(db, season, fixture.home_team_id, home_bench, matchday)
    away_start = remove_injured(db, season, fixture.away_team_id, away_start, matchday)
    away_bench = remove_injured(db, season, fixture.away_team_id, away_bench, matchday)
    
    home_used = fill_to_11(home_start, home_bench)
    away_used = fill_to_11(away_start, away_bench)
    
    inj_home = maybe_injure_team(
        db, season, fixture.home_team_id, home_used, matchday, intensity=float(home_mode["intensity"])
    )
    inj_away = maybe_injure_team(
        db, season, fixture.away_team_id, away_used, matchday, intensity=float(away_mode["intensity"])
    )
    
    if events is not None:
        if inj_home:
            events.append(f"[red]{inj_home[0]} injured ({inj_home[1]} GW)[/red]")
        if inj_away:
            events.append(f"[red]{inj_away[0]} injured ({inj_away[1]} GW)[/red]")
    
    home_atk, home_def = strength_from_players(home_used)
    away_atk, away_def = strength_from_players(away_used)
    
    home_atk *= float(home_mode["atk"])
    home_def *= float(home_mode["def"])
    away_atk *= float(away_mode["atk"])
    away_def *= float(away_mode["def"])
    
    home_xg = 1.25 + (home_atk - away_def) * 0.015 + random.gauss(0, 0.12)
    away_xg = 1.10 + (away_atk - home_def) * 0.015 + random.gauss(0, 0.12)

    home_xg = home_xg * (0.98 + 0.02 * float(home_mode["shots"]))
    away_xg = away_xg * (0.98 + 0.02 * float(away_mode["shots"]))
    
    if home_xg < 0.2:
        home_xg = 0.2
    if away_xg < 0.2:
        away_xg = 0.2
        
    home_goals = goals_from_xg(home_xg)
    away_goals = goals_from_xg(away_xg)

    home_shots = max(1, int(random.gauss(home_xg * 8 * float(home_mode["shots"]), 2)))
    away_shots = max(1, int(random.gauss(away_xg * 8 * float(away_mode["shots"]), 2)))
    
    result = Result(
        fixture_id=fixture.id,
        home_goals=home_goals,
        away_goals=away_goals,
        home_xg=float(home_xg),
        away_xg=float(away_xg),
        home_shots=home_shots,
        away_shots=away_shots
    )

    db.add(result)
    return result

def get_starting_xi(db, season, team_id):
    rows = (
        db.query(Lineup)
        .filter(Lineup.season == season)
        .filter(Lineup.team_id == team_id)
        .filter(Lineup.role == "START")
        .all()
    )
    
    players = []
    for r in rows:
        p = db.get(Player, r.player_id)
        if p is not None and p.team_id == team_id:
            players.append(p)
            
    if len(players) != 11:
        players = (
            db.query(Player)
            .filter(Player.team_id == team_id)
            .order_by(Player.overall.desc())
            .limit(11)
            .all()
        )
        
    return players