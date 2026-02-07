from rich.console import Console
from src.models.schema import Team, Player, Transfer

console = Console()

def list_targets(db, league_id, exclude_team_id, limit=20):
    players = db.query(Player).all()

    out = []
    for p in players:
        if p.team_id != exclude_team_id:
            out.append(p)

    out.sort(key=Player.overall.__get__, reverse=True)

    return out[:limit]

def buy_player(db, season, matchday, buyer_team_id, player_id, fee):
    buyer = db.query(Team).get(buyer_team_id)
    player = db.query(Player).get(player_id)
    
    if buyer is None or Player is None:
        return False, "Buyer or player not found"
    
    if player.team_id == buyer.id:
        return False, "Player already in your team"
    
    seller = db.query(Team).get(player.team_id) if player.team_id else None
    
    if buyer.budget < fee:
        return False, "Not enough budget"
    
    buyer.budget -= fee
    if seller:
        seller.budget += fee

    from_team_id = seller.id if seller else None
    player.team_id = buyer.id
    
    db.add(Transfer(
        season=season,
        matchday=matchday,
        player_id=player.id,
        from_team_id=from_team_id,
        to_team_id=buyer.id,
        fee=fee
    ))
    
    db.commit()
    return True, "Transfer completed"

def sell_player(db, season, matchday, seller_team_id, player_id, fee):
    seller = db.query(Team).get(seller_team_id)
    player = db.query(Player).get(player_id)
    if seller is None or player is None:
        return False, "Seller or player not found"

    if player.team_id != seller.id:
        return False, "That player is not in your team"

    seller.budget += fee
    player.team_id = None

    db.add(Transfer(
        season=season,
        matchday=matchday,
        player_id=player.id,
        from_team_id=seller.id,
        to_team_id=seller.id,
        fee=fee
    ))

    db.commit()
    return True, "Player sold (now free agent)"