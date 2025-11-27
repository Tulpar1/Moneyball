# File: services/players.py
# Author: Hasan Özgür Çağan
# Description: Service layer for the Players model in the Moneyball project.
#              Provides backend functions to retrieve and process player data
#              using the database connection (db).

from Database import db
from Models.Players import Players

PLAYERS_COLUMNS = [
    'player_id', 
    'first_name', 
    'last_name', 
    'name', 
    'last_season', 
    'current_club_id', 
    'player_code', 
    'country_of_birth', 
    'city_of_birth', 
    'country_of_citizenship', 
    'date_of_birth', 
    'sub_position', 
    'position', 
    'foot', 
    'height_in_cm', 
    'market_value_in_eur', 
    'highest_market_value_in_eur', 
    'contract_expiration_date', 
    'agent_name', 
    'image_url', 
    'url', 
    'current_club_domestic_competition_id', 
    'current_club_name'
]

SELECT_FIELDS = ', '.join(PLAYERS_COLUMNS)
PLACEHOLDERS = ', '.join(['%s'] * len(PLAYERS_COLUMNS))


def get_player(player_id):
    """
    Fetch a single player from the database by their unique player_id.
    Returns a Players object if found, otherwise None.
    """
    return db.players.get(player_id)


def get_total_player_count():
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM players"
        cursor.execute(query)
        result = cursor.fetchone()
        return result['COUNT(*)'] if result else 0
    except Exception as e:
        print(f"Hata (get_total_player_count): {e}")
        return 0
    finally:
        if conn: conn.close()

# --- Search ve Pagination Desteği için get_all_players fonksiyonunu güncelle ---
def get_all_players(page=1, per_page=50, search_term=""):
    conn = db.get_connection()
    results_list = []
    
    # Sayfalama için offset hesaplama
    offset = (page - 1) * per_page
    
    # Arama terimi için WHERE koşulu oluşturma
    where_clause = ""
    query_params = [per_page, offset]
    
    if search_term:
        search_like = f"%{search_term}%"
        # Not: Arama yapılacak sütunları burada listelemelisin (name, position, country_of_birth gibi)
        search_cols = ["name", "position", "country_of_birth", "player_code"]
        
        where_conditions = [f"{col} LIKE %s" for col in search_cols]
        where_clause = " WHERE " + " OR ".join(where_conditions)
        
        # LIMIT ve OFFSET'ten önce arama parametrelerini eklemeliyiz
        query_params = [search_like] * len(search_cols) + [per_page, offset]


    try:
        cursor = conn.cursor()
        
        
        query = f"""
            SELECT {SELECT_FIELDS} FROM players
            {where_clause}
            ORDER BY name ASC 
            LIMIT %s OFFSET %s
        """
        
        # LIMIT ve OFFSET parametreleri query_params'ın sonunda olmalı.
        cursor.execute(query, tuple(query_params))       
        results = cursor.fetchall()
        
        for row in results:
            try:
                obj = Players(**row)
                results_list.append(obj)
            except TypeError as e:
                print(f"Model çevrim hatası (Satır atlandı): {e}")

        return results_list

    except Exception as e:
        print(f"Hata (get_all_players): {e}")
        return []
    finally:
        if conn: conn.close()


def get_top_players(limit=10):
    """
    Retrieve the top N players ranked by their market value (descending order).
    Default is 10 players.
    """
    players = db.players.all()
    return sorted(
        players,
        key=lambda p: float(p.market_value_in_eur or 0),
        reverse=True
    )[:limit]

def get_players_by_position(position):
    """
    Return all players who play in a given position.
    Example input: "Midfield", "Defender", "Attack", "Goalkeeper".
    Matching is case-sensitive based on stored data.
    """
    from Database import db
    players = db.players.all()
    return [p for p in players if p.position == position]

from datetime import datetime

def get_players_older_than(age):
    """
    Returns all players older than the given age.
    Uses the player's date_of_birth field to calculate age.
    Players without valid date_of_birth are ignored.
    """
    players = db.players.all()
    result = []

    for p in players:
        if p.date_of_birth:
            try:
                dob = datetime.strptime(p.date_of_birth, "%Y-%m-%d")
                player_age = (datetime.now() - dob).days // 365

                if player_age > age:
                    result.append(p)
            except:
                # Skip invalid dates
                pass

    return result

def get_players_younger_than(age):
    """
    Returns all players younger than the given age.
    Players without valid or parsable date_of_birth are skipped.
    """
    players = db.players.all()
    result = []

    for p in players:
        if p.date_of_birth:
            try:
                dob = datetime.strptime(p.date_of_birth, "%Y-%m-%d")
                player_age = (datetime.now() - dob).days // 365
                if player_age < age:
                    result.append(p)
            except:
                pass
    return result

def get_undervalued_players(threshold_ratio=0.5):
    """
    Returns players whose current market value is significantly lower
    than their historical highest market value.
    Example: threshold_ratio=0.5 means current value < 50% of peak value.
    Players missing value data are ignored.
    """
    players = db.players.all()
    result = []

    for p in players:
        try:
            current = float(p.market_value_in_eur or 0)
            peak = float(p.highest_market_value_in_eur or 0)

            if peak > 0 and current > 0:
                ratio = current / peak
                if ratio < threshold_ratio:
                    result.append(p)
        except:
            pass

    return result

def get_players_by_country(country):
    """
    Return all players whose citizenship matches the given country.
    Case-insensitive comparison.
    """
    players = db.players.all()
    return [
        p for p in players
        if p.country_of_citizenship
        and p.country_of_citizenship.lower() == country.lower()
    ]

def insert_player(player_data: dict):

    conn = db.get_connection()
    try:
        cursor = conn.cursor()


        query = f"""
        INSERT INTO players ({SELECT_FIELDS})
        VALUES ({PLACEHOLDERS})
        """

        insert_values = [player_data.get(col) for col in PLAYERS_COLUMNS]

        cursor.execute(query, tuple(insert_values))

        new_id = player_data.get('player_id', cursor.lastrowid)

        conn.commit()
        cursor.close()
        return new_id

    except Exception as e:
        print(f"Error (create_player): {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()



