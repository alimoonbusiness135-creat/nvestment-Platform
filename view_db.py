import sqlite3
import os

def view_database_schema():
    db_path = 'investment.db'
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        return
    
    print(f"Database file found: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\nTables in database:")
    for table in tables:
        table_name = table[0]
        print(f"\n=== TABLE: {table_name} ===")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, is_pk = col
            print(f"  - {col_name} (type: {col_type}, not_null: {not_null}, default: {default_val}, pk: {is_pk})")
    
    conn.close()
    print("\nDatabase schema view completed.")

if __name__ == '__main__':
    view_database_schema() 