from Database import db
from Models.Games import Games # Bu modelin oluşturulduğunu varsayıyoruz


GAMES_COLUMNS = [
    'game_id', 'competition_id', 'season', 'round', 'date', 'home_club_id', 
    'away_club_id', 'home_club_goals', 'away_club_goals', 'home_club_position', 
    'away_club_position', 'home_club_manager_name', 'away_club_manager_name', 
    'stadium', 'attendance', 'referee', 'url', 'home_club_name', 
    'away_club_name', 'aggregate', 'competition_type'
]

SELECT_FIELDS = ', '.join(GAMES_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(GAMES_COLUMNS))


# --- (Read) ---
def get_game(game_key):
    """Belirtilen game_id'ye sahip oyunu veritabanından getirir."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM games WHERE game_id = %s"
        cursor.execute(query, (game_key,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            # result, Games modelinin __init__ metoduna doğrudan gönderilir.
            return Games(*result)
        return None

    except Exception as e:
        print(f"Error (get_game): {e}")
        return None
    finally:
        if conn:
            conn.close()


# --- (Insert) ---
def insert_game(game_data: dict):
    """Verilen sözlük verilerini kullanarak veritabanına yeni bir oyun kaydı ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO games ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        # Sözlükten sütun sırasına göre değerleri alır
        insert_values = [game_data.get(col) for col in GAMES_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        # Eğer game_id sözlükte yoksa, veritabanının son eklenen kimliğini (lastrowid) kullanmayı dener.
        # Ancak, game_id genellikle birincil anahtar (Primary Key) olarak manuel olarak atanır.
        new_id = game_data.get('game_id', cursor.lastrowid)

        conn.commit()
        cursor.close()
        return new_id

    except Exception as e:
        # Hata durumunda işlemi geri alır ve hatayı yazdırır
        if conn:
            conn.rollback()
        print(f"Error (insert_game): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# --- (Delete) ---
def delete_game(game_key):
    """Belirtilen game_id'ye sahip oyunu veritabanından siler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = "DELETE FROM games WHERE game_id = %s"
        cursor.execute(query, (game_key,))

        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected > 0 # Silme başarılıysa True, değilse False döner

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error (delete_game): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# --- (Query/Search) ---
def search_games_by_club(club_id):
    """Belirtilen club_id'nin hem ev sahibi hem de deplasman kulübü olduğu oyunları arar."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()

        # Ev sahibi veya deplasman kulübü ID'si ile arama yapılır
        query = f"""
        SELECT {SELECT_FIELDS} FROM games 
        WHERE home_club_id = %s OR away_club_id = %s
        ORDER BY date DESC
        """
        cursor.execute(query, (club_id, club_id))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(Games(*row))

        return results_list

    except Exception as e:
        print(f"Error (search_games_by_club): {e}")
        return []
    finally:
        if conn:
            conn.close()


# --- (List All) ---
# services/games.py (Güncel Versiyon)

# ... (dosyanın başındaki import'lar ve GAMES_COLUMNS listesi aynı kalmalı)

# --- (List All) ---
# services/games.py dosyasına bu fonksiyonu kopyalayın

# --- (List All) ---
def get_all_games(limit=100):
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
                 
        query = f"SELECT {SELECT_FIELDS} FROM games ORDER BY date DESC LIMIT %s"
        cursor.execute(query, (limit,))      
        results = cursor.fetchall()
        
        # Eğer DictCursor kullanıyorsanız ve sonuçta sözlükler geliyorsa:
        for row in results:
            try:
                # KRİTİK DEĞİŞİKLİK: Çalışan appearances gibi **row ile sözlük kullanıyoruz
                obj = Games(**row) 
                results_list.append(obj)
            except TypeError as e:
                # Modelin eksik/fazla anahtar kelime alması durumunda hata ayıklama
                print("-" * 50)
                print(f"KRİTİK HATA: Games model dönüşümünde anahtar kelime hatası (TypeError): {e}")
                print(f"Hata sebebi: Veritabanı sütun adları ile Games modelindeki init parametre adları uyuşmuyor.")
                print("-" * 50)
                return []
            except Exception as e:
                print(f"Bilinmeyen Model Oluşturma Hatası: {e}")
                return []

        return results_list

    except Exception as e:
        print(f"Error (get_all_games): SQL Sorgu veya Bağlantı Hatası: {e}")
        return []
    finally:
        if conn:
            conn.close()