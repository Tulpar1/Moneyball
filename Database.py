import pymysql
class Database:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = 'egemen4020' 
        self.db = 'moneyball'
        self.charset = 'utf8mb4'

    def get_connection(self):
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except pymysql.MySQLError as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            return None
db = Database()