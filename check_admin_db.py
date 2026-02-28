import sqlite3
import os

def check_admin():
    db_path = 'investment.db'
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, username, email FROM user WHERE id = 1")
        admin = cursor.fetchone()
        
        if admin:
            print(f"Admin User Found: ID={admin[0]}, Username={admin[1]}, Email={admin[2]}")
        else:
            print("Admin user with ID 1 not found in the database.")
            
        cursor.execute("SELECT id, username, email FROM user LIMIT 5")
        users = cursor.fetchall()
        print("\nFirst 5 users in database:")
        for user in users:
            print(f"ID={user[0]}, Username={user[1]}, Email={user[2]}")
            
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_admin()
