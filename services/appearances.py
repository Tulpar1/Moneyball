from Database import db
from Models.Appearances import Appearances


APPEARANCE_COLUMNS = [
    'appearance_id', 'game_id', 'player_id', 'player_club_id', 'player_current_club_id',
    'date', 'player_name', 'competition_id', 'yellow_cards', 'red_cards',
    'assist', 'minutes_played'
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