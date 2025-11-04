from Database import db
from Models.ClubGames import ClubGames

def get_club_game(game_key):
    return db.club_games.get(game_key)

def get_all_club_games():
    return db.club_games.values()
