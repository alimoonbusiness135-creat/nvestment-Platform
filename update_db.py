from app import app, db
from sqlalchemy import inspect, text
import os
import sqlite3

def update_database_schema():
    """Update the database schema to include recovery columns"""
    with app.app_context():
        try:
            # Check if database file exists
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
                    print(f"Database file not found or empty: {db_path}")
                    print("Creating new database with all tables...")
                    db.create_all()
                    print("New database created with all tables.")
                    return
                else:
                    print(f"Using existing database: {db_path}")
            
            # Use raw SQL to add columns if they don't exist
            inspector = inspect(db.engine)
            if not inspector.has_table('user'):
                print("User table not found. Creating all tables...")
                db.create_all()
                print("All tables created.")
                return
            
            columns = [column['name'] for column in inspector.get_columns('user')]
            
            # Use a transaction for the ALTER TABLE statements
            with db.engine.begin() as connection:
                # Check and add recovery_email column
                if 'recovery_email' not in columns:
                    print("Adding recovery_email column to user table...")
                    connection.execute(text("ALTER TABLE user ADD COLUMN recovery_email VARCHAR(120)"))
                    print("recovery_email column added.")
                else:
                    print("recovery_email column already exists.")
                
                # Check and add recovery_phone column
                if 'recovery_phone' not in columns:
                    print("Adding recovery_phone column to user table...")
                    connection.execute(text("ALTER TABLE user ADD COLUMN recovery_phone VARCHAR(20)"))
                    print("recovery_phone column added.")
                else:
                    print("recovery_phone column already exists.")
            
            print("Database schema update completed successfully!")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()

def update_database():
    # Connect to the SQLite database
    with app.app_context():
        conn = sqlite3.connect('investment.db')
        cursor = conn.cursor()
        
        # Check if the two_factor_enabled column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'two_factor_enabled' not in columns:
            print("Adding two_factor_enabled column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0")
        
        # Commit the changes
        conn.commit()
        print("Database schema updated successfully.")
        
        # Create TwoFactorAuth table if it doesn't exist
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
        print("TwoFactorAuth table created if it didn't exist.")
        
        conn.close()

if __name__ == "__main__":
    update_database_schema()
    update_database() 