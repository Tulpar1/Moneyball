from Database import db
from Models.GameEvents import GameEvents

# GameEvents Sınıfının tüm alanlarını listeleyelim
EVENT_COLUMNS = [
    'game_id', 'minute', 'type', 'club_id', 'player_id', 'description', 'player_in_id'
]

SELECT_FIELDS = ', '.join(EVENT_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(EVENT_COLUMNS))

## GameEvents Veritabanı İşlemleri
# -----------------------------

# --- (Read) ---
def get_event(game_id, minute, event_type):
    """Belirtilen oyun (game_id), dakika ve tür (type) ile eşleşen olayı getirir."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM game_events WHERE game_id = %s AND minute = %s AND type = %s"
        cursor.execute(query, (game_id, minute, event_type))
        result = cursor.fetchone()
        cursor.close()

        if result:
            # DictCursor uyumu için **result kullanıldı
            return GameEvents(**result)
        return None

    except Exception as e:
        print(f"Error (get_event): {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- (Insert) ---
def insert_event(event_data: dict):
    """Yeni bir oyun olayını veritabanına ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO game_events ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        insert_values = [event_data.get(col) for col in EVENT_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        new_id = event_data.get('game_id', cursor.lastrowid) 

        conn.commit()
        cursor.close()
        return new_id

    except Exception as e:
        print(f"Error (insert_event): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Delete) ---
def delete_event(game_id, minute, event_type):
    """Belirtilen oyundaki (game_id, minute, type) olayı siler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = "DELETE FROM game_events WHERE game_id = %s AND minute = %s AND type = %s"
        cursor.execute(query, (game_id, minute, event_type))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected > 0 

    except Exception as e:
        print(f"Error (delete_event): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Query/Search) ---
def search_events_by_game(game_id):
    """Belirtilen oyuna ait tüm olayları (game_id) dakika sırasına göre getirir."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()

        query = f"""
        SELECT {SELECT_FIELDS} FROM game_events 
        WHERE game_id = %s
        ORDER BY minute ASC, type ASC
        """
        cursor.execute(query, (game_id,))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            # DictCursor uyumu için **row kullanıldı
            results_list.append(GameEvents(**row))

        return results_list

    except Exception as e:
        print(f"Error (search_events_by_game): {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- (List All with Pagination) ---
def get_total_event_count(search_term=""):
    """Filtrelenmiş veya tüm olayların toplam sayısını döndürür."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        where_clause = ""
        query_params = []
        
        if search_term:
            search_like = f"%{search_term}%"
            search_cols = ["type", "description"]
            where_conditions = [f"{col} LIKE %s" for col in search_cols]
            where_clause = " WHERE " + " OR ".join(where_conditions)
            query_params = [search_like] * len(search_cols)

        query = f"SELECT COUNT(*) FROM game_events {where_clause}"
        cursor.execute(query, tuple(query_params))
        result = cursor.fetchone()
        
        return result[0] if isinstance(result, tuple) else (result['COUNT(*)'] if result else 0)
        
    except Exception as e:
        print(f"Error (get_total_event_count): {e}")
        return 0
    finally:
        if conn: conn.close()


def get_all_events(page=1, per_page=50, search_term="", sort_by="game_id", sort_order="ASC"): # <-- DEĞİŞTİ
    """Oyun olaylarını sayfalama, arama ve sıralama terimlerine göre listeler."""
    conn = db.get_connection()
    results_list = []
    
    offset = (page - 1) * per_page
    
    where_clause = ""
    query_params = []
    
    if search_term:
        search_like = f"%{search_term}%"
        search_cols = ["type", "description"]
        where_conditions = [f"{col} LIKE %s" for col in search_cols]
        where_clause = " WHERE " + " OR ".join(where_conditions)
        query_params = [search_like] * len(search_cols)

    # Sıralama parametrelerini güvenli hale getir
    safe_sort_order = sort_order.upper() if sort_order.upper() in ["ASC", "DESC"] else "ASC" # <-- DEĞİŞTİ
    if sort_by not in EVENT_COLUMNS:
        sort_by = "game_id" # <-- DEĞİŞTİ
    
    # LIMIT ve OFFSET parametrelerini en sona ekle
    query_params.extend([per_page, offset])

    try:
        cursor = conn.cursor()
        
        query = f"""
            SELECT {SELECT_FIELDS} FROM game_events
            {where_clause}
            ORDER BY {sort_by} {safe_sort_order}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, tuple(query_params))       
        results = cursor.fetchall()
        
        for row in results:
            try:
                # DictCursor uyumu için **row kullanıldı
                obj = GameEvents(**row) 
                results_list.append(obj)
            except TypeError as e:
                print(f"Model conversion error (Row skipped): {e}") 

        return results_list

    except Exception as e:
        print(f"Error (get_all_events): {e}")
        return []
    finally:
        if conn: conn.close()