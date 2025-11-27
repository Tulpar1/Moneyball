from Database import db
# Models klasöründe ClubGames adında bir class oluşturduğunu varsayıyorum
from Models.ClubGames import ClubGames 

CLUB_GAMES_COLUMNS = [
    'game_id', 'club_id', 'own_goals', 'own_position', 'own_manager_name',
    'opponent_id', 'opponent_goals', 'opponent_position', 'opponent_manager_name',
    'hosting', 'is_win'
]

SELECT_FIELDS = ', '.join(CLUB_GAMES_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(CLUB_GAMES_COLUMNS))


# ---(Read)---
# Club Games tablosunda bir satırı bulmak için hem maç id hem kulüp id gerekir
def get_club_game(game_id, club_id):

    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        # İki koşula göre arama yapıyoruz
        query = f"SELECT {SELECT_FIELDS} FROM club_games WHERE game_id = %s AND club_id = %s"
        cursor.execute(query, (game_id, club_id))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return ClubGames(*result)
        return None

    except Exception as e:
        print(f"Error (get_club_game): {e}")
        return None
    finally:
        if conn:
            conn.close()


# ---(Insert) ---
def insert_club_game(game_data: dict):

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO club_games ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        insert_values = [game_data.get(col) for col in CLUB_GAMES_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        conn.commit()
        cursor.close()
        return True # Başarılıysa True döner

    except Exception as e:
        print(f"Error (insert_club_game): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# ---(Delete)---
def delete_club_game(game_id, club_id):

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        # Silmek için de iki anahtarı kullanıyoruz
        query = "DELETE FROM club_games WHERE game_id = %s AND club_id = %s"
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


# ---(Query/Search)---
# Bir kulübe ait tüm maçları getirir
def search_games_by_club(club_id):

    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()

        query = f"SELECT {SELECT_FIELDS} FROM club_games WHERE club_id = %s"
        cursor.execute(query, (club_id,))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(ClubGames(*row))

        return results_list

    except Exception as e:
        print(f"Error (search_games_by_club): {e}")
        return []
    finally:
        if conn:
            conn.close()
