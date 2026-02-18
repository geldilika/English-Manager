# ⚽ English Football Manager (CLI)

A fully interactive football manager simulation built in Python using SQLAlchemy and SQLite.

This project simulates a playable league season with tactical depth, transfers, squad management, fatigue, and injuries — all through a command-line interface.

---

## Features

### League Simulation
- Round-robin fixture generation
- Matchday-by-matchday simulation
- Dynamic league table
- xG-based match engine
- Goals and shot statistics

### Manager Mode
- Pick and manage any team
- Interactive CLI menu
- View squad and club budget
- Simulate matchdays
- View league standings

### Transfers
- Player search system
- Shortlist functionality
- Buy / sell players
- Transfer list (set asking price)
- Budget validation
- Transfer logging in database
- Dynamic player valuation system

### Squad Management
- Select Starting XI
- Bench system
- Formation validation
- Squad depth star rating

### Tactical Engine
Teams can configure:
- Formation
- Tactic preset
- Pressing
- Tempo
- Width
- Defensive line height
- Directness

Tactics affect:
- Attack & defence strength
- Shot volume
- Injury probability
- Style matchups

### Injuries & Fatigue
- Persistent injury system
- 1–3 matchday injury duration
- Injured players automatically removed from XI
- Fatigue reduces performance
- Bench players recover stamina

---

## Tech Stack

- Python 3
- SQLAlchemy
- SQLite
- Rich (CLI formatting)
- Pandas (FPL data import)
- Requests (FPL API)

---
## Project Structure

src/
models/
schema.py
sim/
match_engine.py
season.py
transfers.py
tactics_engine.py
injuries.py
ui/
menu.py
cli.py
data/
import_fpl.py
main.py

## ▶️ Setup

### 1. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
2. Install dependencies
pip install -r requirements.txt
3. Initialize database
python -c "from src.db import init_db, SessionLocal; from src.data.import_fpl import import_pl_from_fpl; init_db(); db=SessionLocal(); import_pl_from_fpl(db,'2024-25'); db.close(); print('DB READY')"
4. Run the game
python -m src.main

