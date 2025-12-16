from flask import Flask, render_template, request, redirect, url_for
from services import appearances as appearance_service
from services import players as players_service
from services import games as games_service
from services import game_events as events_service
from services import competitions as competitions_service
from services import playervaluations as playervaluations_service
from services import club_games as clubgames_service
from services import clubs as clubs_service

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
        "columns": ["appearance_id", "player_name", "player_id", "competition_id", "assists", "minutes_played"]
    },
    "club_games": {
        "title": "Club Matches",
        "icon": "fa-regular fa-calendar-check",
        "columns": [
            "game_id", "club_id", "hosting", "own_goals", "opponent_goals", 
            "is_win", "opponent_id", "own_manager_name"
        ]
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
            "game_id", "date", "competition_id", "home_club_name", 
            "away_club_name", "home_club_goals", "away_club_goals",
            "stadium", "referee"
        ]
    },
    "game_events": {
        "title": "Match Events",
        "icon": "fa-solid fa-bell", 
        "columns": [
            "game_id", "minute", "type", "club_id", 
            "player_id", "description"
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
    
    page = request.args.get('page', 1, type=int)
    per_page = 50 
    search_term = request.args.get('q', '').strip()

    schema = TABLE_SCHEMAS[table_name]
    data_objects = []
    total_count = 0

    if table_name == 'appearances':
        data_objects = appearance_service.get_all_appearances(page, per_page, search_term)
        total_count = appearance_service.get_total_appearance_count(search_term)
    elif table_name == 'players': 
        data_objects = players_service.get_all_players(page, per_page, search_term)
        total_count = players_service.get_total_player_count()
    elif table_name == 'games':
        data_objects = games_service.get_all_games(page, per_page, search_term)
        total_count = games_service.get_total_game_count(search_term)
    elif table_name == 'game_events':
        data_objects = events_service.get_all_events(page, per_page, search_term)
        total_count = events_service.get_total_event_count(search_term)
    elif table_name == 'competitions':
        data_objects = competitions_service.get_all_competitions(page, per_page, search_term)
        total_count = competitions_service.get_total_competition_count(search_term)
    elif table_name == 'playervaluations':
        data_objects = playervaluations_service.get_all_valuations(page, per_page, search_term)
        total_count = playervaluations_service.get_total_valuation_count(search_term)
    elif table_name == 'club_games':
        data_objects = clubgames_service.get_all_club_games(page, per_page, search_term)
        total_count = clubgames_service.get_total_club_game_count(search_term)
    elif table_name == 'clubs':
        data_objects = clubs_service.get_all_clubs(page, per_page, search_term)
        total_count = clubs_service.get_total_club_count(search_term)

    total_pages = (total_count + per_page - 1) // per_page
    data_dicts = [vars(obj) for obj in data_objects]

    return render_template('table.html', 
                          table_name=table_name, 
                          title=schema['title'],
                          columns=schema['columns'],
                          data=data_dicts,
                          current_page=page,
                          total_pages=total_pages,
                          total_count=total_count,
                          per_page=per_page,
                          search_term=search_term)

@app.route('/table/<table_name>/add', methods=['GET', 'POST'])
def add_record(table_name):
    if table_name not in TABLE_SCHEMAS:
        return "Tablo bulunamadı", 404

    schema = TABLE_SCHEMAS[table_name]

    if request.method == 'POST':
        form_data = request.form.to_dict()
        result = None
        
        if table_name == 'appearances':
            result = appearance_service.insert_appearance(form_data)
        elif table_name == 'players':
            result = players_service.insert_player(form_data)
        elif table_name == 'games':
            result = games_service.insert_game(form_data)
        elif table_name == 'game_events':
            result = events_service.insert_event(form_data)
        elif table_name == 'competitions':
            result = competitions_service.insert_competition(form_data)
        elif table_name == 'playervaluations':
            result = playervaluations_service.insert_valuation(form_data)
        elif table_name == 'club_games':
            result = clubgames_service.insert_club_game(form_data)
        elif table_name == 'clubs':
            result = clubs_service.insert_club(form_data)
        
        if result and "Error" in str(result):
            return f"Hata oluştu: {result}"
                
        return redirect(url_for('show_table', table_name=table_name))

    return render_template('form.html', 
                          table_name=table_name, 
                          title=schema['title'],
                          columns=schema['columns'])

# --- 1. ÖZEL DELETE ROUTE: Game Events (EKSİK OLAN KISIM BURASIYDI) ---
@app.route('/table/game_events/delete/<game_id>/<int:minute>/<type>', methods=['POST'])
def delete_game_event_record(game_id, minute, type):
    success = events_service.delete_event(game_id, minute, type)
    if success:
        return redirect(url_for('show_table', table_name='game_events'))
    else:
        return f"Silme Başarısız! (Maç: {game_id}, Dk: {minute}, Tip: {type})"

# --- ÖZEL DELETE ROUTE: Club Games ---
@app.route('/table/club_games/delete/<int:game_id>/<int:club_id>', methods=['POST'])
def delete_club_game_record(game_id, club_id):
    # Bu tabloda Composite Key var: game_id + club_id
    success = clubgames_service.delete_club_game(game_id, club_id)
    
    if success:
        return redirect(url_for('show_table', table_name='club_games'))
    else:
        return f"Silme Başarısız! (Maç ID: {game_id}, Kulüp ID: {club_id})"

# --- 2. GENEL DELETE ROUTE: Diğer Tablolar ---
@app.route('/table/<table_name>/delete/<id>', methods=['POST'])
def delete_record(table_name, id):
    if table_name not in TABLE_SCHEMAS:
        return "Tablo bulunamadı", 404
    
    success = False

    if table_name == 'appearances':
        success = appearance_service.delete_appearance(id)
    elif table_name == 'players':
        success = players_service.delete_player(id)
    elif table_name == 'clubs':
        # success = clubs_service.delete_club(id)
        pass 
    elif table_name == 'games':
        # success = games_service.delete_game(id)
        pass

    if success:
        return redirect(url_for('show_table', table_name=table_name))
    else:
        return f"Silme işlemi başarısız (ID: {id})"

if __name__ == '__main__':
    app.run(debug=True)