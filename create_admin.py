from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create an admin user in the database"""
    with app.app_context():
        try:
            # Check if admin user already exists
            admin = User.query.filter_by(id=1).first()
            
            if admin:
                print(f"Admin user already exists: {admin.username} ({admin.email})")
                return
            
            # Create new admin user
            admin_user = User(
                id=1,
                email='alidaniyal555@gmail.com',
                username='admin',
                password=generate_password_hash('Alidani555???'),
                fullname='Admin User',
                recovery_email='admin_recovery@example.com',
                recovery_phone='+1234567890',
                referral_code='ADMIN123'
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("Admin user created successfully!")
            print(f"Username: {admin_user.username}")
            print(f"Password: Alidani555???")
            print(f"Email: {admin_user.email}")
            
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_admin_user() 