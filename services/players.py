# File: services/players.py
# Author: Hasan Özgür Çağan
# Description: Service layer for the Players model in the Moneyball project.
#              Provides backend functions to retrieve and process player data
#              using the database connection (db).

from Database import db
from Models.Players import Players

def get_player(player_id):
    """
    Fetch a single player from the database by their unique player_id.
    Returns a Players object if found, otherwise None.
    """
    return db.players.get(player_id)


def get_all_players():
    """
    Retrieve all player records from the database.
    Returns a list of Players objects.
    """
    return db.players.all()


def get_top_players(limit=10):
    """
    Retrieve the top N players ranked by their market value (descending order).
    Default is 10 players.
    """
    players = db.players.all()
    return sorted(
        players,
        key=lambda p: float(p.market_value_in_eur or 0),
        reverse=True
    )[:limit]
