import pandas as pd
import requests
from io import StringIO
import numpy as np

from src.db import premier_league
from src.models.schema import Team, Player

RAW_BASE = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master"

def read_csv(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text))

def position_code(x):
    try:
        x = int(x)
    except:
        x = 3

    if x == 1:
        return "GK"
    if x == 2:
        return "DEF"
    if x == 3:
        return "MID"
    if x == 4:
        return "FWD"
    return "MID"

def normalize(values):
    s = pd.to_numeric(values, errors="coerce").fillna(0.0)
    
    low = float(s.min())
    high = float(s.max())
    
    if high - low < 1e-9:
        return s * 0 + 50
    
    return 100.0 * (s - low) / (high - low)
    
def clip_rating(x):
    return float(np.clip(x, 0.0, 100.0))

def import_pl_from_fpl(db, season):
    league = premier_league(db)
    teams_url = RAW_BASE + "/data/" + season + "/teams.csv"
    players_url = RAW_BASE + "/data/" + season + "/players_raw.csv"
    
    teams_df = read_csv(teams_url)
    players_df = read_csv(players_url)
    
    teams = {}
    for _, row in teams_df.iterrows():
        fpl_team_id = int(row["id"])
        team_name = str(row["name"]).strip()
        team = db.query(Team).filter_by(fpl_team_id=fpl_team_id).first()
        if not team:
            if "strength" in teams_df.columns:
                strength = float(row.get("strength", 3))
                reputation = float(np.clip(55 + strength *8, 35, 95))
            else:
                reputation = 70.0

            team = Team(
                name=team_name,
                league_id=league.id,
                fpl_team_id=fpl_team_id,
                budget=25_000_000,
                reputation=reputation,
            )
            db.add(team)
            db.commit()
            
        teams[fpl_team_id] = team
        
    team_ids = []
    for team in teams.values():
        team_ids.append(team.id)
    db.query(Player).filter(Player.team_id.in_(team_ids)).delete(synchronize_session=False)
    db.commit()

    minutes_n = normalize(players_df.get("minutes", 0))
    points_n = normalize(players_df.get("total_points", 0))
    
    influence_n = normalize(players_df.get("influence", 0))
    creativity_n = normalize(players_df.get("creativity", 0))
    threat_n = normalize(players_df.get("threat", 0))
    ict_n = normalize(players_df.get("ict_index", 0))
    
    clean_sheets_n = normalize(players_df.get("clean_sheets", 0))
    goals_conceded_n = normalize(players_df.get("goals_conceded", 0))
    saves_n = normalize(players_df.get("saves", 0))
    
    overall_score = (0.35 * influence_n) + (0.35 * ict_n) + (0.30 * points_n)
    attack_score = (0.45 * threat_n) + (0.35 * creativity_n) + (0.30 * points_n)
    defend_score = (0.55 * clean_sheets_n) + (0.35 * saves_n) + (0.20 * (100.0 - goals_conceded_n))
    stamina_score = minutes_n
    
    for i, row in players_df.iterrows():
        fpl_team_id = int(row["team"])
        team = teams.get(fpl_team_id)
        if not team:
            continue
        
        first = str(row.get("first_name", "")).strip()
        second = str(row.get("second_name", "")).strip()
        web = str(row.get("web_name", "")).strip()
        
        name = (first + " " + second).strip() 
        if (first or second):
            name = (first + " " + second).strip()
        else:
            if web:
                name = web
            else:
                "Unkown"
        
        pos = position_code(row.get("element_type", 3))
        
        overall = clip_rating(float(overall_score.iloc[i]))
        attack  = clip_rating(float(attack_score.iloc[i]))
        defend  = clip_rating(float(defend_score.iloc[i]))
        stamina = clip_rating(float(stamina_score.iloc[i]))

        fpl_player_id = None
        if "id" in players_df.columns:
            try:
                fpl_player_id = int(row.get("id", 0))
            except:
                fpl_player_id = None
        
        try:
            minutes = int(row.get("minutes", 0))
        except:
            minutes = 0
        try:
            total_points = int(row.get("total_points", 0))
        except:
            total_points = 0
        try:
            now_cost = int(row.get("now_cost", 0))
        except:
            now_cost = 0
            
        db.add(Player(
            name=name,
            pos=pos,
            age=24,
            team_id=team.id,

            fpl_player_id=fpl_player_id,

            overall=overall,
            attack=attack,
            defend=defend,
            stamina=stamina,

            minutes=minutes,
            total_points=total_points,
            now_cost=now_cost,
        ))
        
    db.commit()



