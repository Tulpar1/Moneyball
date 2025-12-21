from database import get_db_connection

def verify_database():
    print("--- Veritabanı Bağlantı Testi Başlatılıyor ---")
    
    # database.py içindeki fonksiyonu çağırıyoruz
    db = get_db_connection()

    if db is not None:
        try:
            print("✅ BAŞARILI: Veritabanına fiziksel bağlantı kuruldu.")
            
            cursor = db.cursor()
            
            # 1. Veritabanı ismini kontrol et
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"📂 Bağlı olunan veritabanı: {db_name[0]}")

            # 2. Tabloları listele (İçeride ne var görelim)
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            
            if tables:
                print("\n📋 Mevcut Tablolar:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("\n⚠️ Uyarı: Bağlantı var ama veritabanı içinde henüz hiç tablo yok.")

            cursor.close()
            db.close()
            print("\n--- Test Başarıyla Tamamlandı ---")

        except Exception as e:
            print(f"❌ Sorgu sırasında hata oluştu: {e}")
    else:
        print("❌ HATA: Bağlantı kurulamadı!")
        print("Lütfen database.py içindeki HOST, PORT, USER ve PASSWORD bilgilerini kontrol edin.")

if __name__ == "__main__":
    verify_database()