from flask import Flask, render_template, request, redirect, url_for
from services import appearances as appearance_service
from services import players as players_service
from services import games as games_service
from services import game_events as events_service
from services import competitions as competitions_service
from services import playervaluations as playervaluations_service
from services import club_games as club_games_service
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
        
        # 1. TABLODA GÖRÜNECEK SÜTUNLAR (İsimler var, ID yok)
        "columns": [
            "game_id", 
            "club_name", 
            "hosting", 
            "own_goals", 
            "opponent_goals", 
            "is_win", 
            "opponent_name", 
            "own_manager_name"
        ],
        
        # 2. FORMDA İSTENECEK SÜTUNLAR (Veritabanı için ID ŞART!)
        "form_columns": [
            "game_id", 
            "club_id",
            "hosting", 
            "own_goals", 
            "own_position",
            "own_manager_name",
            "opponent_id",
            "opponent_goals", 
            "opponent_position",
            "opponent_manager_name",
            "is_win"
        ],

        "headers": {
            "game_id": "Game ID",
            "club_name": "Club",
            "hosting": "Side",
            "own_goals": "Home Goals",
            "opponent_goals": "Away Goals",
            "is_win": "Result",
            "opponent_name": "Opponent",
            "own_manager_name": "Manager"
        }
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
        data_objects = club_games_service.get_all_club_games(page, per_page, search_term)
        total_count = club_games_service.get_total_club_game_count(search_term)
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
                          search_term=search_term,
                          table_schemas=TABLE_SCHEMAS)

@app.route('/table/<table_name>/add', methods=['GET', 'POST'])
def add_record(table_name):
    if table_name not in TABLE_SCHEMAS:
        return "Tablo bulunamadı", 404

    schema = TABLE_SCHEMAS[table_name]
    
    # --- DÜZELTME BURADA: Form için özel sütun listesi var mı? ---
    # Varsa onu kullan (ID'li olanı), yoksa normal listeyi kullan.
    # Bu satır olmazsa formda Club ID kutusu çıkmaz!
    actual_columns = schema.get('form_columns', schema['columns'])
    # -----------------------------------------------------------

    if request.method == 'POST':
        form_data = request.form.to_dict()
        result = None
        
        try:
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
                # İsmi düzeltilmiş servis
                result = club_games_service.insert_club_game(form_data)
            elif table_name == 'clubs':
                result = clubs_service.insert_club(form_data)
            
            # Sonuç kontrolü (Hata varsa ekrana bas)
            if result and isinstance(result, str) and "Error" in result:
                return f"Hata oluştu: {result}"
                
            return redirect(url_for('show_table', table_name=table_name))
            
        except Exception as e:
            return f"Python İşlem Hatası: {str(e)}"

    return render_template('form.html', 
                          table_name=table_name, 
                          title=schema['title'],
                          columns=actual_columns) # <-- BURASI ÇOK ÖNEMLİ: schema['columns'] DEĞİL, actual_columns OLACAK
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
            result = club_games_service.insert_club_game(form_data)
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

@app.route('/table/club_games/delete/<int:game_id>', methods=['GET', 'POST'])
def delete_club_game_route(game_id):
    # İmza: Doğru fonksiyonun çalıştığını terminalde görmek için
    print(f"--- ÖZEL CLUB GAMES SİLME FONKSİYONU ÇALIŞTI (ID: {game_id}) ---")

    try:
        # Servisi çağır
        result = club_games_service.delete_club_game(game_id)
        
        # Sonucu işle (Tuple dönüyorsa ayır, dönmüyorsa düz al)
        if isinstance(result, tuple) and len(result) == 2:
            success, message = result
        else:
            success = result
            message = "İşlem tamamlandı."

        if success:
            return redirect(url_for('show_table', table_name='club_games'))
        else:
            # Hata varsa kırmızı kutu göster
            return f"""
            <div style="font-family: Arial; padding: 20px; border: 4px solid red; background-color: #fff0f0;">
                <h2 style="color: red;">SİLME BAŞARISIZ (ÖZEL FONKSİYON)</h2>
                <p><b>Hata Detayı:</b> {message}</p>
                <br>
                <a href="/table/club_games">Geri Dön</a>
            </div>
            """
            
    except Exception as e:
        return f"PYTHON HATASI: {str(e)}"
    try:
        # Servisten yanıt almayı dene
        result = club_games_service.delete_club_game(game_id)
        
        # Eğer servis iki değer döndürüyorsa (success, message)
        if isinstance(result, tuple) and len(result) == 2:
            success, message = result
        else:
            # Eğer eski servis kullanılıyorsa sadece True/False döner
            success = result
            message = "Servis sadece True/False döndürdü, detay yok."

        if success:
            return redirect(url_for('get_all_club_games_route'))
        else:
            # HATA VARSA BU KIRMIZI KUTUYU GÖSTER
            return f"""
            <div style="font-family: Arial; padding: 20px; border: 4px solid red; background-color: #fff0f0;">
                <h1 style="color: red;">HATA YAKALANDI! (PORT 5001)</h1>
                <h3>Silinememe Sebebi:</h3>
                <p style="font-size: 18px; font-weight: bold;">{message}</p>
                <br>
                <hr>
                <p><i>Hakkı Yusuf, bu hatayı kopyalayıp bana atarsan sorunu hemen çözerim.</i></p>
                <a href="/table/club_games">Geri Dön</a>
            </div>
            """
            
    except Exception as e:
        return f"PYTHON KOD HATASI: {str(e)}"
    # İmza testi: Konsola yazdır
    print(f"SİLME İSTEĞİ GELDİ - ID: {game_id}")

    try:
        success, message = club_games_service.delete_club_game(game_id)
    except Exception as e:
        return f"SERVİS HATASI: {str(e)}"

    if success:
        return redirect(url_for('get_all_club_games_route'))
    else:
        # Hata mesajına "HAKKI YUSUF TEST" yazdık.
        # Eğer ekranda bunu görmezsen, yanlış dosyayı çalıştırıyorsun demektir.
        return f"""
        <div style="border: 5px solid red; padding: 20px; font-size: 20px;">
            <h1>HAKKI YUSUF TEST - SİLME BAŞARISIZ</h1>
            <p><b>Hata Detayı:</b> {message}</p>
        </div>
        """
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
            result = clubs_service.delete_club(id)
            if result is True:
                success = True
            else:
                print(f"Kulüp silme hatası: {result}")
                success = False
    elif table_name == 'games':
        # success = games_service.delete_game(id)
        pass

    if success:
        return redirect(url_for('show_table', table_name=table_name))
    else:
        return f"Silme işlemi başarısız (ID: {id})"

if __name__ == '__main__':
    app.run(debug=True, port=5001)