from database import get_db_connection

class GameEventsModel:
    @staticmethod
    def get_all_events(page=1, per_page=50, player_name="", club_name="", event_type="", min_minute="", max_minute="", sort_by="minute", sort_order="ASC"):
        conn = get_db_connection()
        offset = (page - 1) * per_page
        
        where_clauses = []
        params = []
        
        # Game ID bloğu kaldırıldı
        
        if player_name:
            where_clauses.append("(p.name LIKE %s OR p_in.name LIKE %s)")
            params.extend([f"%{player_name}%", f"%{player_name}%"])
        if club_name:
            where_clauses.append("c.name LIKE %s")
            params.append(f"%{club_name}%")
            
        # GÜNCELLEME: Penaltı mantığı değiştirildi
        if event_type:
            if event_type == "Penalty":
                # Hem seri penaltı atışlarını (Shootout) hem de açıklamasında 'Penalty' geçen golleri getir
                where_clauses.append("(ge.type = 'Shootout' OR ge.description LIKE %s)")
                params.append("%Penalty%")
            else:
                where_clauses.append("ge.type = %s")
                params.append(event_type)
                
        if min_minute:
            where_clauses.append("ge.minute >= %s")
            params.append(min_minute)
        if max_minute:
            where_clauses.append("ge.minute <= %s")
            params.append(max_minute)
        # Add base NULL filters for essential fields
        where_clauses.append("p.name IS NOT NULL AND p.name != ''")
        where_clauses.append("ge.type IS NOT NULL AND ge.type != ''")
        where_clauses.append("ge.minute IS NOT NULL")
        where_clauses.append("g.home_club_name IS NOT NULL")
        where_clauses.append("g.away_club_name IS NOT NULL")
            
        where_str = " WHERE " + " AND ".join(where_clauses)
        
        allowed_columns = {
            "minute": "ge.minute",
            "type": "ge.type",
            "club": "c.name",
            "player": "p.name"
        }
        order_col = allowed_columns.get(sort_by, "ge.minute")
        order_dir = "ASC" if sort_order.upper() == "ASC" else "DESC"

        try:
            cursor = conn.cursor(dictionary=True) 
            query = f"""
                SELECT ge.*, 
                       c.name as club_name,
                       p.name as player_name, 
                       p_in.name as player_in_name,
                       g.date as game_date,
                       g.home_club_name,
                       g.away_club_name
                FROM game_events ge
                LEFT JOIN clubs c ON ge.club_id = c.club_id
                LEFT JOIN players p ON ge.player_id = p.player_id
                LEFT JOIN players p_in ON ge.player_in_id = p_in.player_id
                LEFT JOIN games g ON ge.game_id = g.game_id
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
    def get_total_events_count(player_name="", club_name="", event_type="", min_minute="", max_minute=""):
        conn = get_db_connection()
        where_clauses = []
        params = []
        
        # Game ID bloğu kaldırıldı

        if player_name:
            where_clauses.append("(p.name LIKE %s OR p_in.name LIKE %s)")
            params.extend([f"%{player_name}%", f"%{player_name}%"])
        if club_name:
            where_clauses.append("c.name LIKE %s")
            params.append(f"%{club_name}%")
            
        # GÜNCELLEME: Count için de aynı penaltı mantığı
        if event_type:
            if event_type == "Penalty":
                where_clauses.append("(ge.type = 'Shootout' OR ge.description LIKE %s)")
                params.append("%Penalty%")
            else:
                where_clauses.append("ge.type = %s")
                params.append(event_type)
                
        if min_minute:
            where_clauses.append("ge.minute >= %s")
            params.append(min_minute)
        if max_minute:
            where_clauses.append("ge.minute <= %s")
            params.append(max_minute)
        # Add base NULL filters for essential fields
        where_clauses.append("p.name IS NOT NULL AND p.name != ''")
        where_clauses.append("ge.type IS NOT NULL AND ge.type != ''")
        where_clauses.append("ge.minute IS NOT NULL")
        where_clauses.append("g.home_club_name IS NOT NULL")
        where_clauses.append("g.away_club_name IS NOT NULL")

        where_str = " WHERE " + " AND ".join(where_clauses)
        try:
            cursor = conn.cursor(dictionary=True)
            query = f"""
                SELECT COUNT(*) as total 
                FROM game_events ge
                LEFT JOIN clubs c ON ge.club_id = c.club_id
                LEFT JOIN players p ON ge.player_id = p.player_id
                LEFT JOIN players p_in ON ge.player_in_id = p_in.player_id
                LEFT JOIN games g ON ge.game_id = g.game_id
                {where_str}
            """
            cursor.execute(query, tuple(params))
            res = cursor.fetchone()
            return res['total'] if res else 0
        finally:
            if conn: conn.close()