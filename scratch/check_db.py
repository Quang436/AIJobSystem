from app.database.database import get_connection

def check_columns():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 0 * FROM jobs")
        columns = [column[0] for column in cursor.description]
        print(f"Columns in 'jobs' table: {columns}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_columns()
