from flask import Flask
from extensions import db
from models import User, Deposit, Earning, Withdrawal, Notification
from models import Referral, DeletedAccount, PasswordReset, ProfitCollection
from models import ReferralBonus, TwoFactorAuth
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///investment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def rebuild_database():
    with app.app_context():
        # Check if database file exists and back it up
        if os.path.exists('investment.db'):
            try:
                # Make a backup
                import shutil
                print("Creating backup of existing database...")
                shutil.copy2('investment.db', 'investment.db.bak')
                print("Backup created as investment.db.bak")
            except Exception as e:
                print(f"Warning: Could not create backup: {str(e)}")
                return
        
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables with new schema...")
        db.create_all()
        
        print("Database schema has been rebuilt successfully.")
        print("IMPORTANT: You will need to restore your data or recreate it.")

if __name__ == '__main__':
    while True:
        confirm = input("This will DELETE ALL DATA and rebuild the schema. Are you sure? (yes/no): ")
        if confirm.lower() == 'yes':
            rebuild_database()
            break
        elif confirm.lower() == 'no':
            print("Operation cancelled.")
            break
        else:
            print("Please enter 'yes' or 'no'.") 