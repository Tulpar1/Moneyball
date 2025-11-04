from Database import db
from Models.Clubs import Clubs

def get_club(club_key):
    return db.clubs.get(club_key)

def get_all_clubs():
    return db.clubs.values()
