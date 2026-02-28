from app import app, db
from models import User, Deposit, Earning, Withdrawal, Notification, Referral
import sqlite3
import os

def add_recovery_columns():
    """Add recovery_email and recovery_phone columns to the user table"""
    with app.app_context():
        try:
            # Get the database URI from app config
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            
            # Parse the SQLite database path from the URI
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                
                # Check if database file exists
                if not os.path.exists(db_path):
                    print(f"Database file not found at: {db_path}")
                    return
                
                print(f"Using database at: {db_path}")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if columns already exist
                cursor.execute("PRAGMA table_info(user)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'recovery_email' not in columns:
                    print("Adding recovery_email column to user table...")
                    cursor.execute("ALTER TABLE user ADD COLUMN recovery_email VARCHAR(120)")
                
                if 'recovery_phone' not in columns:
                    print("Adding recovery_phone column to user table...")
                    cursor.execute("ALTER TABLE user ADD COLUMN recovery_phone VARCHAR(20)")
                
                conn.commit()
                print("Database migration completed successfully!")
            else:
                print(f"Unsupported database URI: {db_uri}")
                
        except Exception as e:
            print(f"An error occurred during migration: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    add_recovery_columns() 