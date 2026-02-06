from operator import attrgetter
from rich.console import Console
from rich.table import Table

from src.models.schema import Team, Player
from src.ui.cli import print_matchday, league_table
from src.sim.season import simulate_matchday

console = Console()

def pick_team (db, league_id):
    teams = db.query(Team).filter_by(league_id=league_id).all()
    teams.sort(key=attrgetter("name"))
    
    table = Table(title = "Choose Your Team")
    table.add_column("#", justify="right")
    table.add_column("Team")
    for i in range(len(teams)):
        table.add_row(str(i+1), teams[i].name)
    console.print(table)
    
    while True:
        choice = input("Enter team number: ").strip()

        if not choice.isdigit():
            console.print("Please enter a valid number.")
            continue

        n = int(choice)

        if 1 <= n <= len(teams):
            return teams[n - 1]

        console.print("Number out of range.")
        
def find_team(db, league_id, name):
    teams = db.query(Team).filter_by(league_id=league_id).all()
    for t in teams:
        if t.name.lower() == name.lower():
            return t
    return None

def show_my_club(db, team):
    console.print(f"My Club: {team.name}")
    console.print(f"Budget: £{team.budget:,}")
    
    players = db.query(Player).filter_by(team_id=team.id).all()
    players.sort(key=attrgetter("overall"), reverse=True)

    table = Table(title="Squad")
    table.add_column("Name")
    table.add_column("Pos", justify="center")
    table.add_column("Overall", justify="right")
    table.add_column("Attack", justify="right")
    table.add_column("Defend", justify="right")

    for p in players[:25]:
        table.add_row(
            p.name,
            p.pos,
            str(int(p.overall)),
            str(int(p.attack)),
            str(int(p.defend)),
        )
    console.print(table)
    
def run_menu(db, league, season, managed_team):
    current_matchday = 1
    
    while True:
        console.print("\n[bold]==== Manager Menu ==== [/bold]")
        console.print(f"Season: {season} | Matchday: {current_matchday}")
        console.print(f"Managing: {managed_team.name}")
        console.print("1) Simulate next matchday")
        console.print("2) Show last matchday results")
        console.print("3) Show league table")
        console.print("4) Show my club (squad + budget)")
        console.print("5) Transfers (coming next)")
        console.print("0) Exit")

        choice = input("Choose: ").strip()
        
        if choice == "1":
            simulate_matchday(db, league.id, season, current_matchday)
            print_matchday(db, league.id, season, current_matchday)
            current_matchday += 1
            if current_matchday > 38:
                current_matchday = 38
                console.print("Season finished.")

        elif choice == "2":
            md = current_matchday - 1
            if md < 1:
                console.print("No matchdays played yet.")
            else:
                print_matchday(db, league.id, season, md)
                
        elif choice == "3":
            played = current_matchday - 1
            if played < 1:
                console.print("[yellow]No matchdays played yet.[/yellow]")
            else:
                league_table(db, league.id, season, up_to_matchday=played)

        elif choice == "4":
            team = db.query(Team).get(managed_team.id)
            show_my_club(db, team)

        elif choice == "5":
            console.print("Transfers menu not yet added.")

        elif choice == "0":
            console.print("Thanks for playing.")
            return
        else:
            console.print("Invalid option.")