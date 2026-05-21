from app.database.database import get_connection
from app.utils.auth import hash_password

def create_admin():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Kiểm tra xem đã có email này chưa
        cursor.execute("SELECT id FROM users WHERE email = 'admin@geojob.com'")
        if cursor.fetchone():
            print("Tài khoản admin@geojob.com đã tồn tại.")
            return

        hashed_pw = hash_password('admin123')
        cursor.execute("""
            INSERT INTO users (fullname, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, ('System Admin', 'admin@geojob.com', hashed_pw, 'Admin'))
        conn.commit()
        print("--- TẠO TÀI KHOẢN ADMIN THÀNH CÔNG ---")
        print("Email: admin@geojob.com")
        print("Password: admin123")
        print("Role: Admin")
        print("--------------------------------------")
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin()
