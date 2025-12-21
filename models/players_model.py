from database import get_db_connection

class PlayerModel:
    @staticmethod
    def get_all_players(search_query=None, position_filter=None, country_filter=None, sort_by='name', sort_order='asc', page=1, per_page=20):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        offset = (page - 1) * per_page
        
        # Güvenlik ve Mapping: İzin verilen sıralama sütunları
        # Yaş (age) istenirse veritabanındaki date_of_birth kullanılır
        # Not: Yaşın büyük olması, doğum tarihinin küçük olması demektir. 
        # Bu yüzden Age mantığını Controller veya View'da tersleyebiliriz ama burada düz mantık kuralım:
        valid_sort_columns = {
            'name': 'p.name',
            'market_value_in_eur': 'p.market_value_in_eur',
            'age': 'p.date_of_birth' 
        }
        
        # Eğer geçersiz bir sütun gelirse varsayılan olarak isme göre sırala
        sort_column = valid_sort_columns.get(sort_by, 'p.name')
        
        # Yön kontrolü (SQL Injection önlemi)
        order_direction = 'ASC' if sort_order == 'asc' else 'DESC'

        # Yaş sıralamasında mantık terstir:
        # Yaş Küçükten Büyüğe (ASC) -> Doğum Tarihi Büyükten Küçüğe (DESC)
        if sort_by == 'age':
            order_direction = 'DESC' if sort_order == 'asc' else 'ASC'

        # Temel sorgu: Clubs tablosu ile JOIN yapıldı
        base_query = """
            FROM players p 
            LEFT JOIN clubs c ON p.current_club_id = c.club_id 
            WHERE 1=1
        """
        params = []
        
        # Filtreler
        if search_query:
            base_query += " AND (p.name LIKE %s OR c.name LIKE %s)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        
        if position_filter:
            base_query += " AND p.position = %s"
            params.append(position_filter)

        if country_filter:
            base_query += " AND p.country_of_citizenship LIKE %s"
            params.append(f"%{country_filter}%")
            
        # Veri çekme sorgusu (Dinamik Sıralama Eklendi)
        query = f"SELECT p.*, c.name as club_name {base_query} ORDER BY {sort_column} {order_direction} LIMIT %s OFFSET %s"
        query_params = params + [per_page, offset]
        
        cursor.execute(query, query_params)
        players = cursor.fetchall()
        
        # Toplam kayıt sayısı
        count_query = f"SELECT COUNT(*) as count {base_query}"
        cursor.execute(count_query, params)
        res = cursor.fetchone()
        total_count = res['count'] if res else 0
        
        cursor.close()
        db.close()
        return players, total_count

    @staticmethod
    def get_player_by_id(player_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT p.*, c.name as club_name 
            FROM players p 
            LEFT JOIN clubs c ON p.current_club_id = c.club_id 
            WHERE p.player_id = %s
        """
        cursor.execute(query, (player_id,))
        player = cursor.fetchone()
        cursor.close()
        db.close()
        return player