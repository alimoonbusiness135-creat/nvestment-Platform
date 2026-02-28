import sqlite3

def reset_sqlite_cache():
    conn = sqlite3.connect('investment.db')
    cursor = conn.cursor()
    
    # Run VACUUM to rebuild the database
    print("Running VACUUM to rebuild the database...")
    cursor.execute("VACUUM")
    conn.commit()
    
    # Run ANALYZE to update statistics
    print("Running ANALYZE to update statistics...")
    cursor.execute("ANALYZE")
    conn.commit()
    
    # Close connection
    conn.close()
    print("SQLite cache reset successfully.")

if __name__ == '__main__':
    reset_sqlite_cache() 
 