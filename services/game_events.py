# File: services/game_events.py
# Description: Service layer for GameEvents model using players.py structure.

from Database import db
from Models.GameEvents import GameEvents

EVENT_COLUMNS = [
    'game_id', 'minute', 'type', 'club_id', 'player_id', 'description', 'player_in_id'
]

SELECT_FIELDS = ', '.join(EVENT_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(EVENT_COLUMNS))


def get_event(game_id, minute, event_type):
    """Tekil bir olay getirir (Primary key: game_id, minute, type)."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM game_events WHERE game_id=%s AND minute=%s AND type=%s"
        cursor.execute(query, (game_id, minute, event_type))
        result = cursor.fetchone()
        return GameEvents(**result) if result else None
    except Exception as e:
        print(f"Hata (get_event): {e}")
        return None
    finally:
        if conn: conn.close()


def get_total_event_count(search_term=""):
    """Toplam olay sayısını döndürür."""
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
        
        if isinstance(result, tuple):
            return result[0]
        elif isinstance(result, dict):
             return list(result.values())[0] if result else 0
        return 0
    except Exception as e:
        print(f"Hata: {e}")
        return 0
    finally:
        if conn: conn.close()


def get_all_events(page=1, per_page=50, search_term="", sort_by="game_id", sort_order="ASC"):
    """Tüm olayları listeler (Sayfalama ve Arama ile)."""
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

    safe_sort_order = "DESC" if sort_order.upper() == "DESC" else "ASC"
    if sort_by not in EVENT_COLUMNS: sort_by = "game_id"

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
                results_list.append(GameEvents(**row))
            except TypeError as e:
                print(f"Model hata: {e}")
        return results_list
    except Exception as e:
        print(f"Hata (get_all_events): {e}")
        return []
    finally:
        if conn: conn.close()


def insert_event(event_data: dict):
    """Yeni olay ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"INSERT INTO game_events ({SELECT_FIELDS}) VALUES ({PLACEHOLDERS})"
        values = [event_data.get(col) for col in EVENT_COLUMNS]
        cursor.execute(query, tuple(values))
        new_id = cursor.lastrowid 
        conn.commit()
        return new_id
    except Exception as e:
        print(f"Hata: {e}")
        return f"Error: {e}"
    finally:
        if conn: conn.close()


def update_event(game_id, minute, event_type, changes: dict):
    """Olayı günceller."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        valid_keys = [k for k in changes.keys() if k in EVENT_COLUMNS]
        if not valid_keys: return False

        set_clause = ", ".join([f"{key} = %s" for key in valid_keys])
        values = [changes[key] for key in valid_keys]
        values.extend([game_id, minute, event_type])

        query = f"UPDATE game_events SET {set_clause} WHERE game_id=%s AND minute=%s AND type=%s"
        cursor.execute(query, tuple(values))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Hata: {e}")
        return False
    finally:
        if conn: conn.close()


def delete_event(game_id, minute, event_type):
    """Olayı siler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = "DELETE FROM game_events WHERE game_id=%s AND minute=%s AND type=%s"
        cursor.execute(query, (game_id, minute, event_type))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Hata: {e}")
        return False
    finally:
        if conn: conn.close()


# --- ÖZEL ANALİTİK FONKSİYONLAR (Players.py Mantığıyla) ---

def get_events_by_player(player_id):
    """
    Belirli bir oyuncuya ait tüm olayları (Gol, Kart, Değişiklik) getirir.
    (Players.py'deki get_players_by_position mantığına benzer)
    """
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        # player_id veya player_in_id (oyuna giren) kontrol edilir
        query = f"""
            SELECT {SELECT_FIELDS} FROM game_events 
            WHERE player_id = %s OR player_in_id = %s
            ORDER BY game_id DESC, minute ASC
        """
        cursor.execute(query, (player_id, player_id))
        for row in cursor.fetchall():
            results_list.append(GameEvents(**row))
        return results_list
    except Exception as e:
        print(f"Hata (get_events_by_player): {e}")
        return []
    finally:
        if conn: conn.close()


def get_goals_by_game(game_id):
    """Bir maçtaki sadece 'Goals' türündeki olayları getirir."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM game_events WHERE game_id = %s AND type = 'Goals' ORDER BY minute ASC"
        cursor.execute(query, (game_id,))
        for row in cursor.fetchall():
            results_list.append(GameEvents(**row))
        return results_list
    except Exception as e:
        print(f"Hata: {e}")
        return []
    finally:
        if conn: conn.close()


def get_cards_by_game(game_id):
    """Bir maçtaki sadece 'Cards' türündeki olayları getirir."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM game_events WHERE game_id = %s AND type = 'Cards' ORDER BY minute ASC"
        cursor.execute(query, (game_id,))
        for row in cursor.fetchall():
            results_list.append(GameEvents(**row))
        return results_list
    except Exception as e:
        print(f"Hata: {e}")
        return []
    finally:
        if conn: conn.close()

def get_events_in_minute_range(min_minute, max_minute):
    """
    Belirli bir dakika aralığında (Örn: 80-90 arası) gerçekleşen olayları getirir.
    (Players.py'deki get_players_by_height_range mantığı)
    """
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        query = f"""
            SELECT {SELECT_FIELDS} FROM game_events 
            WHERE minute BETWEEN %s AND %s
            LIMIT 100
        """
        cursor.execute(query, (min_minute, max_minute))
        for row in cursor.fetchall():
            results_list.append(GameEvents(**row))
        return results_list
    except Exception as e:
        print(f"Hata: {e}")
        return []
    finally:
        if conn: conn.close()
