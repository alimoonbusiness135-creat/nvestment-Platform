import sqlite3
import os

def check_admin_instance():
    db_path = 'instance/investment.db'
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM user WHERE id = 1")
        admin = cursor.fetchone()
        
        if admin:
            print("Admin User found in INSTANCE DB:")
            for key in admin.keys():
                print(f"{key}: {admin[key]}")
        else:
            print("Admin user with ID 1 not found in INSTANCE DB.")
            
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_admin_instance()
