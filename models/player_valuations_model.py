from database import get_db_connection

class PlayerValuationModel:
    @staticmethod
    def get_all_valuations(page=1, per_page=50, player_name="", club_name="", start_year="", end_year="", min_value="", max_value="", sort_by="date", sort_order="DESC"):
        conn = get_db_connection()
        offset = (page - 1) * per_page # Hangi kayıttan başlanacağını belirler
        
        where_clauses = []
        params = []
        
        if player_name:
            where_clauses.append("p.name LIKE %s")
            params.append(f"%{player_name}%")
        if club_name:
            where_clauses.append("c.name LIKE %s")
            params.append(f"%{club_name}%")
        if start_year:
            where_clauses.append("YEAR(pv.date) >= %s")
            params.append(start_year)
        if end_year:
            where_clauses.append("YEAR(pv.date) <= %s")
            params.append(end_year)
        if min_value:
            where_clauses.append("pv.market_value_in_eur >= %s")
            params.append(min_value)
        if max_value:
            where_clauses.append("pv.market_value_in_eur <= %s")
            params.append(max_value)
            
        where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        allowed_columns = {"name": "p.name", "date": "pv.date", "value": "pv.market_value_in_eur"}
        order_col = allowed_columns.get(sort_by, "pv.date")
        order_dir = "ASC" if sort_order.upper() == "ASC" else "DESC"

        try:
            cursor = conn.cursor(dictionary=True) 
            query = f"""
                SELECT pv.*, p.name as player_name, p.image_url as player_image, c.name as club_name
                FROM player_valuations pv
                LEFT JOIN players p ON pv.player_id = p.player_id
                LEFT JOIN clubs c ON pv.current_club_id = c.club_id
                {where_str}
                ORDER BY {order_col} {order_dir}
                LIMIT %s OFFSET %s
            """
            params.extend([per_page, offset]) # LIMIT ve OFFSET parametrelerini ekler
            cursor.execute(query, tuple(params))       
            return cursor.fetchall()
        finally:
            if conn: conn.close()

    @staticmethod
    def get_total_valuation_count(player_name="", club_name="", start_year="", end_year="", min_value="", max_value=""):
        conn = get_db_connection()
        where_clauses = []
        params = []
        
        if player_name:
            where_clauses.append("p.name LIKE %s")
            params.append(f"%{player_name}%")
        if club_name:
            where_clauses.append("c.name LIKE %s")
            params.append(f"%{club_name}%")
        if start_year:
            where_clauses.append("YEAR(pv.date) >= %s")
            params.append(start_year)
        if end_year:
            where_clauses.append("YEAR(pv.date) <= %s")
            params.append(end_year)
        if min_value:
            where_clauses.append("pv.market_value_in_eur >= %s")
            params.append(min_value)
        if max_value:
            where_clauses.append("pv.market_value_in_eur <= %s")
            params.append(max_value)

        where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        try:
            cursor = conn.cursor(dictionary=True)
            query = f"SELECT COUNT(*) as total FROM player_valuations pv LEFT JOIN players p ON pv.player_id = p.player_id LEFT JOIN clubs c ON pv.current_club_id = c.club_id {where_str}"
            cursor.execute(query, tuple(params))
            res = cursor.fetchone()
            return res['total'] if res else 0
        finally:
            if conn: conn.close()