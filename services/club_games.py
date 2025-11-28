from Database import db
from Models.ClubGames import ClubGames

# ClubGames Sınıfının tüm alanlarını listeleyelim
CLUB_GAME_COLUMNS = [
    'game_id', 'club_id', 'own_goals', 'own_position', 'own_manager_name',
    'opponent_id', 'opponent_goals', 'opponent_position', 'opponent_manager_name',
    'hosting', 'is_win'
]

# Arama için kullanılabilecek sütunlar
SEARCHABLE_CLUB_GAME_COLUMNS = ["own_manager_name", "opponent_manager_name", "opponent_id", "hosting"]

SELECT_FIELDS = ', '.join(CLUB_GAME_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(CLUB_GAME_COLUMNS))
TABLE_NAME = "club_games" # Bağımsız club_games tablosu varsayımı

## ClubGames Veritabanı İşlemleri
# ----------------------------------------

# --- (Read) ---
def get_club_game(game_id, club_id):
    """Belirtilen game_id ve club_id'ye sahip kulüp oyununu veritabanından getirir."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM {TABLE_NAME} WHERE game_id = %s AND club_id = %s"
        cursor.execute(query, (game_id, club_id))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return ClubGames(**result)
        return None

    except Exception as e:
        print(f"Error (get_club_game): {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- (Insert) ---
def insert_club_game(club_game_data: dict):
    """Yeni bir kulüp oyun kaydını veritabanına ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO {TABLE_NAME} ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        insert_values = [club_game_data.get(col) for col in CLUB_GAME_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        new_keys = (club_game_data.get('game_id'), club_game_data.get('club_id'))

        conn.commit()
        cursor.close()
        return new_keys

    except Exception as e:
        print(f"Error (insert_club_game): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Delete) ---
def delete_club_game(game_id, club_id):
    """Belirtilen game_id ve club_id'ye sahip kaydı veritabanından siler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"DELETE FROM {TABLE_NAME} WHERE game_id = %s AND club_id = %s"
        cursor.execute(query, (game_id, club_id))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected > 0

    except Exception as e:
        print(f"Error (delete_club_game): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Update) ---
def update_club_game(game_id, club_id, update_data: dict):
    """Belirtilen game_id ve club_id'ye ait kaydı günceller."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        set_clauses = []
        update_values = []

        if 'game_id' in update_data: del update_data['game_id']
        if 'club_id' in update_data: del update_data['club_id']


        for col, value in update_data.items():
            if col in CLUB_GAME_COLUMNS:
                set_clauses.append(f"{col} = %s")
                update_values.append(value)
        
        if not set_clauses:
            return 0

        query = f"UPDATE {TABLE_NAME} SET {', '.join(set_clauses)} WHERE game_id = %s AND club_id = %s"
        
        update_values.extend([game_id, club_id])

        cursor.execute(query, tuple(update_values))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected

    except Exception as e:
        print(f"Error (update_club_game): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# --- (Query/Search) ---
def search_all_club_games_by_club(club_id):
    """Belirtilen kulübün (club_id) tüm maç kayıtlarını getirir."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()

        query = f"""
        SELECT {SELECT_FIELDS} FROM {TABLE_NAME}
        WHERE club_id = %s
        ORDER BY game_id DESC
        """
        cursor.execute(query, (club_id,))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(ClubGames(**row))

        return results_list

    except Exception as e:
        print(f"Error (search_all_club_games_by_club): {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- (List All with Pagination) ---
def get_total_club_game_count(search_term=""):
    """Filtrelenmiş veya tüm ClubGames kayıtlarının toplam sayısını döndürür."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        where_clause = ""
        query_params = []
        
        if search_term:
            search_like = f"%{search_term}%"
            search_cols = SEARCHABLE_CLUB_GAME_COLUMNS
            where_conditions = [f"{col} LIKE %s" for col in search_cols]
            where_clause = " WHERE " + " OR ".join(where_conditions)
            query_params = [search_like] * len(search_cols)

        query = f"SELECT COUNT(*) FROM {TABLE_NAME} {where_clause}"
        cursor.execute(query, tuple(query_params))
        result = cursor.fetchone()
        
        return result[0] if isinstance(result, tuple) else (result['COUNT(*)'] if result else 0)
        
    except Exception as e:
        print(f"Error (get_total_club_game_count): {e}")
        return 0
    finally:
        if conn: conn.close()


def get_all_club_games(page=1, per_page=50, search_term="", sort_by="game_id", sort_order="ASC"):
    """ClubGames kayıtlarını sayfalama, arama ve sıralama terimlerine göre listeler."""
    conn = db.get_connection()
    results_list = []
    
    offset = (page - 1) * per_page
    
    where_clause = ""
    query_params = []
    
    if search_term:
        search_like = f"%{search_term}%"
        search_cols = SEARCHABLE_CLUB_GAME_COLUMNS
        where_conditions = [f"{col} LIKE %s" for col in search_cols]
        where_clause = " WHERE " + " OR ".join(where_conditions)
        query_params = [search_like] * len(search_cols)
        
    # Sıralama parametrelerini güvenli hale getir
    safe_sort_order = sort_order.upper() if sort_order.upper() in ["ASC", "DESC"] else "ASC"
    if sort_by not in CLUB_GAME_COLUMNS:
        sort_by = "game_id"

    # LIMIT ve OFFSET parametrelerini en sona ekle
    query_params.extend([per_page, offset])

    try:
        cursor = conn.cursor()
        
        query = f"""
            SELECT {SELECT_FIELDS} FROM {TABLE_NAME}
            {where_clause}
            ORDER BY {sort_by} {safe_sort_order}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, tuple(query_params))       
        results = cursor.fetchall()
        
        for row in results:
            try:
                obj = ClubGames(**row) 
                results_list.append(obj)
            except TypeError as e:
                print(f"Model conversion error (Row skipped): {e}") 

        return results_list

    except Exception as e:
        print(f"Error (get_all_club_games): {e}")
        return []
    finally:
        if conn: conn.close()