from Database import db
from Models.PlayerValuations import PlayerValuations

def get_player_valuation(key):  # key = (player_id, date)
    return db.player_valuations.get(key)
