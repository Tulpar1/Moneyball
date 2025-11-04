from Database import db
from Models.Appearances import Appearances

def get_appearance(appearance_key):
    return db.appearances.get(appearance_key)
