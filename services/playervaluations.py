from Database import db
from Models.PlayerValuations import PlayerValuations

# Tablo sütunları
VALUATION_COLUMNS = [
    'player_id', 'last_season', 'datetime', 'date', 'dateweek',
    'market_value_in_eur', 'n', 'current_club_id', 'player_club_domestic_competition_id'
]

SELECT_FIELDS = ', '.join(VALUATION_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(VALUATION_COLUMNS))


# ---(Read)---
# Bir oyuncunun tüm piyasa değeri geçmişini getirir (Tarihe göre sıralı)
def get_valuations_by_player_id(player_id):
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        # Tarihe göre tersten sıralıyoruz ki en güncel en üstte olsun
        query = f"SELECT {SELECT_FIELDS} FROM player_valuations WHERE player_id = %s ORDER BY date DESC"
        cursor.execute(query, (player_id,))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(PlayerValuations(*row))
            
        return results_list

    except Exception as e:
        print(f"Error (get_valuations_by_player_id): {e}")
        return []
    finally:
        if conn:
            conn.close()


# ---(Insert)---
def insert_valuation(val_data: dict):
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO player_valuations ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """
        
        insert_values = [val_data.get(col) for col in VALUATION_COLUMNS]
        
        cursor.execute(query, tuple(insert_values))
        conn.commit()
        cursor.close()
        
        return True # ID olmadığı için True dönüyoruz

    except Exception as e:
        print(f"Error (insert_valuation): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# ---(Delete)---
# Bir oyuncunun belirli bir tarihteki değer kaydını siler
def delete_valuation_entry(player_id, date):
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
        print(f"Error (delete_valuation_entry): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# ---(Query/Analytics)---
# Bir oyuncunun en yüksek piyasa değerini bulur (Hocanın seveceği tipte bir fonksiyon)
def get_max_market_value(player_id):
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        query = "SELECT MAX(market_value_in_eur) as max_val FROM player_valuations WHERE player_id = %s"
        cursor.execute(query, (player_id,))
        result = cursor.fetchone()
        cursor.close()

        return result['max_val'] if result and result['max_val'] else 0

    except Exception as e:
        print(f"Error (get_max_market_value): {e}")
        return 0
    finally:
        if conn:
            conn.close()
