from src.models.schema import TeamTactics
from src.sim.tactics import (
    TACTIC_BASE,
    TACTIC_PRESETS,
    LINE_HEIGHT,
    DIRECTNESS,
    STYLE_MATCHUPS,
)

def get_team_tactics(db, season, team_id):
    row = (
        db.query(TeamTactics)
        .filter(TeamTactics.season == season)
        .filter(TeamTactics.team_id == team_id)
        .first()
    )
    if row:
        return row
    
    row = TeamTactics(season=season, team_id=team_id)
    
    db.add(row)
    db.commit()
    
    return row

def compute_mode(row):
    tactic = row.tactic or "Balanced"
    pressing = row.pressing or "Normal"
    tempo = row.tempo or "Normal"
    width = row.width or "Balanced"
    line_height = row.line_height or "Normal"
    directness = row.directness or "Mixed"
    
    base = TACTIC_BASE.get(tactic, TACTIC_BASE["Balanced"])
    p = TACTIC_PRESETS["pressing"].get(pressing, TACTIC_PRESETS["pressing"]["Normal"])
    t = TACTIC_PRESETS["tempo"].get(tempo, TACTIC_PRESETS["tempo"]["Normal"])
    w = TACTIC_PRESETS["width"].get(width, TACTIC_PRESETS["width"]["Balanced"])
    lh = LINE_HEIGHT.get(line_height, LINE_HEIGHT["Normal"])
    d = DIRECTNESS.get(directness, DIRECTNESS["Mixed"])
    
    atk = float(base["atk"]) * float(p["atk"]) * float(t["atk"]) * float(w["atk"]) * float(lh["atk"]) * float(d["atk"])
    dfn = float(base["def"]) * float(p["def"]) * float(t["def"]) * float(w["def"]) * float(lh["def"])
    shots = float(t.get("shots", 1.0)) * float(d.get("shots", 1.0))
    intensity = float(p["intensity"]) * float(t["intensity"])
    opp_atk = float(lh.get("opp_atk", 1.0))
    
    return {
        "tactic": tactic,
        "pressing": pressing,
        "tempo": tempo,
        "width": width,
        "line_height": line_height,
        "directness": directness,
        "atk": atk,
        "def": dfn,
        "shots": shots,
        "intensity": intensity,
        "opp_atk": opp_atk,
    }
    
def apply_style_matchup(home_mods, away_mods):
    key = (home_mods["pressing"], away_mods["tempo"])
    eff = STYLE_MATCHUPS.get(key)
    if eff:
        if "opp_atk" in eff:
            away_mods["atk"] = float(away_mods["atk"]) * float(eff["opp_atk"])
        if "opp_def" in eff:
            away_mods["def"] = float(away_mods["def"]) * float(eff["opp_def"])

    key2 = (away_mods["pressing"], home_mods["tempo"])
    eff2 = STYLE_MATCHUPS.get(key2)
    if eff2:
        if "opp_atk" in eff2:
            home_mods["atk"] = float(home_mods["atk"]) * float(eff2["opp_atk"])
        if "opp_def" in eff2:
            home_mods["def"] = float(home_mods["def"]) * float(eff2["opp_def"])
            
    away_mods["atk"] = float(away_mods["atk"]) * float(home_mods.get("opp_atk", 1.0))
    home_mods["atk"] = float(home_mods["atk"]) * float(away_mods.get("opp_atk", 1.0))
    
    return home_mods, away_mods