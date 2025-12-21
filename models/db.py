import pymysql
from database import Config

def get_db_connection():
    """Creates and returns a database connection using settings from Config."""
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )