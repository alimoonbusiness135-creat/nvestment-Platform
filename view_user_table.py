import sqlite3
import os

def view_user_table():
    db_path = 'investment.db'
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        return
    
    print(f"Database file found: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get user table schema
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    print("\n=== USER TABLE SCHEMA ===")
    print("Columns:")
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, is_pk = col
        print(f"  - {col_name} (type: {col_type}, not_null: {not_null}, default: {default_val}, pk: {is_pk})")
    
    # Check if two_factor_enabled column exists
    has_two_factor = any(col[1] == 'two_factor_enabled' for col in columns)
    if has_two_factor:
        print("\nThe two_factor_enabled column exists in the user table.")
    else:
        print("\nWARNING: The two_factor_enabled column does NOT exist in the user table!")
        
        # Try to add the column
        try:
            print("Attempting to add the two_factor_enabled column...")
            cursor.execute("ALTER TABLE user ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0")
            conn.commit()
            print("Successfully added the two_factor_enabled column.")
        except sqlite3.Error as e:
            print(f"Error adding column: {e}")
    
    conn.close()

if __name__ == '__main__':
    view_user_table() 