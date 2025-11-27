from Database import db
from Models.GameEvents import GameEvents


GAME_EVENTS_COLUMNS = [
    'game_id', 'minute', 'type', 'club_id', 'player_id', 'description', 'player_in_id'
]

SELECT_FIELDS = ', '.join(GAME_EVENTS_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(GAME_EVENTS_COLUMNS))


# --- (Read) ---
def get_event(event_key):
    """Belirtilen game_id ve muhtemelen minute/type ile olayı veritabanından getirir. 
       (Not: GameEvents tablosunda birleşik anahtar gerekebilir.)"""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        # Bu tablo için birincil anahtar (PK) net olmadığı için sadece game_id ile arama yapıyoruz.
        query = f"SELECT {SELECT_FIELDS} FROM game_events WHERE game_id = %s LIMIT 1"
        cursor.execute(query, (event_key,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            # Modelin **kwargs almadığını varsayarak *args ile çağırıyoruz
            # Not: Diğer servisleriniz **kwargs aldığı için, burada da **result kullanmak daha güvenli olabilir.
            return GameEvents(*result) 
        return None

    except Exception as e:
        print(f"Error (get_event): {e}")
        return None
    finally:
        if conn:
            conn.close()


# --- (Insert) ---
def insert_game_event(event_data: dict):
    """Verilen sözlük verilerini kullanarak veritabanına yeni bir oyun olayı ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO game_events ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        # Sözlükten sütun sırasına göre değerleri alır
        insert_values = [event_data.get(col) for col in GAME_EVENTS_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        # Game_events tablosu genellikle otomatik artan bir ID'ye sahip değildir, 
        # bu yüzden başarıyı döndürürüz.
        new_id = event_data.get('game_id') 

        conn.commit()
        cursor.close()
        return new_id

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error (insert_game_event): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


# --- (List All) ---
def get_all_game_events(limit=100):
    """En son olayları (varsayılan: 100) getirir."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
                 
        query = f"SELECT {SELECT_FIELDS} FROM game_events ORDER BY game_id DESC, minute ASC LIMIT %s"
        cursor.execute(query, (limit,))      
        results = cursor.fetchall()
           
        for row in results:
            try:
                # KRİTİK NOKTA: Diğer çalışan servislerinizde **row kullandığınız için, burada da aynı yöntemi kullanıyoruz.
                obj = GameEvents(**row)
                results_list.append(obj)
            except Exception as e:
                # Veritabanından gelen veri formatı (sıra/sözlük) modelin beklentisini karşılamıyorsa hata verir.
                print(f"Error (GameEvents Model Conversion): {e}")
                
        return results_list

    except Exception as e:
        print(f"Error (get_all_game_events): {e}")
        return []
    finally:
        if conn:
            conn.close()