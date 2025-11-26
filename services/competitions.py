from Database import db
from Models.Competitions import Competitions

def get_competition(competition_id):
    return db.competitions.get(competition_id)
