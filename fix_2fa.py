import sqlite3
import os

def update_database():
    db_path = 'investment.db'
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        # List files in the current directory
        print("Files in current directory:")
        for file in os.listdir('.'):
            if file.endswith('.db'):
                print(f"- {file}")
        return
    
    print(f"Database file found: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Check if user table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
    if not cursor.fetchone():
        print("Error: 'user' table not found in the database!")
        return
    
    # Check if the two_factor_enabled column exists
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    print("Columns in user table:")
    column_names = []
    for col in columns:
        column_names.append(col[1])
        print(f"- {col[1]} (type: {col[2]})")
    
    if 'two_factor_enabled' not in column_names:
        print("\nAdding two_factor_enabled column to user table...")
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0")
            conn.commit()
            print("Added two_factor_enabled column successfully.")
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
    else:
        print("\ntwo_factor_enabled column already exists.")
    
    # Create TwoFactorAuth table if it doesn't exist
    try:
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
        print("TwoFactorAuth table created or verified.")
    except sqlite3.Error as e:
        print(f"SQLite error while creating two_factor_auth table: {e}")
    
    conn.close()
    print("Database update completed.")

if __name__ == '__main__':
    update_database() 