import sqlite3

def add_recovery_phone_column():
    """Add recovery_phone column to the user table"""
    try:
        conn = sqlite3.connect('investment.db')
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'recovery_phone' not in columns:
            print("Adding recovery_phone column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN recovery_phone VARCHAR(20)")
            conn.commit()
            print("Column added successfully!")
        else:
            print("recovery_phone column already exists.")
        
        # Verify columns
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        print("\nAll columns in the user table:")
        for col in columns:
            print(f" - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_recovery_phone_column() 