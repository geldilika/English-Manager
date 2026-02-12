TACTIC_BASE = {
    "Attacking": {"atk": 1.08, "def": 0.94},
    "Balanced":  {"atk": 1.00, "def": 1.00},
    "Defensive": {"atk": 0.94, "def": 1.08},
}

TACTIC_PRESETS = {
    "pressing": {
        "Low":    {"atk": 0.99, "def": 1.02, "intensity": 0.90},
        "Normal": {"atk": 1.00, "def": 1.00, "intensity": 1.00},
        "High":   {"atk": 1.02, "def": 0.99, "intensity": 1.15},
    },
    "tempo": {
        "Slow":   {"atk": 0.98, "def": 1.02, "shots": 0.92, "intensity": 0.92},
        "Normal": {"atk": 1.00, "def": 1.00, "shots": 1.00, "intensity": 1.00},
        "Fast":   {"atk": 1.03, "def": 0.99, "shots": 1.10, "intensity": 1.12},
    },
    "width": {
        "Narrow":   {"atk": 0.99, "def": 1.01},
        "Balanced": {"atk": 1.00, "def": 1.00},
        "Wide":     {"atk": 1.02, "def": 0.99},
    },
}

LINE_HEIGHT = {
    "Deep":   {"atk": 0.98, "def": 1.03, "opp_atk": 0.98},
    "Normal": {"atk": 1.00, "def": 1.00, "opp_atk": 1.00},
    "High":   {"atk": 1.02, "def": 0.98, "opp_atk": 1.03},  # more counters conceded
}

DIRECTNESS = {
    "Short":  {"atk": 0.99, "shots": 0.95},
    "Mixed":  {"atk": 1.00, "shots": 1.00},
    "Direct": {"atk": 1.02, "shots": 1.08},
}

STYLE_MATCHUPS = {
    ("High", "Slow"): {"opp_atk": 0.98},
    ("High", "Fast"): {"opp_def": 0.99},
    ("Low",  "Fast"): {"opp_atk": 1.03},
}