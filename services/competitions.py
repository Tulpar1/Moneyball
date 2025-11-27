from Database import db
from Models.Competitions import Competitions # 'Models.Competitions' varsayılıyor

# Competitions Sınıfının tüm alanlarını listeleyelim
COMPETITION_COLUMNS = [
    'competition_id', 'name', 'type', 'country_id', 'country_name', 
    'league_level', 'market_value_in_eur', 'num_clubs', 'num_players', 
    'last_update', 'url', 'domestic_league_code'
]

SELECT_FIELDS = ', '.join(COMPETITION_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(COMPETITION_COLUMNS))

## Competitions Veritabanı İşlemleri
# ----------------------------------

# --- (Read) ---
def get_competition(competition_id):
    """Belirtilen competition_id'ye sahip ligi/müsabakayı veritabanından getirir."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM competitions WHERE competition_id = %s"
        cursor.execute(query, (competition_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            # Result'u Models.Competitions sınıfına dönüştürerek döndür
            return Competitions(**result) 
        return None

    except Exception as e:
        print(f"Error (get_competition): {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- (Insert) ---
def insert_competition(competition_data: dict):
    """Yeni bir lig/müsabaka kaydını veritabanına ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO competitions ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        # Sözlükten sadece gerekli alanları al
        insert_values = [competition_data.get(col) for col in COMPETITION_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        # game_id gibi, competition_id'nin de data içinde olması veya lastrowid kullanılması
        new_id = competition_data.get('competition_id', cursor.lastrowid) 

        conn.commit()
        cursor.close()
        return new_id

    except Exception as e:
        print(f"Error (insert_competition): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Delete) ---
def delete_competition(competition_id):
    """Belirtilen competition_id'ye sahip ligi/müsabakayı veritabanından siler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = "DELETE FROM competitions WHERE competition_id = %s"
        cursor.execute(query, (competition_id,))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected > 0

    except Exception as e:
        print(f"Error (delete_competition): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Update) ---
def update_competition(competition_id, update_data: dict):
    """Belirtilen competition_id'ye ait ligin/müsabakanın verilerini günceller."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        set_clauses = []
        update_values = []

        if 'competition_id' in update_data:
            del update_data['competition_id'] # ID'yi güncellemeye izin verme

        for col, value in update_data.items():
            if col in COMPETITION_COLUMNS:
                set_clauses.append(f"{col} = %s")
                update_values.append(value)
        
        if not set_clauses:
            return 0 # Güncellenecek veri yok

        query = f"UPDATE competitions SET {', '.join(set_clauses)} WHERE competition_id = %s"
        update_values.append(competition_id)

        cursor.execute(query, tuple(update_values))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected

    except Exception as e:
        print(f"Error (update_competition): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# --- (Query/Search) ---

def get_competition_total_market_value(competition_id):
    """
    Bir ligdeki (Competition) tüm oyuncuların toplam piyasa değerini hesaplar.
    (Orijinal competitions.py dosyasındaki fonksiyon korunmuştur)
    """
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT c.name, SUM(p.market_value_in_eur) as total_value
            FROM competitions c
            JOIN clubs cl ON c.competition_id = cl.domestic_competition_id
            JOIN players p ON cl.club_id = p.current_club_id
            WHERE c.competition_id = %s
            GROUP BY c.name
        """
        cursor.execute(query, (competition_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error (get_competition_total_market_value): {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- (List All with Pagination) ---
def get_total_competition_count(search_term=""):
    """Filtrelenmiş veya tüm liglerin/müsabakaların toplam sayısını döndürür."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        where_clause = ""
        query_params = []
        
        if search_term:
            search_like = f"%{search_term}%"
            # Arama sütunları competitions tablosu için ayarlandı
            search_cols = ["name", "country_name", "domestic_league_code", "competition_id"]
            where_conditions = [f"{col} LIKE %s" for col in search_cols]
            where_clause = " WHERE " + " OR ".join(where_conditions)
            query_params = [search_like] * len(search_cols)

        query = f"SELECT COUNT(*) FROM competitions {where_clause}"
        cursor.execute(query, tuple(query_params))
        result = cursor.fetchone()
        
        # Sonuç formatı games.py'deki ile aynı tutulmuştur.
        return result[0] if isinstance(result, tuple) else (result['COUNT(*)'] if result else 0)
        
    except Exception as e:
        print(f"Error (get_total_competition_count): {e}")
        return 0
    finally:
        if conn: conn.close()


def get_all_competitions(page=1, per_page=50, search_term="", sort_by="competition_id", sort_order="ASC"):
    """Ligleri/müsabakaları sayfalama, arama ve sıralama terimlerine göre listeler."""
    conn = db.get_connection()
    results_list = []
    
    offset = (page - 1) * per_page
    
    where_clause = ""
    query_params = []
    
    if search_term:
        search_like = f"%{search_term}%"
        search_cols = ["name", "country_name", "domestic_league_code", "competition_id"]
        where_conditions = [f"{col} LIKE %s" for col in search_cols]
        where_clause = " WHERE " + " OR ".join(where_conditions)
        query_params = [search_like] * len(search_cols)
        
    # Sıralama parametrelerini güvenli hale getir
    safe_sort_order = sort_order.upper() if sort_order.upper() in ["ASC", "DESC"] else "ASC"
    if sort_by not in COMPETITION_COLUMNS:
        sort_by = "competition_id"

    # LIMIT ve OFFSET parametrelerini en sona ekle
    query_params.extend([per_page, offset])

    try:
        cursor = conn.cursor()
        
        query = f"""
            SELECT {SELECT_FIELDS} FROM competitions
            {where_clause}
            ORDER BY {sort_by} {safe_sort_order}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, tuple(query_params))       
        results = cursor.fetchall()
        
        for row in results:
            try:
                # Row'u Models.Competitions sınıfına dönüştürerek listeye ekle
                obj = Competitions(**row) 
                results_list.append(obj)
            except TypeError as e:
                print(f"Model conversion error (Row skipped): {e}") 

        return results_list

    except Exception as e:
        print(f"Error (get_all_competitions): {e}")
        return []
    finally:
        if conn: conn.close()
