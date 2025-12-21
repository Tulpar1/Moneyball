from database import get_db_connection

class ClubGameModel:
    @staticmethod
    def get_all_club_games(search_query=None, is_win=None, page=1, per_page=20):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        offset = (page - 1) * per_page
        
        where_clauses = []
        params = []
        
        # Filtreleme
        if search_query:
            where_clauses.append("""(
                cg.own_manager_name LIKE %s OR 
                c_own.name LIKE %s OR
                c_opp.name LIKE %s
            )""")
            params.extend([f"%{search_query}%"] * 3)
        
        if is_win is not None and is_win != "":
            where_clauses.append("cg.is_win = %s")
            params.append(is_win)
            
        where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        try:
            # GÜNCELLEME: 'cg.*' diyerek tablodaki her şeyi garantiye aldık.
            query = f"""
                SELECT cg.*, 
                       c_own.name as club_name, 
                       c_opp.name as opponent_name,
                       g.date as date
                FROM club_games cg
                LEFT JOIN clubs c_own ON cg.club_id = c_own.club_id
                LEFT JOIN clubs c_opp ON cg.opponent_id = c_opp.club_id
                LEFT JOIN games g ON cg.game_id = g.game_id
                {where_str}
                ORDER BY g.date DESC
                LIMIT %s OFFSET %s
            """
            
            current_params = params + [per_page, offset]
            cursor.execute(query, tuple(current_params))
            stats = cursor.fetchall()
            
            # Toplam sayı
            count_query = f"""
                SELECT COUNT(*) as count 
                FROM club_games cg
                LEFT JOIN clubs c_own ON cg.club_id = c_own.club_id
                LEFT JOIN clubs c_opp ON cg.opponent_id = c_opp.club_id
                {where_str}
            """
            cursor.execute(count_query, tuple(params))
            res = cursor.fetchone()
            total_count = res['count'] if res else 0
            
            return stats, total_count
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def add_match(date, home_club_id, away_club_id, home_score, away_score, home_manager, away_manager):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            # 1. Yeni bir GAME ID oluştur
            cursor.execute("SELECT MAX(game_id) FROM games")
            row = cursor.fetchone()
            max_id = row[0] if row and row[0] else 0
            new_game_id = max_id + 1

            # 2. GAMES tablosuna tarihi ekle
            # (Eğer games tablosunda başka zorunlu alan varsa hata verebilir, basit tutuyoruz)
            cursor.execute("INSERT INTO games (game_id, date) VALUES (%s, %s)", (new_game_id, date))

            # 3. Skorları Sayıya Çevir
            h_score = int(home_score)
            a_score = int(away_score)

            # 4. Galibiyet Durumlarını Hesapla (1: Kazandı, 0: Kazanamadı)
            home_win = 1 if h_score > a_score else 0
            away_win = 1 if a_score > h_score else 0

            # 5. CLUB_GAMES - Ev Sahibi Kaydı
            sql_home = """
                INSERT INTO club_games 
                (game_id, club_id, opponent_id, own_goals, opponent_goals, hosting, is_win, own_manager_name) 
                VALUES (%s, %s, %s, %s, %s, 'Home', %s, %s)
            """
            cursor.execute(sql_home, (new_game_id, home_club_id, away_club_id, h_score, a_score, home_win, home_manager))

            # 6. CLUB_GAMES - Deplasman Kaydı
            sql_away = """
                INSERT INTO club_games 
                (game_id, club_id, opponent_id, own_goals, opponent_goals, hosting, is_win, own_manager_name) 
                VALUES (%s, %s, %s, %s, %s, 'Away', %s, %s)
            """
            cursor.execute(sql_away, (new_game_id, away_club_id, home_club_id, a_score, h_score, away_win, away_manager))

            db.commit()
            return True
        except Exception as e:
            print(f"HATA: {e}")
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def delete_match(game_id):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            # Önce club_games tablosundaki detayları sil
            cursor.execute("DELETE FROM club_games WHERE game_id = %s", (game_id,))
            # Sonra games tablosundaki ana kaydı sil
            cursor.execute("DELETE FROM games WHERE game_id = %s", (game_id,))
            db.commit()
            return True
        except Exception as e:
            print(f"Silme Hatası: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def get_match_details(game_id):
        # Düzenleme penceresi için maç verilerini çeker
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            query = """
                SELECT cg.*, g.date
                FROM club_games cg
                JOIN games g ON cg.game_id = g.game_id
                WHERE cg.game_id = %s
            """
            cursor.execute(query, (game_id,))
            rows = cursor.fetchall()
            
            if not rows: return None
            
            # Veriyi işle: Home ve Away satırlarını tek bir nesnede birleştir
            match_data = {'game_id': game_id, 'date': rows[0]['date']}
            
            for row in rows:
                if row['hosting'] == 'Home':
                    match_data['home_club_id'] = row['club_id']
                    match_data['home_score'] = row['own_goals']
                    match_data['home_manager'] = row['own_manager_name']
                else:
                    match_data['away_club_id'] = row['club_id']
                    match_data['away_score'] = row['own_goals']
                    match_data['away_manager'] = row['own_manager_name']
            
            return match_data
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def update_match(game_id, date, home_club_id, away_club_id, home_score, away_score, home_manager, away_manager):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            # 1. Games tablosunda tarihi güncelle
            cursor.execute("UPDATE games SET date = %s WHERE game_id = %s", (date, game_id))
            
            # 2. Club_games tablosundaki eski kayıtları temizle
            cursor.execute("DELETE FROM club_games WHERE game_id = %s", (game_id,))
            
            # 3. Yeni verilerle tekrar ekle
            h_score = int(home_score)
            a_score = int(away_score)
            home_win = 1 if h_score > a_score else 0
            away_win = 1 if a_score > h_score else 0

            # Ev Sahibi Kaydı
            cursor.execute("""
                INSERT INTO club_games (game_id, club_id, opponent_id, own_goals, opponent_goals, hosting, is_win, own_manager_name)
                VALUES (%s, %s, %s, %s, %s, 'Home', %s, %s)
            """, (game_id, home_club_id, away_club_id, h_score, a_score, home_win, home_manager))

            # Deplasman Kaydı
            cursor.execute("""
                INSERT INTO club_games (game_id, club_id, opponent_id, own_goals, opponent_goals, hosting, is_win, own_manager_name)
                VALUES (%s, %s, %s, %s, %s, 'Away', %s, %s)
            """, (game_id, away_club_id, home_club_id, a_score, h_score, away_win, away_manager))

            db.commit()
        finally:
            if db.is_connected():
                cursor.close()
                db.close()