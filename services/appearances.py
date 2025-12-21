from Database import db
from Models.Appearances import Appearances


APPEARANCE_COLUMNS = [
    'appearance_id', 'game_id', 'player_id', 'player_club_id', 'player_current_club_id',
    'date', 'player_name', 'competition_id', 'yellow_cards', 'red_cards',
    'assists', 'minutes_played'
]

SELECT_FIELDS = ', '.join(APPEARANCE_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(APPEARANCE_COLUMNS))


# ---(Read)---
def get_appearance(appearance_key):


    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM appearances WHERE appearance_id = %s"
        cursor.execute(query, (appearance_key,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return Appearances(*result)
        return None

    except Exception as e:
        print(f"Error (get_appearance): {e}")
        return None
    finally:
        if conn:
            conn.close()


# ---(Insert) ---
def insert_appearance(appearance_data: dict):

    conn = db.get_connection()
    try:
        cursor = conn.cursor()


        query = f"""
        INSERT INTO appearances ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        insert_values = [appearance_data.get(col) for col in APPEARANCE_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        new_id = appearance_data.get('appearance_id', cursor.lastrowid)

        conn.commit()
        cursor.close()
        return new_id

    except Exception as e:
        print(f"Error (create_appearance): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# ---(Delete)---
def delete_appearance(appearance_key):

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = "DELETE FROM appearances WHERE appearance_id = %s"
        cursor.execute(query, (appearance_key,))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected > 0

    except Exception as e:
        print(f"Error (delete_appearance): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# ---(Query/Search)---
def search_appearances_by_player(player_id):

    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()

        query = f"SELECT {SELECT_FIELDS} FROM appearances WHERE player_id = %s"
        cursor.execute(query, (player_id,))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(Appearances(*row))

        return results_list

    except Exception as e:
        print(f"Error (search_appearances): {e}")
        return []
    finally:
        if conn:
            conn.close()

# ---(List All)---
def get_total_appearance_count(search_term=""):
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        # Arama terimi varsa, toplam sayıyı da filtreleyerek hesaplamalıyız
        where_clause = ""
        query_params = []
        
        if search_term:
            search_like = f"%{search_term}%"
            search_cols = ["player_name", "appearance_id", "competition_id"]
            where_conditions = [f"{col} LIKE %s" for col in search_cols]
            where_clause = " WHERE " + " OR ".join(where_conditions)
            query_params = [search_like] * len(search_cols)

        query = f"SELECT COUNT(*) FROM appearances {where_clause}"
        cursor.execute(query, tuple(query_params))
        result = cursor.fetchone()
        
        # DictCursor kullandığımız için anahtarı 'COUNT(*)' olacaktır.
        return result['COUNT(*)'] if result else 0 
        
    except Exception as e:
        print(f"Error (get_total_appearance_count): {e}")
        return 0
    finally:
        if conn: conn.close()
def bulk_insert_appearances(appearances_list: list[dict]):
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        query = f"INSERT INTO appearances ({SELECT_FIELDS}) VALUES ({PLACEHOLDERS})"
        values_list = []
        for data in appearances_list:
            values_list.append(tuple(data.get(col) for col in APPEARANCE_COLUMNS))

        cursor.executemany(query, values_list)
        conn.commit()
        
        return cursor.rowcount 

    except Exception as e:
        print(f"Error (bulk_insert): {e}")
        return 0
    finally:
        if conn: conn.close()      

def get_appearances_by_date_range(start_date, end_date, player_id=None):
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        
        query = f"SELECT {SELECT_FIELDS} FROM appearances WHERE date BETWEEN %s AND %s"
        params = [start_date, end_date]

        if player_id:
            query += " AND player_id = %s"
            params.append(player_id)
            
        query += " ORDER BY date DESC"

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        
        for row in results:
            results_list.append(Appearances(*row))
            
        return results_list
    except Exception as e:
        print(f"Error (date_range): {e}")
        return []
    finally:
        if conn: conn.close()

# ---(Analytics)---
def get_player_season_stats(player_id, season_year=None):
    conn = db.get_connection()
    try:
        cursor = conn.cursor(dictionary=True) 
        query = """
            SELECT 
                COUNT(*) as total_matches,
                SUM(minutes_played) as total_minutes,
                SUM(assists) as total_assists,
                SUM(yellow_cards) as total_yellow,
                SUM(red_cards) as total_red,
                AVG(minutes_played) as avg_minutes
            FROM appearances 
            WHERE player_id = %s
        """
        cursor.execute(query, (player_id,))
        result = cursor.fetchone()
        return result

    except Exception as e:
        print(f"Error (get_player_season_stats): {e}")
        return None
    finally:
        if conn: conn.close()
        
# ---(Update)---
def update_appearance(appearance_id, update_data: dict):
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        fields = []
        values = []
        
        for key, value in update_data.items():
            if key in APPEARANCE_COLUMNS and key != 'appearance_id': 
                fields.append(f"{key} = %s")
                values.append(value)
        
        if not fields:
            return False 

        values.append(appearance_id) 
        
        query = f"UPDATE appearances SET {', '.join(fields)} WHERE appearance_id = %s"
        
        cursor.execute(query, tuple(values))
        conn.commit()
        
        return cursor.rowcount > 0

    except Exception as e:
        print(f"Error (update_appearance): {e}")
        return False
    finally:
        if conn: conn.close()

# --- Search and Pagination support for get_all_appearances ---
def get_all_appearances(page=1, per_page=50, search_term=""):
    conn = db.get_connection()
    results_list = []
    
    offset = (page - 1) * per_page
    
    where_clause = ""
    query_params = []
    
    if search_term:
        search_like = f"%{search_term}%"
        search_cols = ["player_name", "appearance_id", "competition_id"]
        where_conditions = [f"{col} LIKE %s" for col in search_cols]
        where_clause = " WHERE " + " OR ".join(where_conditions)
        query_params = [search_like] * len(search_cols)

    # Append LIMIT and OFFSET parameters to the end
    query_params.extend([per_page, offset])

    try:
        cursor = conn.cursor()
        
        query = f"""
            SELECT {SELECT_FIELDS} FROM appearances
            {where_clause}
            ORDER BY player_name ASC 
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, tuple(query_params))       
        results = cursor.fetchall()
        
        for row in results:
            try:
                # Assuming Appearances class handles all fields correctly
                obj = Appearances(**row)
                results_list.append(obj)
            except TypeError as e:
                # This should be checked and fixed if encountered!
                print(f"Model conversion error (Row skipped): {e}") 

        return results_list

    except Exception as e:
        print(f"Error (get_all_appearances): {e}")
        return []
    finally:
        if conn: conn.close()