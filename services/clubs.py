from Database import db
# Models klasöründe Clubs adında bir class oluşturduğunu varsayıyorum
from Models.Clubs import Clubs 

CLUB_COLUMNS = [
    'club_id', 'club_code', 'name', 'domestic_competition_id', 'total_market_value',
    'squad_size', 'average_age', 'foreigners_number', 'foreigners_percentage',
    'national_team_players', 'stadium_name', 'stadium_seats', 'net_transfer_record',
    'coach_name', 'last_season', 'url'
]

SELECT_FIELDS = ', '.join(CLUB_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(CLUB_COLUMNS))


# ---(Read)---
# Kulüp ID'sine göre tek bir kulüp getirir
def get_club(club_id):

    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM clubs WHERE club_id = %s"
        cursor.execute(query, (club_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return Clubs(*result)
        return None

    except Exception as e:
        print(f"Error (get_club): {e}")
        return None
    finally:
        if conn:
            conn.close()


# ---(Insert) ---
def insert_club(club_data: dict):

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO clubs ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        insert_values = [club_data.get(col) for col in CLUB_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        # Eğer club_id verilmediyse ve auto-increment ise lastrowid kullanılır
        # Ancak senin tablonda club_id manuel veriliyor gibi görünüyor,
        # o yüzden veri içinden gelen ID'yi döndürüyoruz.
        new_id = club_data.get('club_id')

        conn.commit()
        cursor.close()
        return new_id

    except Exception as e:
        print(f"Error (insert_club): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# ---(Delete)---
def delete_club(club_id):

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = "DELETE FROM clubs WHERE club_id = %s"
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


# ---(Query/Search)---
# Kulüp ismine göre arama yapar (Örn: "Galatasaray" yazınca bulur)
def search_clubs_by_name(club_name):

    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        
        # % işareti ile "LIKE" araması yapıyoruz (içinde geçen kelimeyi bulur)
        query = f"SELECT {SELECT_FIELDS} FROM clubs WHERE name LIKE %s"
        search_term = f"%{club_name}%"
        
        cursor.execute(query, (search_term,))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(Clubs(*row))

        return results_list

    except Exception as e:
        print(f"Error (search_clubs_by_name): {e}")
        return []
    finally:
        if conn:
            conn.close()