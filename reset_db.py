from app import app, db
from models import User, Deposit, Earning, Withdrawal, Notification, Referral
import os

def reset_database():
    """Reset the database and create tables with the updated schema"""
    with app.app_context():
        try:
            # Get the database URI
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"Using database: {db_uri}")
            
            # For SQLite databases, delete the file if it exists
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    print(f"Removing existing database file: {db_path}")
                    os.remove(db_path)
            
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
            # Create sample admin user if needed
            admin = User.query.filter_by(id=1).first()
            if not admin:
                from werkzeug.security import generate_password_hash
                admin_user = User(
                    id=1,
                    email='admin@example.com',
                    username='admin',
                    password=generate_password_hash('adminpassword'),
                    referral_code='ADMIN123'
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created!")
            
            print("Database reset and migration completed successfully!")
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    reset_database() 