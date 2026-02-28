from app import app
from models import User
from werkzeug.security import check_password_hash

def verify_final():
    with app.app_context():
        email = 'alidaniyal555@gmail.com'
        password = 'Alidani555???'
        
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User found: {user.username} ({user.email})")
            if check_password_hash(user.password, password):
                print("✅ Password verified successfully!")
            else:
                print("❌ Password verification failed!")
        else:
            print(f"❌ User with email {email} not found in the current database context.")

if __name__ == '__main__':
    verify_final()
