<<<<<<< HEAD
from Database import db
from Models.PlayerValuations import PlayerValuations

def get_player_valuation(key):  # key = (player_id, date)
    return db.player_valuations.get(key)
=======
from Database import db
from Models.PlayerValuations import PlayerValuations

def get_player_valuation(key):  # key = (player_id, date)
    return db.player_valuations.get(key)

def get_player_valuation_trend(player_id):
    """
    Oyuncunun son 10 piyasa değeri kaydını tarihe göre sıralı getirir.
    Grafik çizdirmek veya artış/azalış görmek için kullanılır.
    """
    query = """
        SELECT date, market_value_in_eur 
        FROM player_valuations 
        WHERE player_id = %s 
        ORDER BY date DESC 
        LIMIT 10
    """
    cursor.execute(query, (player_id,))
    results = cursor.fetchall()
    return results
>>>>>>> 8ea19d707d171c70732efbe4abd89c671b6c9e5c
