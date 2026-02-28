import sqlite3
import os
import hashlib
from werkzeug.security import generate_password_hash

def update_admin():
    db_path = 'investment.db'
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        return
    
    new_email = 'alidaniyal555@gmail.com'
    new_password = 'Alidani555???'
    
    # Generate both hashes for compatibility
    werkzeug_hash = generate_password_hash(new_password)
    sha256_hash = hashlib.sha256(new_password.encode()).hexdigest()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Update admin user (id=1)
        # Using sha256_hash for the password field as seen in init_db.py
        # and checking if the app prefers werkzeug or sha256
        cursor.execute("""
            UPDATE user 
            SET email = ?, password = ? 
            WHERE id = 1
        """, (new_email, sha256_hash))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Admin user updated successfully!")
            print(f"New Email: {new_email}")
            print(f"New Password: {new_password}")
        else:
            print("❌ Admin user with ID 1 not found.")
            
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    update_admin()
