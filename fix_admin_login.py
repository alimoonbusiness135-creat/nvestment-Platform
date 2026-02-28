from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def fix_admin():
    with app.app_context():
        admin = User.query.filter_by(id=1).first()
        if admin:
            admin.email = 'alidaniyal555@gmail.com'
            admin.password = generate_password_hash('Alidani555???')
            db.session.commit()
            print("Successfully updated admin email and hashed password using Werkzeug.")
            print(f"Email: {admin.email}")
            print(f"Password stored (first 20 chars): {admin.password[:20]}...")
        else:
            print("Admin user not found.")

if __name__ == '__main__':
    fix_admin()
