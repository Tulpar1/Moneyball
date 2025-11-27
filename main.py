from flask import Flask, render_template, request, redirect, url_for
from services import appearances as appearance_service
from services import players as players_service
from services import games as games_service  
from services import game_events as events_service
app = Flask(__name__)


TABLE_SCHEMAS = {
    "players": {
        "title": "Players",
        "icon": "fa-solid fa-user",
        "columns": ["player_id", "name", "country_of_birth", "date_of_birth", "position", "sub_position"]
    },
    "clubs": {
        "title": "Clubs",
        "icon": "fa-solid fa-shield",
        "columns": ["club_id", "name", "domestic_competition_id", "squad_size", "average_age"]
    },
    "competitions": {
        "title": "Leagues / Competitions",
        "icon": "fa-solid fa-trophy", 
        "columns": ["competition_id", "name", "type", "country_name", "confederation"]
    },
    "appearances": {
        "title": "Match Statistics",
        "icon": "fa-solid fa-person-running",
        "columns": ["appearance_id", "game_id", "player_id", "goals", "assists", "minutes_played"]
    },
    "club_games": {
        "title": "Club Matches",
        "icon": "fa-regular fa-calendar-check",
        "columns": ["game_id", "home_club_id", "away_club_id", "season", "round", "date"]
    },
    "playervaluations": {
        "title": "Market Values",
        "icon": "fa-solid fa-line-chart",
        "columns": ["player_id", "date", "market_value_in_eur", "current_club_id"]
    },
    "games": {
        "title": "Match Details",
        "icon": "fa-solid fa-trophy", 
        "columns": [
            "game_id", 
            "date", 
            "competition_id",           # Hangi ligde/kupada oynandı? (Analiz için çok önemli)
            "home_club_name", 
            "away_club_name", 
            "home_club_goals", 
            "away_club_goals",
            "stadium",                  # Maçın Ev Sahibi/Deplasman dengesi için önemli
            "referee"                   # Hakem verisi (Analitik varyasyon için)
        ]
    },
    "game_events": {
        "title": "Match Events",
        "icon": "fa-solid fa-bell", 
        "columns": [
            "game_id", 
            "minute", 
            "type", 
            "club_id",                  # Hangi kulübün olayı gerçekleştirdiği (H/A ayrımı)
            "player_id", 
            "description"
    ]
}

}

@app.route('/')
def index():
    return render_template('index.html', tables=TABLE_SCHEMAS)

@app.route('/table/<table_name>')
def show_table(table_name):
    if table_name not in TABLE_SCHEMAS:
        return "Tablo bulunamadı", 404
    
    schema = TABLE_SCHEMAS[table_name]
    data_objects = []

    # 1. Hangi tablo istendiyse onun servisine git
    if table_name == 'appearances':
        data_objects = appearance_service.get_all_appearances(limit=50)
    elif table_name == 'players':   # 'elif' kullanmak daha verimlidir
        data_objects = players_service.get_all_players(limit=50)
    elif table_name == 'games':     # YENİ EKLEME: Games Servisi
        # games_service.get_all_games fonksiyonunun limit=50 alabilmesi gerekir.
        data_objects = games_service.get_all_games(limit=50)
    elif table_name == 'game_events': # YENİ EKLEME: Game Events Servisi
        # events_service.get_all_game_events fonksiyonu gereklidir.
        data_objects = events_service.get_all_game_events(limit=50)
    # Not: İleride elif table_name == 'players': ... diye gidecek

    # 2. Template objeleri (row.player_name) okuyabilir ama
    # generic template (row['player_name']) bekliyorsa dönüşüm yapmalıyız.
    # Bizim template yapımız row['col'] şeklinde olduğu için objeleri dict'e çeviriyoruz:
    data_dicts = [vars(obj) for obj in data_objects]

    return render_template('table.html', 
                            table_name=table_name, 
                            title=schema['title'],
                            columns=schema['columns'],
                            data=data_dicts)

@app.route('/table/<table_name>/add', methods=['GET', 'POST'])
def add_record(table_name):
    if table_name not in TABLE_SCHEMAS:
        return "Tablo bulunamadı", 404

    schema = TABLE_SCHEMAS[table_name]

    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        # INSERT İşlemi
        if table_name == 'appearances':
            result = appearance_service.insert_appearance(form_data)
        elif table_name == 'players':
            result = players_service.insert_player(form_data)
        elif table_name == 'games':        # YENİ EKLEME: Games Insert
            result = games_service.insert_game(form_data)
        elif table_name == 'game_events':  # YENİ EKLEME: Game Events Insert
            result = events_service.insert_game_event(form_data)
            
            if "Error" in str(result):
                return f"Hata oluştu: {result}"
                
        return redirect(url_for('show_table', table_name=table_name))

    return render_template('form.html', 
                         table_name=table_name, 
                         title=schema['title'],
                         columns=schema['columns'])

if __name__ == '__main__':
    app.run(debug=True)