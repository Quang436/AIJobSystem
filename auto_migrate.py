import sys
import os

# Ensure the app module can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database.database import get_connection
except ImportError as e:
    print(f"Failed to import get_connection: {e}")
    sys.exit(1)

def migrate():
    print("Đang khởi tạo kết nối Database...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
        return

    queries = [
        "ALTER TABLE users ADD cv_file_url NVARCHAR(1000) NULL;",
        "ALTER TABLE users ADD cccd_number NVARCHAR(20) NULL;",
        "ALTER TABLE users ADD cccd_front_url NVARCHAR(1000) NULL;",
        "ALTER TABLE users ADD cccd_back_url NVARCHAR(1000) NULL;",
        "ALTER TABLE users ADD certificate_urls NVARCHAR(MAX) NULL;",
        "ALTER TABLE employer_profiles ADD tax_code NVARCHAR(50) NULL;",
        "ALTER TABLE employer_profiles ADD facility_images NVARCHAR(MAX) NULL;",
        "ALTER TABLE employer_profiles ADD manager_phone NVARCHAR(30) NULL;"
    ]
    
    for q in queries:
        try:
            cursor.execute(q)
            conn.commit()
            print(f"✅ Đã thêm: {q.split('ADD ')[1].split(' ')[0]}")
        except Exception as e:
            # Catching errors if the column already exists
            print(f"⚠️ Bỏ qua (Đã tồn tại): {q.split('ADD ')[1].split(' ')[0]}")
            
    conn.close()
    print("\n🎉 Hoàn tất vá Database tự động! Bạn có thể test Đăng ký lại rồi.")

if __name__ == '__main__':
    migrate()
