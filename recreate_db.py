from app import app, db
from models import User
from werkzeug.security import generate_password_hash
import os

def recreate_database():
    """Delete and recreate the database from scratch"""
    with app.app_context():
        try:
            # Get database path
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                
                # Delete the database file if it exists
                if os.path.exists(db_path):
                    print(f"Removing existing database: {db_path}")
                    os.remove(db_path)
            
            # Create all tables from scratch
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
            # Create admin user
            admin_user = User(
                id=1,
                email='admin@example.com',
                username='admin',
                password=generate_password_hash('adminpassword'),
                fullname='Admin User',
                recovery_email='admin_recovery@example.com',
                recovery_phone='+1234567890',
                referral_code='ADMIN123'
            )
            
            # Create a test user
            test_user = User(
                id=2,
                email='test@example.com',
                username='testuser',
                password=generate_password_hash('testpassword'),
                fullname='Test User',
                recovery_email='test_recovery@example.com',
                recovery_phone='+9876543210',
                referral_code='TEST1234'
            )
            
            # Add users to database
            db.session.add(admin_user)
            db.session.add(test_user)
            db.session.commit()
            
            print("Users created successfully:")
            print(f"Admin - Username: {admin_user.username}, Password: adminpassword")
            print(f"Test User - Username: {test_user.username}, Password: testpassword")
            
            print("Database has been completely recreated!")
            
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    recreate_database() 