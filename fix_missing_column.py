from app import app, db
import sqlite3
import os

def fix_deposit_table():
    with app.app_context():
        try:
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if not os.path.exists(db_path):
                    # Check in instance folder too
                    if os.path.exists(os.path.join('instance', db_path)):
                        db_path = os.path.join('instance', db_path)
                
                print(f"Connecting to database: {db_path}")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check columns in deposit table
                cursor.execute("PRAGMA table_info(deposit)")
                columns = [info[1] for info in cursor.fetchall()]
                
                if 'proof_image' not in columns:
                    print("Adding proof_image column to deposit table...")
                    cursor.execute("ALTER TABLE deposit ADD COLUMN proof_image VARCHAR(100)")
                    conn.commit()
                    print("Column added successfully!")
                else:
                    print("Column proof_image already exists.")
                
                conn.close()
            else:
                print(f"Unsupported database URI: {db_uri}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    fix_deposit_table()
