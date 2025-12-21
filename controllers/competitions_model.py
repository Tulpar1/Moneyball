from database import get_db_connection

class CompetitionModel:
    @staticmethod
    def get_all_competitions(search_query=None, type_filter=None, sort_by='name', page=1, per_page=20):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        offset = (page - 1) * per_page
        
        # Dinamik SQL Sorgusu
        query = "SELECT * FROM competitions WHERE 1=1"
        params = []
        
        if search_query:
            query += " AND name LIKE %s"
            params.append(f"%{search_query}%")
        if type_filter:
            query += " AND type = %s"
            params.append(type_filter)
            
        # Sıralama ve Sayfalama
        query += f" ORDER BY {sort_by} LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        competitions = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as count FROM competitions")
        total_count = cursor.fetchone()['count']
        
        cursor.close()
        db.close()
        return competitions, total_count

    @staticmethod
    def get_competition_by_id(comp_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM competitions WHERE competition_id = %s", (comp_id,))
        comp = cursor.fetchone()
        cursor.close()
        db.close()
        return comp