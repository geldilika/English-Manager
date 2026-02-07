from operator import attrgetter
from rich.console import Console
from rich.table import Table

from src.models.schema import Team, Player
from src.ui.cli import print_matchday, league_table
from src.sim.season import simulate_matchday
from src.sim.transfers import get_transfer_list, list_player_for_transfer, search_targets, add_to_shortlist, remove_from_shortlist, get_shortlist_players, buy_player, unlist_player

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
        console.print("5) Transfers")
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
            last_search = []

            while True:
                console.print("\n[bold]Transfers[/bold]")
                console.print("1) Search players")
                console.print("2) Add from last search to shortlist")
                console.print("3) View shortlist")
                console.print("4) Buy from shortlist")
                console.print("5) Sell player")
                console.print("6) View transfer list")
                console.print("7) Remove player from transfer list")
                console.print("0) Back")

                sub = input("Choose: ").strip()

                if sub == "0":
                    break

                elif sub == "1":
                    q = input("Search name: ").strip()
                    if not q:
                        console.print("Enter a search term")
                        continue

                    last_search = search_targets(
                        db, league.id, managed_team.id, q, limit=15
                    )

                    if not last_search:
                        console.print("No matches")
                        continue

                    t = Table(title=f"Search: {q}")
                    t.add_column("#", justify="right")
                    t.add_column("Name")
                    t.add_column("Pos", justify="center")
                    t.add_column("Ovr", justify="right")
                    t.add_column("Value", justify="right")

                    i = 1
                    for p in last_search:
                        t.add_row(str(i), p.name, p.pos, str(int(p.overall)), f"£{p.value:,}")
                        i += 1

                    console.print(t)

                elif sub == "2":
                    if not last_search:
                        console.print("Search first.")
                        continue

                    pick = input("Add which #?: ").strip()
                    if not pick.isdigit():
                        console.print("Invalid number")
                        continue

                    n = int(pick)
                    if n < 1 or n > len(last_search):
                        console.print("Out of range")
                        continue

                    player = last_search[n - 1]
                    ok, msg = add_to_shortlist(db, managed_team.id, player.id)
                    console.print(msg)

                elif sub == "3":
                    shortlist = get_shortlist_players(db, managed_team.id)

                    if not shortlist:
                        console.print("Shortlist empty")
                        continue

                    t = Table(title="Shortlist")
                    t.add_column("#", justify="right")
                    t.add_column("Name")
                    t.add_column("Pos", justify="center")
                    t.add_column("Value", justify="right")

                    i = 1
                    for p in shortlist:
                        t.add_row(str(i), p.name, p.pos, f"£{p.value:,}")
                        i += 1

                    console.print(t)

                elif sub == "4":
                    shortlist = get_shortlist_players(db, managed_team.id)

                    if not shortlist:
                        console.print("Shortlist empty")
                        continue

                    t = Table(title="Buy from Shortlist")
                    t.add_column("#", justify="right")
                    t.add_column("Name")
                    t.add_column("Value", justify="right")

                    i = 1
                    for p in shortlist:
                        t.add_row(str(i), p.name, f"£{p.value:,}")
                        i += 1

                    console.print(t)

                    pick = input("Buy which #?: ").strip()
                    if not pick.isdigit():
                        console.print("Invalid number")
                        continue

                    n = int(pick)
                    if n < 1 or n > len(shortlist):
                        console.print("Out of range")
                        continue

                    player = shortlist[n - 1]

                    fee_raw = input(f"Fee (£) [Enter = £{player.value:,}]: ").strip()

                    if fee_raw == "":
                        fee = int(player.value)
                    else:
                        if not fee_raw.isdigit():
                            console.print("Invalid fee")
                            continue
                        fee = int(fee_raw)
                        
                    ok, msg = buy_player(
                        db,
                        season,
                        current_matchday - 1,
                        managed_team.id,
                        player.id,
                        fee,
                    )

                    console.print(msg)

                    if ok:
                        remove_from_shortlist(db, managed_team.id, player.id)

                elif sub == "5":
                    squad = db.query(Player).filter_by(team_id=managed_team.id).all()
                    if not squad:
                        console.print("No players in your squad")
                        continue

                    t = Table(title="List Player for Transfer")
                    t.add_column("#", justify="right")
                    t.add_column("Name")
                    t.add_column("Value", justify="right")

                    i = 1
                    for p in squad:
                        t.add_row(str(i), p.name, f"£{p.value:,}")
                        i += 1
                    console.print(t)

                    pick = input("List which #?: ").strip()
                    if not pick.isdigit():
                        console.print("Invalid number")
                        continue

                    n = int(pick)
                    if n < 1 or n > len(squad):
                        console.print("Out of range")
                        continue

                    player = squad[n - 1]

                    ask_raw = input(f"Asking price (£) [Enter = £{player.value:,}]: ").strip()
                    if ask_raw == "":
                        asking = int(player.value)
                    else:
                        if not ask_raw.isdigit():
                            console.print("Invalid asking price")
                            continue
                        asking = int(ask_raw)

                    ok, msg = list_player_for_transfer(db, season, managed_team.id, player.id, asking)
                    console.print(msg)

                elif sub == "6":
                    rows = get_transfer_list(db, season, managed_team.id, limit=50, order_by="asking")
                    if not rows:
                        console.print("Your transfer list is empty")
                        continue

                    t = Table(title="My Transfer List")
                    t.add_column("#", justify="right")
                    t.add_column("Name")
                    t.add_column("Asking", justify="right")
                    t.add_column("Value", justify="right")

                    i = 1
                    for (p, r) in rows:
                        t.add_row(str(i), p.name, f"£{r.asking_price:,}", f"£{p.value:,}")
                        i += 1
                    console.print(t)

                elif sub == "7":
                    rows = get_transfer_list(db, season, managed_team.id, limit=50, order_by="asking")
                    if not rows:
                        console.print("Your transfer list is empty")
                        continue

                    t = Table(title="Remove from Transfer List")
                    t.add_column("#", justify="right")
                    t.add_column("Name")
                    t.add_column("Asking", justify="right")

                    i = 1
                    for (p, r) in rows:
                        t.add_row(str(i), p.name, f"£{r.asking_price:,}")
                        i += 1
                    console.print(t)

                    pick = input("Remove which #?: ").strip()
                    if not pick.isdigit():
                        console.print("Invalid number")
                        continue

                    n = int(pick)
                    if n < 1 or n > len(rows):
                        console.print("Out of range")
                        continue

                    player = rows[n - 1][0]
                    ok, msg = unlist_player(db, season, managed_team.id, player.id)
                    console.print(msg)

                else:
                    console.print("Invalid option")

        elif choice == "0":
            console.print("Thanks for playing.")
            return
        else:
            console.print("Invalid option.")