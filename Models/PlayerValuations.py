class PlayerValuations:
    def __init__(self, player_id, last_season, datetime, date, dateweek,
                 market_value_in_eur, n, current_club_id,
                 player_club_domestic_competition_id):
        self.player_id = int(player_id) if player_id not in ("", None) else None
        self.last_season = int(last_season) if last_season not in ("", None) else None
        self.datetime = datetime                 # string olarak saklıyoruz; ihtiyaca göre parse edebilirsin
        self.date = date                         # "YYYY-MM-DD"
        self.dateweek = dateweek                 # "YYYY-MM-DD"
        self.market_value_in_eur = int(market_value_in_eur) if market_value_in_eur not in ("", None) else None
        self.n = int(n) if n not in ("", None) else None
        self.current_club_id = int(current_club_id) if current_club_id not in ("", None) else None
        self.player_club_domestic_competition_id = player_club_domestic_competition_id

    def __repr__(self):
        return f"<PlayerValuations player_id={self.player_id} date={self.date} value={self.market_value_in_eur}>"
