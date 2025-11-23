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

def get_players_by_position(position):
    """
    Return all players who play in a given position.
    Example input: "Midfield", "Defender", "Attack", "Goalkeeper".
    Matching is case-sensitive based on stored data.
    """
    from Database import db
    players = db.players.all()
    return [p for p in players if p.position == position]

from datetime import datetime

def get_players_older_than(age):
    """
    Returns all players older than the given age.
    Uses the player's date_of_birth field to calculate age.
    Players without valid date_of_birth are ignored.
    """
    players = db.players.all()
    result = []

    for p in players:
        if p.date_of_birth:
            try:
                dob = datetime.strptime(p.date_of_birth, "%Y-%m-%d")
                player_age = (datetime.now() - dob).days // 365

                if player_age > age:
                    result.append(p)
            except:
                # Skip invalid dates
                pass

    return result

def get_players_younger_than(age):
    """
    Returns all players younger than the given age.
    Players without valid or parsable date_of_birth are skipped.
    """
    players = db.players.all()
    result = []

    for p in players:
        if p.date_of_birth:
            try:
                dob = datetime.strptime(p.date_of_birth, "%Y-%m-%d")
                player_age = (datetime.now() - dob).days // 365
                if player_age < age:
                    result.append(p)
            except:
                pass
    return result

def get_undervalued_players(threshold_ratio=0.5):
    """
    Returns players whose current market value is significantly lower
    than their historical highest market value.
    Example: threshold_ratio=0.5 means current value < 50% of peak value.
    Players missing value data are ignored.
    """
    players = db.players.all()
    result = []

    for p in players:
        try:
            current = float(p.market_value_in_eur or 0)
            peak = float(p.highest_market_value_in_eur or 0)

            if peak > 0 and current > 0:
                ratio = current / peak
                if ratio < threshold_ratio:
                    result.append(p)
        except:
            pass

    return result

def get_players_by_country(country):
    """
    Return all players whose citizenship matches the given country.
    Case-insensitive comparison.
    """
    players = db.players.all()
    return [
        p for p in players
        if p.country_of_citizenship
        and p.country_of_citizenship.lower() == country.lower()
    ]




