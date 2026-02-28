from flask import Flask
from extensions import db
from models import User, TwoFactorAuth
import traceback

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///investment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def test_user_model():
    with app.app_context():
        try:
            print("Testing User model...")
            # Attempt to query a user
            user = User.query.first()
            
            if user:
                print(f"Successfully retrieved user: {user.username} (ID: {user.id})")
                print(f"User attributes:")
                print(f"  - email: {user.email}")
                print(f"  - two_factor_enabled: {user.two_factor_enabled}")
                print(f"  - referral_code: {user.referral_code}")
            else:
                print("No users found in the database.")
            
            print("\nTesting TwoFactorAuth model...")
            # Attempt to query 2FA records
            tfa = TwoFactorAuth.query.first()
            
            if tfa:
                print(f"Successfully retrieved 2FA record for user ID: {tfa.user_id}")
                print(f"2FA attributes:")
                print(f"  - secret_key: {tfa.secret_key[:5]}... (truncated)")
                print(f"  - created_at: {tfa.created_at}")
            else:
                print("No 2FA records found in the database.")
            
            print("\nAll SQLAlchemy model tests passed!")
            
        except Exception as e:
            print(f"Error testing SQLAlchemy models: {str(e)}")
            traceback.print_exc()

if __name__ == '__main__':
    test_user_model() 