from database import get_db_connection

class ClubModel:
    @staticmethod
    def get_all_clubs(search_query=None, league_filter=None, min_squad=None, max_squad=None, sort_by='name', sort_order='asc', page=1, per_page=20):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        offset = (page - 1) * per_page
        
        where_clauses = []
        params = []
        
        if search_query:
            where_clauses.append("c.name LIKE %s")
            params.append(f"%{search_query}%")
        
        if league_filter:
            where_clauses.append("c.domestic_competition_id = %s")
            params.append(league_filter)
            
        if min_squad:
            where_clauses.append("c.squad_size >= %s")
            params.append(min_squad)
        if max_squad:
            where_clauses.append("c.squad_size <= %s")
            params.append(max_squad)
        # Add base NULL filter for club name
        where_clauses.append("c.name IS NOT NULL AND c.name != ''")
            
        where_str = " WHERE " + " AND ".join(where_clauses)
        
        allowed_sorts = {'name': 'c.name', 'squad_size': 'c.squad_size', 'id': 'c.club_id'}
        sort_col = allowed_sorts.get(sort_by, 'c.name')
        sort_dir = "DESC" if sort_order == "desc" else "ASC"

        try:
            query = f"""
                SELECT c.*, comp.name as league_name, comp.sub_type as league_type
                FROM clubs c
                LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
                {where_str}
                ORDER BY {sort_col} {sort_dir}
                LIMIT %s OFFSET %s
            """
            
            current_params = params + [per_page, offset]
            cursor.execute(query, tuple(current_params))
            clubs = cursor.fetchall()
            
            count_query = f"SELECT COUNT(*) as count FROM clubs c {where_str}"
            cursor.execute(count_query, tuple(params))
            total_count = cursor.fetchone()['count']
            
            return clubs, total_count
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def get_club_by_id(club_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            query = """
                SELECT c.*, comp.name as league_name 
                FROM clubs c
                LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
                WHERE c.club_id = %s
            """
            cursor.execute(query, (club_id,))
            return cursor.fetchone()
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def add_club(name, competition_id, squad_size, image_url=None, url=None):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            # Otomatik ID üretimi
            cursor.execute("SELECT MAX(club_id) FROM clubs")
            row = cursor.fetchone()
            max_id = row[0] if row and row[0] is not None else 0
            new_id = max_id + 1

            query = """
                INSERT INTO clubs (club_id, name, domestic_competition_id, squad_size)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (new_id, name, competition_id, squad_size))
            db.commit()
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def update_club(club_id, name, competition_id, squad_size, image_url=None, url=None):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            query = """
                UPDATE clubs 
                SET name = %s, domestic_competition_id = %s, squad_size = %s
                WHERE club_id = %s
            """
            cursor.execute(query, (name, competition_id, squad_size, club_id))
            db.commit()
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def delete_club(club_id):
        # İŞTE BURASI: Önce maçları, sonra kulübü siliyoruz (Manual Cascade)
        db = get_db_connection()
        cursor = db.cursor()
        try:
            # 1. ADIM: Bu kulübe ait tüm maç kayıtlarını sil
            # (Hem kendisinin olduğu hem rakip olduğu maçlar)
            delete_games_query = "DELETE FROM club_games WHERE club_id = %s OR opponent_id = %s"
            cursor.execute(delete_games_query, (club_id, club_id))
            
            # 2. ADIM: Kulübü sil
            delete_club_query = "DELETE FROM clubs WHERE club_id = %s"
            cursor.execute(delete_club_query, (club_id,))
            
            db.commit()
            return True
        except Exception as e:
            print(f"Silme Hatası: {e}")
            db.rollback() # Hata olursa işlemi geri al
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()