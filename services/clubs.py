from Database import db
from Models.Clubs import Clubs

# Clubs Sınıfının tüm alanlarını listeleyelim
CLUB_COLUMNS = [
    'club_id', 'club_code', 'name', 'domestic_competition_id',
    'total_market_value', 'squad_size', 'average_age', 'foreigners_number',
    'foreigners_percentage', 'national_team_players', 'stadium_name',
    'stadium_seats', 'net_transfer_record', 'coach_name', 'last_season', 'url'
]

SELECT_FIELDS = ', '.join(CLUB_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(CLUB_COLUMNS))
TABLE_NAME = "clubs" # Clubs tablosu varsayımı

## Clubs Veritabanı İşlemleri
# -----------------------------

# --- (Read) ---
def get_club(club_id):
    """Belirtilen club_id'ye sahip kulübü veritabanından getirir."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM {TABLE_NAME} WHERE club_id = %s"
        cursor.execute(query, (club_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return Clubs(**result)
        return None

    except Exception as e:
        print(f"Error (get_club): {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- (Insert) ---
def insert_club(club_data: dict):
    """Yeni bir kulüp kaydını veritabanına ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO {TABLE_NAME} ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        # Sadece tanımlanan sütunlara ait verileri al
        insert_values = [club_data.get(col) for col in CLUB_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        # Eğer club_id otomatik artan değilse, gönderilen ID'yi veya lastrowid'yi al
        new_id = club_data.get('club_id', cursor.lastrowid)

        conn.commit()
        cursor.close()
        return new_id

    except Exception as e:
        print(f"Error (insert_club): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Delete) ---
def delete_club(club_id):
    """Belirtilen club_id'ye sahip kulübü veritabanından siler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"DELETE FROM {TABLE_NAME} WHERE club_id = %s"
        cursor.execute(query, (club_id,))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected > 0

    except Exception as e:
        print(f"Error (delete_club): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Update) ---
def update_club(club_id, update_data: dict):
    """Belirtilen club_id'ye ait kulüp verilerini günceller."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        set_clauses = []
        update_values = []

        if 'club_id' in update_data:
            del update_data['club_id']

        for col, value in update_data.items():
            if col in CLUB_COLUMNS:
                set_clauses.append(f"{col} = %s")
                update_values.append(value)
        
        if not set_clauses:
            return 0

        query = f"UPDATE {TABLE_NAME} SET {', '.join(set_clauses)} WHERE club_id = %s"
        update_values.append(club_id)

        cursor.execute(query, tuple(update_values))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected

    except Exception as e:
        print(f"Error (update_club): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()

# --- (Query/Search by Competition) ---
def search_clubs_by_competition(competition_id):
    """Belirtilen lige (domestic_competition_id) ait tüm kulüpleri getirir."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()

        query = f"""
        SELECT {SELECT_FIELDS} FROM {TABLE_NAME} 
        WHERE domestic_competition_id = %s
        ORDER BY total_market_value DESC
        """
        cursor.execute(query, (competition_id,))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(Clubs(**row))

        return results_list

    except Exception as e:
        print(f"Error (search_clubs_by_competition): {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- (List All with Pagination) ---
def get_total_club_count(search_term=""):
    """Filtrelenmiş veya tüm kulüplerin toplam sayısını döndürür."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        where_clause = ""
        query_params = []
        
        if search_term:
            search_like = f"%{search_term}%"
            # Arama için uygun sütunlar: İsim, Stadyum, Menajer
            search_cols = ["name", "stadium_name", "coach_name", "domestic_competition_id"]
            where_conditions = [f"{col} LIKE %s" for col in search_cols]
            where_clause = " WHERE " + " OR ".join(where_conditions)
            query_params = [search_like] * len(search_cols)

        query = f"SELECT COUNT(*) FROM {TABLE_NAME} {where_clause}"
        cursor.execute(query, tuple(query_params))
        result = cursor.fetchone()
        
        return result[0] if isinstance(result, tuple) else (result['COUNT(*)'] if result else 0)
        
    except Exception as e:
        print(f"Error (get_total_club_count): {e}")
        return 0
    finally:
        if conn: conn.close()


def get_all_clubs(page=1, per_page=50, search_term="", sort_by="club_id", sort_order="ASC"):
    """Kulüpleri sayfalama, arama ve sıralama terimlerine göre listeler."""
    conn = db.get_connection()
    results_list = []
    
    offset = (page - 1) * per_page
    
    where_clause = ""
    query_params = []
    
    if search_term:
        search_like = f"%{search_term}%"
        search_cols = ["name", "stadium_name", "coach_name", "domestic_competition_id"]
        where_conditions = [f"{col} LIKE %s" for col in search_cols]
        where_clause = " WHERE " + " OR ".join(where_conditions)
        query_params = [search_like] * len(search_cols)
        
    # Sıralama parametrelerini güvenli hale getir
    safe_sort_order = sort_order.upper() if sort_order.upper() in ["ASC", "DESC"] else "ASC"
    if sort_by not in CLUB_COLUMNS:
        sort_by = "club_id"

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
                obj = Clubs(**row) 
                results_list.append(obj)
            except TypeError as e:
                print(f"Model conversion error (Row skipped): {e}") 

        return results_list

    except Exception as e:
        print(f"Error (get_all_clubs): {e}")
        return []
    finally:
        if conn: conn.close()