from sqlalchemy import or_
from src.models.schema import Team, Player, Transfer, Shortlist

def list_targets(db, league_id, exclude_team_id, limit=20, order_by="value"):
    q = (
        db.query(Player)
        .join(Team, Player.team_id == Team.id)
        .filter(Team.league_id == league_id)
        .filter(Player.team_id != exclude_team_id)
    )

    if order_by == "overall":
        q = q.order_by(Player.overall.desc())
    else:
        q = q.order_by(Player.value.desc())

    return q.limit(limit).all()


def search_targets(db, league_id, exclude_team_id, query, limit=20, order_by="value"):
    q = (
        db.query(Player)
        .join(Team, Player.team_id == Team.id)
        .filter(Team.league_id == league_id)
        .filter(Player.team_id != exclude_team_id)
        .filter(Player.name.ilike(f"%{query}%"))
    )

    if order_by == "overall":
        q = q.order_by(Player.overall.desc())
    else:
        q = q.order_by(Player.value.desc())

    return q.limit(limit).all()


def list_squad(db, team_id, order_by="value"):
    q = db.query(Player).filter(Player.team_id == team_id)

    if order_by == "overall":
        q = q.order_by(Player.overall.desc())
    else:
        q = q.order_by(Player.value.desc())

    return q.all()

def add_to_shortlist(db, team_id, player_id):
    exists = (
        db.query(Shortlist)
        .filter(Shortlist.team_id == team_id, Shortlist.player_id == player_id)
        .first()
    )
    if exists:
        return False, "Already on shortlist"

    db.add(Shortlist(team_id=team_id, player_id=player_id))
    db.commit()
    return True, "Added to shortlist"


def remove_from_shortlist(db, team_id, player_id):
    row = (
        db.query(Shortlist)
        .filter(Shortlist.team_id == team_id, Shortlist.player_id == player_id)
        .first()
    )
    if not row:
        return False, "Not on shortlist"

    db.delete(row)
    db.commit()
    return True, "Removed from shortlist"


def get_shortlist_players(db, team_id, limit=50, order_by="value"):
    q = (
        db.query(Player)
        .join(Shortlist, Shortlist.player_id == Player.id)
        .filter(Shortlist.team_id == team_id)
    )

    if order_by == "overall":
        q = q.order_by(Player.overall.desc())
    else:
        q = q.order_by(Player.value.desc())

    return q.limit(limit).all()

def buy_player(db, season, matchday, buyer_team_id, player_id, fee):
    buyer = db.get(Team, buyer_team_id)
    player = db.get(Player, player_id)

    if buyer is None or player is None:
        return False, "Buyer or player not found"

    if player.team_id == buyer.id:
        return False, "Player already in your team"

    seller = db.get(Team, player.team_id) if player.team_id else None

    if fee <= 0:
        return False, "Fee must be > 0"

    if buyer.budget < fee:
        return False, "Not enough budget"

    buyer.budget -= fee
    if seller:
        seller.budget += fee

    from_team_id = seller.id if seller else None
    player.team_id = buyer.id

    db.add(
        Transfer(
            season=season,
            matchday=matchday,
            player_id=player.id,
            from_team_id=from_team_id,
            to_team_id=buyer.id,
            fee=fee,
        )
    )

    db.commit()
    return True, f"Bought {player.name} for £{fee:,}"


def sell_player(db, season, matchday, seller_team_id, buyer_team_id, player_id, fee):
    seller = db.get(Team, seller_team_id)
    buyer  = db.get(Team, buyer_team_id)
    player = db.get(Player, player_id)

    if seller is None or buyer is None or player is None:
        return False, "Seller, buyer, or player not found"

    if buyer.id == seller.id:
        return False, "Buyer must be a different club"

    if player.team_id != seller.id:
        return False, "That player is not in your team"

    if fee <= 0:
        return False, "Fee must be > 0"

    if buyer.budget < fee:
        return False, "Buyer cannot afford this fee"

    buyer.budget -= fee
    seller.budget += fee

    player.team_id = buyer.id

    db.add(Transfer(
        season=season,
        matchday=matchday,
        player_id=player.id,
        from_team_id=seller.id,
        to_team_id=buyer.id,
        fee=fee
    ))

    db.commit()
    return True, f"Sold {player.name} to {buyer.name} for £{fee:,}"