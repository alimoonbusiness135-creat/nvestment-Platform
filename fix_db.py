from app import app
import os
import sqlite3

def fix_database():
    """Find the correct database and ensure it has all required columns"""
    with app.app_context():
        # Print the configured database URI
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Configured database URI: {db_uri}")
        
        # Extract the database path
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            absolute_path = os.path.abspath(db_path)
            print(f"Database file should be at: {absolute_path}")
            
            # Check if the file exists
            if os.path.exists(absolute_path):
                file_size = os.path.getsize(absolute_path)
                print(f"Database file exists: {absolute_path} (Size: {file_size} bytes)")
            else:
                print(f"Database file NOT found at: {absolute_path}")
                
            # Look for any .db files in the current directory
            db_files = [f for f in os.listdir() if f.endswith('.db')]
            
            if db_files:
                print(f"Found {len(db_files)} .db files in the current directory:")
                for db_file in db_files:
                    db_size = os.path.getsize(db_file)
                    print(f" - {db_file} (Size: {db_size} bytes)")
                    
                    # Check the schema of each database
                    try:
                        conn = sqlite3.connect(db_file)
                        cursor = conn.cursor()
                        cursor.execute("PRAGMA table_info(user)")
                        columns = cursor.fetchall()
                        
                        print(f"   Columns in the 'user' table of {db_file}:")
                        column_names = []
                        for col in columns:
                            column_names.append(col[1])
                            print(f"     - {col[1]} ({col[2]})")
                        
                        # Check for recovery columns
                        if 'recovery_email' in column_names and 'recovery_phone' in column_names:
                            print(f"   ✅ This database HAS the required recovery columns")
                        else:
                            print(f"   ❌ This database DOES NOT HAVE the required recovery columns")
                            
                            # Check if this is the correct database file
                            if db_file == os.path.basename(db_path):
                                print("   This is the configured database but it's missing columns!")
                                
                                # Add the missing columns
                                print("   Adding the missing recovery columns...")
                                if 'recovery_email' not in column_names:
                                    cursor.execute("ALTER TABLE user ADD COLUMN recovery_email VARCHAR(120)")
                                if 'recovery_phone' not in column_names:
                                    cursor.execute("ALTER TABLE user ADD COLUMN recovery_phone VARCHAR(20)")
                                
                                conn.commit()
                                print("   ✅ Recovery columns added successfully")
                        
                        conn.close()
                    except Exception as e:
                        print(f"   Error examining {db_file}: {e}")
            else:
                print("No .db files found in the current directory")
        else:
            print("Not a SQLite database - cannot fix directly")

if __name__ == "__main__":
    fix_database()