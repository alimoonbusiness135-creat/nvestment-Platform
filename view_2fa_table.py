import sqlite3
import os

def view_2fa_table():
    db_path = 'investment.db'
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        return
    
    print(f"Database file found: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if two_factor_auth table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='two_factor_auth';")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("\nWARNING: The two_factor_auth table does NOT exist in the database!")
        
        # Try to create the table
        try:
            print("Attempting to create the two_factor_auth table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS two_factor_auth (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL UNIQUE,
                    secret_key VARCHAR(32) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    backup_codes TEXT,
                    FOREIGN KEY(user_id) REFERENCES user(id)
                )
            """)
            conn.commit()
            print("Successfully created the two_factor_auth table.")
            
            # Check if the table was actually created
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='two_factor_auth';")
            if cursor.fetchone():
                print("Verified: The two_factor_auth table now exists.")
            else:
                print("ERROR: Failed to create the two_factor_auth table!")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
    else:
        print("\nThe two_factor_auth table exists in the database.")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(two_factor_auth)")
        columns = cursor.fetchall()
        print("\n=== TWO_FACTOR_AUTH TABLE SCHEMA ===")
        print("Columns:")
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, is_pk = col
            print(f"  - {col_name} (type: {col_type}, not_null: {not_null}, default: {default_val}, pk: {is_pk})")
    
    conn.close()

if __name__ == '__main__':
    view_2fa_table() 