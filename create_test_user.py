from flask import Flask
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///investment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_test_user():
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(email='test@example.com').first()
        if existing_user:
            print(f"Test user already exists: {existing_user.username} (ID: {existing_user.id})")
            return
        
        # Create new test user
        hashed_password = generate_password_hash('password123')
        test_user = User(
            email='test@example.com',
            username='testuser',
            password=hashed_password,
            fullname='Test User',
            phone='+1234567890',
            two_factor_enabled=False
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        print(f"Test user created successfully: {test_user.username} (ID: {test_user.id})")
        print(f"Login credentials: email=test@example.com, password=password123")

if __name__ == '__main__':
    create_test_user() 