<<<<<<< HEAD
from Database import db
from Models.Competitions import Competitions

def get_competition(competition_id):
    return db.competitions.get(competition_id)
=======
from Database import db
from Models.Competitions import Competitions

def get_competition(competition_id):
    return db.competitions.get(competition_id)

def get_competition_total_market_value(competition_id):
    """
    Bir ligdeki (Competition) tüm oyuncuların toplam piyasa değerini hesaplar.
    """
    query = """
        SELECT c.name, SUM(p.market_value_in_eur) as total_value
        FROM competitions c
        JOIN clubs cl ON c.competition_id = cl.domestic_competition_id
        JOIN players p ON cl.club_id = p.current_club_id
        WHERE c.competition_id = %s
        GROUP BY c.name
    """
    cursor.execute(query, (competition_id,))
    return cursor.fetchone()
>>>>>>> 8ea19d707d171c70732efbe4abd89c671b6c9e5c
