import mysql.connector

class Config:
    SECRET_KEY = 'abartan123'
    
    # Database Configuration
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''  
    DB_NAME = 'moneyball'
    DB_PORT = 3306

def get_db_connection():
    """Veritabanına bağlanmak için bu fonksiyonu kullanacağız"""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Hata: {err}")
        return None