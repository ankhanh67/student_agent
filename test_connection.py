# test_connection.py
import os
from dotenv import load_dotenv
import psycopg2

# Tải biến môi trường từ file .env
load_dotenv()

# Lấy URL kết nối
DATABASE_URL = os.getenv("DATABASE_URL")
print("=" * 50)
print("🔌 ĐANG KIỂM TRA KẾT NỐI DATABASE")
print("=" * 50)
print(f"📌 Database URL: {DATABASE_URL}")
print()

try:
    # Thử kết nối
    conn = psycopg2.connect(DATABASE_URL)
    print(" KẾT NỐI THÀNH CÔNG!")
    
    # Lấy thông tin database
    cur = conn.cursor()
    
    # Kiểm tra version PostgreSQL
    cur.execute('SELECT version()')
    version = cur.fetchone()
    print(f"📊 PostgreSQL version: {version[0][:50]}...")
    
    # Kiểm tra tên database hiện tại
    cur.execute("SELECT current_database()")
    db_name = cur.fetchone()
    print(f"🗄️  Database hiện tại: {db_name[0]}")
    
    cur.close()
    conn.close()
    print("\n ĐÃ NGẮT KẾT NỐI AN TOÀN")
    
except Exception as e:
    print("❌ KẾT NỐI THẤT BẠI!")
    print(f"Lỗi: {e}")

print("=" * 50)