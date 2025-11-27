from Database import db
from Models.Games import Games

# Games Sınıfının tüm alanlarını listeleyelim
GAME_COLUMNS = [
    'game_id', 'competition_id', 'season', 'round', 'date', 'home_club_id',
    'away_club_id', 'home_club_goals', 'away_club_goals', 'home_club_position',
    'away_club_position', 'home_club_manager_name', 'away_club_manager_name',
    'stadium', 'attendance', 'referee', 'url', 'home_club_name',
    'away_club_name', 'aggregate', 'competition_type'
]

SELECT_FIELDS = ', '.join(GAME_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(GAME_COLUMNS))

## Games Veritabanı İşlemleri
# -----------------------------

# --- (Read) ---
def get_game(game_id):
    """Belirtilen game_id'ye sahip oyunu veritabanından getirir."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM games WHERE game_id = %s"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return Games(**result)
        return None

    except Exception as e:
        print(f"Error (get_game): {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- (Insert) ---
def insert_game(game_data: dict):
    """Yeni bir oyun kaydını veritabanına ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO games ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        insert_values = [game_data.get(col) for col in GAME_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        new_id = game_data.get('game_id', cursor.lastrowid)

        conn.commit()
        cursor.close()
        return new_id

    except Exception as e:
        print(f"Error (insert_game): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Delete) ---
def delete_game(game_id):
    """Belirtilen game_id'ye sahip oyunu veritabanından siler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = "DELETE FROM games WHERE game_id = %s"
        cursor.execute(query, (game_id,))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected > 0

    except Exception as e:
        print(f"Error (delete_game): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Update) ---
def update_game(game_id, update_data: dict):
    """Belirtilen game_id'ye ait oyunun verilerini günceller."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        set_clauses = []
        update_values = []

        if 'game_id' in update_data:
            del update_data['game_id']

        for col, value in update_data.items():
            if col in GAME_COLUMNS:
                set_clauses.append(f"{col} = %s")
                update_values.append(value)
        
        if not set_clauses:
            return 0

        query = f"UPDATE games SET {', '.join(set_clauses)} WHERE game_id = %s"
        update_values.append(game_id)

        cursor.execute(query, tuple(update_values))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected

    except Exception as e:
        print(f"Error (update_game): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# --- (Query/Search) ---
def search_games_by_club(club_id):
    """Belirtilen kulübün (ev sahibi veya deplasman) oynadığı tüm maçları getirir."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()

        query = f"""
        SELECT {SELECT_FIELDS} FROM games 
        WHERE home_club_id = %s OR away_club_id = %s
        ORDER BY date DESC
        """
        cursor.execute(query, (club_id, club_id))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(Games(**row))

        return results_list

    except Exception as e:
        print(f"Error (search_games_by_club): {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- (List All with Pagination) ---
def get_total_game_count(search_term=""):
    """Filtrelenmiş veya tüm oyunların toplam sayısını döndürür."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        where_clause = ""
        query_params = []
        
        if search_term:
            search_like = f"%{search_term}%"
            search_cols = ["home_club_name", "away_club_name", "competition_id", "stadium"]
            where_conditions = [f"{col} LIKE %s" for col in search_cols]
            where_clause = " WHERE " + " OR ".join(where_conditions)
            query_params = [search_like] * len(search_cols)

        query = f"SELECT COUNT(*) FROM games {where_clause}"
        cursor.execute(query, tuple(query_params))
        result = cursor.fetchone()
        
        return result[0] if isinstance(result, tuple) else (result['COUNT(*)'] if result else 0)
        
    except Exception as e:
        print(f"Error (get_total_game_count): {e}")
        return 0
    finally:
        if conn: conn.close()


def get_all_games(page=1, per_page=50, search_term="", sort_by="game_id", sort_order="ASC"): # <-- DEĞİŞTİ
    """Oyunları sayfalama, arama ve sıralama terimlerine göre listeler."""
    conn = db.get_connection()
    results_list = []
    
    offset = (page - 1) * per_page
    
    where_clause = ""
    query_params = []
    
    if search_term:
        search_like = f"%{search_term}%"
        search_cols = ["home_club_name", "away_club_name", "competition_id", "stadium"]
        where_conditions = [f"{col} LIKE %s" for col in search_cols]
        where_clause = " WHERE " + " OR ".join(where_conditions)
        query_params = [search_like] * len(search_cols)
        
    # Sıralama parametrelerini güvenli hale getir
    safe_sort_order = sort_order.upper() if sort_order.upper() in ["ASC", "DESC"] else "ASC" # <-- DEĞİŞTİ
    if sort_by not in GAME_COLUMNS:
        sort_by = "game_id" # <-- DEĞİŞTİ

    # LIMIT ve OFFSET parametrelerini en sona ekle
    query_params.extend([per_page, offset])

    try:
        cursor = conn.cursor()
        
        query = f"""
            SELECT {SELECT_FIELDS} FROM games
            {where_clause}
            ORDER BY {sort_by} {safe_sort_order}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, tuple(query_params))       
        results = cursor.fetchall()
        
        for row in results:
            try:
                obj = Games(**row) 
                results_list.append(obj)
            except TypeError as e:
                print(f"Model conversion error (Row skipped): {e}") 

        return results_list

    except Exception as e:
        print(f"Error (get_all_games): {e}")
        return []
    finally:
        if conn: conn.close()