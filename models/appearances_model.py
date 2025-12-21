from database import get_db_connection

class AppearanceModel:
    @staticmethod
    def get_all_appearances(search_query=None, min_minutes=None, page=1, per_page=20):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        offset = (page - 1) * per_page
        
        # Base SQL Query with NULL filter
        query = "SELECT * FROM appearances WHERE player_name IS NOT NULL AND player_name != ''"
        params = []
        
        if search_query:
            query += " AND player_name LIKE %s"
            params.append(f"%{search_query}%")
        
        if min_minutes:
            query += " AND minutes_played >= %s"
            params.append(min_minutes)
            
        # Tarihe göre sıralama ve Sayfalama
        query += " ORDER BY date DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        appearances = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as count FROM appearances")
        total_count = cursor.fetchone()['count']
        
        cursor.close()
        db.close()
        return appearances, total_count

    @staticmethod
    def get_appearance_by_id(app_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM appearances WHERE appearance_id = %s", (app_id,))
        appearance = cursor.fetchone()
        cursor.close()
        db.close()
        return appearance