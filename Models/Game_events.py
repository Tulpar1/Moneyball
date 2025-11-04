import csv

class GameEvents:
    def __init__(
        self,
        game_id,
        minute,
        type,
        club_id,
        player_id,
        description,
        player_in_id
    ):
        self.game_id = game_id
        self.minute = minute
        self.type = type
        self.club_id = club_id
        self.player_id = player_id
        self.description = description
        self.player_in_id = player_in_id