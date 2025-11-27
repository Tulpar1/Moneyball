from Database import db
from Models.PlayerValuations import PlayerValuations # 'Models.PlayerValuations' varsayılıyor

# PlayerValuations Sınıfının tüm alanlarını listeleyelim
PLAYER_VALUATION_COLUMNS = [
    'player_id', 'last_season', 'datetime', 'date', 'dateweek',
    'market_value_in_eur', 'n', 'current_club_id',
    'player_club_domestic_competition_id'
]

SELECT_FIELDS = ', '.join(PLAYER_VALUATION_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(PLAYER_VALUATION_COLUMNS))

# Varsayım: PlayerValuations tablosunun birincil anahtarı (Primary Key) 
# 'player_id' ve 'date' kombinasyonudur, çünkü bir oyuncunun birden 
# fazla tarihte piyasa değeri olabilir.

## PlayerValuations Veritabanı İşlemleri
# -------------------------------------

# --- (Read) ---
def get_valuation(player_id, date):
    """
    Belirtilen player_id ve tarihe (date) sahip oyuncu piyasa değeri kaydını 
    veritabanından getirir.
    """
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"""
        SELECT {SELECT_FIELDS} FROM player_valuations 
        WHERE player_id = %s AND date = %s
        """
        cursor.execute(query, (player_id, date))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return PlayerValuations(**result) 
        return None

    except Exception as e:
        print(f"Error (get_valuation): {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- (Insert) ---
def insert_valuation(valuation_data: dict):
    """Yeni bir oyuncu piyasa değeri kaydını veritabanına ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO player_valuations ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        insert_values = [valuation_data.get(col) for col in PLAYER_VALUATION_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        # Piyasa değerlerinin kendi unique ID'si olmayabilir, 
        # bu nedenle sadece başarılı ekleme onayı dönebiliriz.
        conn.commit()
        cursor.close()
        return True # Başarı göstergesi

    except Exception as e:
        print(f"Error (insert_valuation): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Delete) ---
def delete_valuation(player_id, date):
    """Belirtilen player_id ve tarihe sahip piyasa değeri kaydını siler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = "DELETE FROM player_valuations WHERE player_id = %s AND date = %s"
        cursor.execute(query, (player_id, date))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected > 0

    except Exception as e:
        print(f"Error (delete_valuation): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Update) ---
def update_valuation(player_id, date, update_data: dict):
    """Belirtilen kayda ait verileri günceller."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        set_clauses = []
        update_values = []

        # Primary Key (player_id ve date) güncellemeye dahil edilmez.
        if 'player_id' in update_data: del update_data['player_id']
        if 'date' in update_data: del update_data['date']

        for col, value in update_data.items():
            if col in PLAYER_VALUATION_COLUMNS:
                set_clauses.append(f"{col} = %s")
                update_values.append(value)
        
        if not set_clauses:
            return 0 # Güncellenecek veri yok

        query = f"""
        UPDATE player_valuations 
        SET {', '.join(set_clauses)} 
        WHERE player_id = %s AND date = %s
        """
        # WHERE koşulu için player_id ve date eklenir
        update_values.extend([player_id, date]) 

        cursor.execute(query, tuple(update_values))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected

    except Exception as e:
        print(f"Error (update_valuation): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# --- (Query/Search) ---

def get_valuations_by_player(player_id):
    """Belirtilen oyuncuya ait tüm piyasa değeri geçmişini getirir."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()

        query = f"""
        SELECT {SELECT_FIELDS} FROM player_valuations 
        WHERE player_id = %s 
        ORDER BY date DESC
        """
        cursor.execute(query, (player_id,))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(PlayerValuations(**row))

        return results_list

    except Exception as e:
        print(f"Error (get_valuations_by_player): {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- (List All with Pagination) ---
def get_total_valuation_count(search_term=""):
    """Filtrelenmiş veya tüm piyasa değeri kayıtlarının toplam sayısını döndürür."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        where_clause = ""
        query_params = []
        
        if search_term:
            search_like = f"%{search_term}%"
            # Arama sütunları piyasa değeri tablosu için ayarlandı (Örn: player_id, current_club_id)
            search_cols = ["player_id", "current_club_id", "player_club_domestic_competition_id"]
            where_conditions = [f"{col} LIKE %s" for col in search_cols]
            where_clause = " WHERE " + " OR ".join(where_conditions)
            query_params = [search_like] * len(search_cols)

        query = f"SELECT COUNT(*) FROM player_valuations {where_clause}"
        cursor.execute(query, tuple(query_params))
        result = cursor.fetchone()
        
        return result[0] if isinstance(result, tuple) else (result['COUNT(*)'] if result else 0)
        
    except Exception as e:
        print(f"Error (get_total_valuation_count): {e}")
        return 0
    finally:
        if conn: conn.close()


def get_all_valuations(page=1, per_page=50, search_term="", sort_by="date", sort_order="DESC"):
    """Piyasa değeri kayıtlarını sayfalama, arama ve sıralama terimlerine göre listeler."""
    conn = db.get_connection()
    results_list = []
    
    offset = (page - 1) * per_page
    
    where_clause = ""
    query_params = []
    
    if search_term:
        search_like = f"%{search_term}%"
        search_cols = ["player_id", "current_club_id", "player_club_domestic_competition_id"]
        where_conditions = [f"{col} LIKE %s" for col in search_cols]
        where_clause = " WHERE " + " OR ".join(where_conditions)
        query_params = [search_like] * len(search_cols)
        
    # Sıralama parametrelerini güvenli hale getir
    safe_sort_order = sort_order.upper() if sort_order.upper() in ["ASC", "DESC"] else "DESC" # Varsayılan: En yeni ilk
    if sort_by not in PLAYER_VALUATION_COLUMNS:
        sort_by = "date"

    # LIMIT ve OFFSET parametrelerini en sona ekle
    query_params.extend([per_page, offset])

    try:
        cursor = conn.cursor()
        
        query = f"""
            SELECT {SELECT_FIELDS} FROM player_valuations
            {where_clause}
            ORDER BY {sort_by} {safe_sort_order}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, tuple(query_params))       
        results = cursor.fetchall()
        
        for row in results:
            try:
                obj = PlayerValuations(**row) 
                results_list.append(obj)
            except TypeError as e:
                print(f"Model conversion error (Row skipped): {e}") 

        return results_list

    except Exception as e:
        print(f"Error (get_all_valuations): {e}")
        return []
    finally:
        if conn: conn.close()