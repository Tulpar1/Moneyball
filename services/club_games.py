from Database import db
from Models.ClubGames import ClubGames

# ClubGames Sınıfının tüm alanlarını listeleyelim
CLUB_GAME_COLUMNS = [
    'game_id', 'club_id', 'own_goals', 'own_position', 'own_manager_name',
    'opponent_id', 'opponent_goals', 'opponent_position', 'opponent_manager_name',
    'hosting', 'is_win'
]

# Arama için kullanılabilecek sütunlar
SEARCHABLE_CLUB_GAME_COLUMNS = ["own_manager_name", "opponent_manager_name", "opponent_id", "hosting"]

SELECT_FIELDS = ', '.join(CLUB_GAME_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(CLUB_GAME_COLUMNS))
TABLE_NAME = "club_games" 

## ClubGames Veritabanı İşlemleri
# ----------------------------------------

# --- (Read) ---
def get_club_game(game_id, club_id):
    """Belirtilen game_id ve club_id'ye sahip kulüp oyununu veritabanından getirir."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = f"SELECT {SELECT_FIELDS} FROM {TABLE_NAME} WHERE game_id = %s AND club_id = %s"
        cursor.execute(query, (game_id, club_id))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return ClubGames(**result)
        return None

    except Exception as e:
        print(f"Error (get_club_game): {e}")
        return None
    finally:
        if conn: conn.close()

# --- (Insert) ---
def insert_club_game(club_game_data: dict):
    """Yeni bir kulüp oyun kaydını veritabanına ekler."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        query = f"""
        INSERT INTO {TABLE_NAME} ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        insert_values = [club_game_data.get(col) for col in CLUB_GAME_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        new_keys = (club_game_data.get('game_id'), club_game_data.get('club_id'))

        conn.commit()
        cursor.close()
        return new_keys

    except Exception as e:
        print(f"Error (insert_club_game): {e}")
        return f"Error: {e}"
    finally:
        if conn: conn.close()

# --- (Delete) ---

def delete_club_game(game_id):
    """
    Belirtilen game_id'ye sahip kayıtları silmeye çalışır.
    Eğer başka tablolarda (örn: game_events, appearances) bu maça ait veri varsa,
    SQL'in vereceği hatayı yakalayıp kullanıcıya döndürür.
    """
    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        # BURASI ÖNEMLİ:
        # Eğer "game_events" veya "appearances" gibi tabloların varsa,
        # önce onları silmen gerekir. Örnek olarak yorum satırına ekliyorum:
        # cursor.execute("DELETE FROM game_events WHERE game_id = %s", (game_id,))
        # cursor.execute("DELETE FROM appearances WHERE game_id = %s", (game_id,))
        
        # Asıl silme işlemi
        query = f"DELETE FROM {TABLE_NAME} WHERE game_id = %s"
        cursor.execute(query, (game_id,))

        rows_affected = cursor.rowcount
        conn.commit()
        cursor.close()

        if rows_affected > 0:
            return True, f"Maç başarıyla silindi. (Silinen kayıt: {rows_affected})"
        else:
            return False, "Silinecek kayıt bulunamadı (ID yanlış olabilir)."

    except Exception as e:
        # Hatayı konsola yazdır
        print(f"SQL Hatası: {e}")
        
        # Hatayı string'e çevir
        error_msg = str(e)
        
        # Kullanıcı dostu ipuçları ekle
        if "foreign key constraint fails" in error_msg.lower():
            return False, f"BU MAÇ SİLİNEMİYOR ÇÜNKÜ BAĞLI VERİLER VAR.<br><br><b>Teknik Hata:</b> {error_msg}<br><br><b>Çözüm:</b> Bu maçı silmeden önce, bu maça ait golleri veya oyuncu istatistiklerini silmelisiniz."
        
        return False, f"Bir hata oluştu: {error_msg}"
    finally:
        if conn: conn.close()
# --- (Update) ---
def update_club_game(game_id, club_id, update_data: dict):
    """
    Belirtilen maç (game_id) ve kulüp (club_id) çiftine ait kaydı günceller.
    """
    if not update_data:
        return 0

    conn = db.get_connection()
    try:
        cursor = conn.cursor()

        set_clauses = []
        update_values = []

        # Anahtar kolonları güncelleme verisinden çıkar
        if 'game_id' in update_data: del update_data['game_id']
        if 'club_id' in update_data: del update_data['club_id']

        for col, value in update_data.items():
            if col in CLUB_GAME_COLUMNS:
                set_clauses.append(f"{col} = %s")
                update_values.append(value)
        
        if not set_clauses:
            return 0

        query = f"UPDATE {TABLE_NAME} SET {', '.join(set_clauses)} WHERE game_id = %s AND club_id = %s"
        update_values.extend([game_id, club_id])

        cursor.execute(query, tuple(update_values))
        rows_affected = cursor.rowcount

        conn.commit()
        cursor.close()
        return rows_affected

    except Exception as e:
        print(f"Error (update_club_game): {e}")
        return f"Error: {e}"
    finally:
        if conn: conn.close()

# --- (Query/Search) ---
def search_all_club_games_by_club(club_id):
    """Belirtilen kulübün (club_id) tüm maç kayıtlarını getirir."""
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()

        query = f"""
        SELECT {SELECT_FIELDS} FROM {TABLE_NAME}
        WHERE club_id = %s
        ORDER BY game_id DESC
        """
        cursor.execute(query, (club_id,))
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            results_list.append(ClubGames(**row))

        return results_list

    except Exception as e:
        print(f"Error (search_all_club_games_by_club): {e}")
        return []
    finally:
        if conn: conn.close()

# --- (List All with Pagination) ---
def get_total_club_game_count(search_term=""):
    """Filtrelenmiş veya tüm ClubGames kayıtlarının toplam sayısını döndürür."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        
        where_clause = ""
        query_params = []
        
        if search_term:
            search_like = f"%{search_term}%"
            search_cols = SEARCHABLE_CLUB_GAME_COLUMNS
            where_conditions = [f"{col} LIKE %s" for col in search_cols]
            where_clause = " WHERE " + " OR ".join(where_conditions)
            query_params = [search_like] * len(search_cols)

        query = f"SELECT COUNT(*) FROM {TABLE_NAME} {where_clause}"
        cursor.execute(query, tuple(query_params))
        result = cursor.fetchone()
        
        return result[0] if isinstance(result, tuple) else (result['COUNT(*)'] if result else 0)
        
    except Exception as e:
        print(f"Error (get_total_club_game_count): {e}")
        return 0
    finally:
        if conn: conn.close()

def get_all_club_games(page=1, per_page=50, search_term="", sort_by="game_id", sort_order="ASC"):
    """
    ClubGames kayıtlarını listeler. 
    YENİLİK: Artık 'clubs' tablosuna JOIN atarak Takım İsimlerini de getiriyor.
    """
    conn = db.get_connection()
    results_list = []
    
    offset = (page - 1) * per_page
    
    # Varsayılan sıralama sütunu kontrolü
    if sort_by not in CLUB_GAME_COLUMNS and sort_by not in ['club_name', 'opponent_name']:
        sort_by = "cg.game_id"
    elif sort_by in CLUB_GAME_COLUMNS:
        # Tablo alias'ı ekleyelim ki karışıklık olmasın (cg = club_games)
        sort_by = f"cg.{sort_by}"

    safe_sort_order = sort_order.upper() if sort_order.upper() in ["ASC", "DESC"] else "ASC"

    # Arama Filtresi
    where_clause = ""
    query_params = []
    if search_term:
        search_like = f"%{search_term}%"
        # Hem menajer isminde hem de TAKIM İSMİNDE arama yapabilsin
        where_clause = """
        WHERE (cg.own_manager_name LIKE %s 
           OR cg.opponent_manager_name LIKE %s 
           OR c1.name LIKE %s 
           OR c2.name LIKE %s)
        """
        query_params = [search_like, search_like, search_like, search_like]

    query_params.extend([per_page, offset])

    try:
        cursor = conn.cursor()
        
        # SQL JOIN SORGUSU
        # c1: Kendi kulübümüz, c2: Rakip kulüp
        query = f"""
            SELECT 
                cg.game_id, cg.club_id, cg.own_goals, cg.own_position, cg.own_manager_name,
                cg.opponent_id, cg.opponent_goals, cg.opponent_position, cg.opponent_manager_name,
                cg.hosting, cg.is_win,
                c1.name as club_name,       -- Kendi kulüp ismimiz
                c2.name as opponent_name    -- Rakip kulüp ismi
            FROM {TABLE_NAME} cg
            LEFT JOIN clubs c1 ON cg.club_id = c1.club_id
            LEFT JOIN clubs c2 ON cg.opponent_id = c2.club_id
            {where_clause}
            ORDER BY {sort_by} {safe_sort_order}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, tuple(query_params))       
        results = cursor.fetchall()
        
        for row in results:
            
            if isinstance(row, dict):
                obj = ClubGames(**row)
            else:
            
                obj = ClubGames(*row) 
                
            results_list.append(obj)

        return results_list

    except Exception as e:
        print(f"Error (get_all_club_games JOIN): {e}")
        return []
    finally:
        if conn: conn.close()
# --- ANALIZ FONKSIYONLARI ---

def get_games_by_manager(manager_name):
    """
    Verilen teknik direktör ismine sahip maçları getirir.
    """
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        query = f"""
        SELECT {SELECT_FIELDS} FROM {TABLE_NAME}
        WHERE own_manager_name LIKE %s
        ORDER BY game_id DESC
        """
        cursor.execute(query, (f"%{manager_name}%",))
        results = cursor.fetchall()
        
        for row in results:
            results_list.append(ClubGames(**row))
            
        return results_list
    except Exception as e:
        print(f"Error (get_games_by_manager): {e}")
        return []
    finally:
        if conn: conn.close()

def get_club_wins(club_id):
    """
    Belirtilen kulübün kazandığı maçları getirir.
    """
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        query = f"""
        SELECT {SELECT_FIELDS} FROM {TABLE_NAME}
        WHERE club_id = %s AND is_win = 1
        ORDER BY game_id DESC
        """
        cursor.execute(query, (club_id,))
        results = cursor.fetchall()
        
        for row in results:
            results_list.append(ClubGames(**row))
            
        return results_list
    except Exception as e:
        print(f"Error (get_club_wins): {e}")
        return []
    finally:
        if conn: conn.close()

def get_high_scoring_games(min_goals=3):
    """
    Belirli bir gol sayısının üzerindeki maçları getirir.
    """
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        query = f"""
        SELECT {SELECT_FIELDS} FROM {TABLE_NAME}
        WHERE own_goals >= %s
        ORDER BY own_goals DESC
        """
        cursor.execute(query, (min_goals,))
        results = cursor.fetchall()
        
        for row in results:
            results_list.append(ClubGames(**row))
            
        return results_list
    except Exception as e:
        print(f"Error (get_high_scoring_games): {e}")
        return []
    finally:
        if conn: conn.close()

def get_head_to_head(club_id_1, club_id_2):
    """
    İki takım arasındaki maçları getirir.
    """
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        query = f"""
        SELECT {SELECT_FIELDS} FROM {TABLE_NAME}
        WHERE club_id = %s AND opponent_id = %s
        ORDER BY game_id DESC
        """
        cursor.execute(query, (club_id_1, club_id_2))
        results = cursor.fetchall()
        
        for row in results:
            results_list.append(ClubGames(**row))
            
        return results_list
    except Exception as e:
        print(f"Error (get_head_to_head): {e}")
        return []
    finally:
        if conn: conn.close()

def get_clean_sheets(club_id):
    """
    Kulübün gol yemediği maçları getirir.
    """
    conn = db.get_connection()
    results_list = []
    try:
        cursor = conn.cursor()
        query = f"""
        SELECT {SELECT_FIELDS} FROM {TABLE_NAME}
        WHERE club_id = %s AND opponent_goals = 0
        ORDER BY game_id DESC
        """
        cursor.execute(query, (club_id,))
        results = cursor.fetchall()
        
        for row in results:
            results_list.append(ClubGames(**row))
            
        return results_list
    except Exception as e:
        print(f"Error (get_clean_sheets): {e}")
        return []
    finally:
        if conn: conn.close()