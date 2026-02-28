from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def reset_admin():
    with app.app_context():
        email = 'alidaniyal555@gmail.com'
        password = 'Alidani555???'
        
        # Try to find the admin by id or email
        admin = User.query.filter_by(id=1).first() or User.query.filter_by(email=email).first()
        
        if admin:
            admin.email = email
            admin.password = generate_password_hash(password)
            db.session.commit()
            print(f"Admin updated! Email: {email}, Password: {password}")
        else:
            new_admin = User(
                id=1,
                email=email,
                username='admin',
                password=generate_password_hash(password),
                referral_code='ADMIN123'
            )
            db.session.add(new_admin)
            db.session.commit()
            print(f"New Admin created! Email: {email}, Password: {password}")

if __name__ == "__main__":
    reset_admin()
