from app import app, db
from sqlalchemy import MetaData, Table, Column, String, inspect
import os

def refresh_sqlalchemy_metadata():
    """Force SQLAlchemy to refresh its metadata from the actual database"""
    with app.app_context():
        try:
            # Get database path
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"Database URI: {db_uri}")
            
            # First, check if the file exists and has the correct columns
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    print(f"Database file exists at: {db_path}")
                    
                    # Check the schema using SQLAlchemy's inspector
                    inspector = inspect(db.engine)
                    table_names = inspector.get_table_names()
                    print(f"Tables in database: {', '.join(table_names)}")
                    
                    if 'user' in table_names:
                        columns = [column['name'] for column in inspector.get_columns('user')]
                        print(f"Columns in user table: {', '.join(columns)}")
                        
                        # Check for recovery columns
                        has_recovery_email = 'recovery_email' in columns
                        has_recovery_phone = 'recovery_phone' in columns
                        
                        print(f"Has recovery_email: {has_recovery_email}")
                        print(f"Has recovery_phone: {has_recovery_phone}")
                        
                        # If columns are missing, we need to add them
                        if not (has_recovery_email and has_recovery_phone):
                            print("One or both recovery columns are missing from the database schema.")
                            
                            # Try to add the missing columns
                            with db.engine.begin() as connection:
                                if not has_recovery_email:
                                    print("Adding recovery_email column...")
                                    connection.execute("ALTER TABLE user ADD COLUMN recovery_email VARCHAR(120)")
                                
                                if not has_recovery_phone:
                                    print("Adding recovery_phone column...")
                                    connection.execute("ALTER TABLE user ADD COLUMN recovery_phone VARCHAR(20)")
                            
                            print("Columns added. Now refreshing metadata...")
                        else:
                            print("Database schema has the required columns.")
                else:
                    print(f"Database file NOT found at: {db_path}")
            
            # Now, recreate the metadata with what's actually in the database
            print("\nRefreshing SQLAlchemy metadata...")
            
            # Reflect the actual schema from the database
            metadata = MetaData()
            metadata.reflect(bind=db.engine)
            
            # Let's inspect and print what SQLAlchemy now sees
            if 'user' in metadata.tables:
                user_table = metadata.tables['user']
                print("\nUser table columns according to SQLAlchemy:")
                for column in user_table.columns:
                    print(f" - {column.name} ({column.type})")
            
            # Refresh the engine and session
            print("\nRefreshing engine and session...")
            db.Model.metadata = metadata
            
            # Create a test query to verify
            print("\nTesting a query to check if everything is working...")
            from models import User
            user_count = User.query.count()
            print(f"Number of users in database: {user_count}")
            
            print("\nMetadata refresh completed successfully!")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    refresh_sqlalchemy_metadata() 