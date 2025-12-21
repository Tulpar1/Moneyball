from database import get_db_connection

class GamesModel:
    @staticmethod
    def get_all_games(page=1, per_page=50, search_term="", opponent="", competition_id="", season="", min_attendance="", max_attendance="", competition_type="", sort_by="date", sort_order="DESC"):
        conn = get_db_connection()
        offset = (page - 1) * per_page
        
        where_clauses = []
        params = []
        
        # 1. Takım (Ana Arama)
        if search_term:
            where_clauses.append("(home_club_name LIKE %s OR away_club_name LIKE %s)")
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            
        # 2. Takım (Rakip - Yeni Özellik)
        if opponent:
            where_clauses.append("(home_club_name LIKE %s OR away_club_name LIKE %s)")
            params.extend([f"%{opponent}%", f"%{opponent}%"])
            
        if competition_id:
            where_clauses.append("competition_id = %s")
            params.append(competition_id)
        if season:
            where_clauses.append("season = %s")
            params.append(season)
        if min_attendance:
            where_clauses.append("attendance >= %s")
            params.append(min_attendance)
        if max_attendance:
            where_clauses.append("attendance <= %s")
            params.append(max_attendance)
        if competition_type:
            where_clauses.append("competition_type = %s")
            params.append(competition_type)
            
        where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        allowed_columns = {
            "date": "date", 
            "competition": "competition_id",
            "home_club": "home_club_name",
            "score": "home_club_goals",
            "away_club": "away_club_name",
            "stadium": "stadium",
            "attendance": "attendance",
            "type": "competition_type"
        }
        
        order_col = allowed_columns.get(sort_by, "date")
        order_dir = "ASC" if sort_order.upper() == "ASC" else "DESC"

        try:
            cursor = conn.cursor(dictionary=True) 
            query = f"""
                SELECT * FROM games
                {where_str}
                ORDER BY {order_col} {order_dir}
                LIMIT %s OFFSET %s
            """
            params.extend([per_page, offset])
            cursor.execute(query, tuple(params))       
            return cursor.fetchall()
        finally:
            if conn: conn.close()

    @staticmethod
    def get_total_games_count(search_term="", opponent="", competition_id="", season="", min_attendance="", max_attendance="", competition_type=""):
        conn = get_db_connection()
        where_clauses = []
        params = []
        
        if search_term:
            where_clauses.append("(home_club_name LIKE %s OR away_club_name LIKE %s)")
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        if opponent: # Yeni Özellik
            where_clauses.append("(home_club_name LIKE %s OR away_club_name LIKE %s)")
            params.extend([f"%{opponent}%", f"%{opponent}%"])
        if competition_id:
            where_clauses.append("competition_id = %s")
            params.append(competition_id)
        if season:
            where_clauses.append("season = %s")
            params.append(season)
        if min_attendance:
            where_clauses.append("attendance >= %s")
            params.append(min_attendance)
        if max_attendance:
            where_clauses.append("attendance <= %s")
            params.append(max_attendance)
        if competition_type:
            where_clauses.append("competition_type = %s")
            params.append(competition_type)

        where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        try:
            cursor = conn.cursor(dictionary=True)
            query = f"SELECT COUNT(*) as total FROM games {where_str}"
            cursor.execute(query, tuple(params))
            res = cursor.fetchone()
            return res['total'] if res else 0
        finally:
            if conn: conn.close()