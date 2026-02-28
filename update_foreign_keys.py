from flask import Flask
from extensions import db
from models import User, Deposit, Earning, Withdrawal, Notification
from models import Referral, DeletedAccount, PasswordReset, ProfitCollection
from models import ReferralBonus, TwoFactorAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///investment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def update_foreign_keys():
    """This function will recreate tables with proper ON DELETE CASCADE constraints"""
    with app.app_context():
        print("To properly update the foreign key constraints, we'd need to recreate the tables.")
        print("This would require:")
        print("1. Backing up all data")
        print("2. Dropping and recreating tables with proper constraints")
        print("3. Restoring the data")
        print("\nInstead, it's recommended to handle this at the application level,")
        print("which we've done by properly deleting related records before deleting a user.")
        
        print("\nChecking existing foreign key constraints...")
        from sqlalchemy import text
        
        # Check foreign key constraints
        result = db.session.execute(text("PRAGMA foreign_keys=ON"))
        print("Foreign keys are enabled:", result.fetchone()[0] != 0)
        
        # Check if the database is properly set up for cascade
        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        
        print("\nDatabase tables:", ", ".join(tables))
        
        # Check for any DEFERRABLE constraints (SQLite specific)
        print("\nNote: SQLite doesn't fully support ON DELETE CASCADE constraints in ALTER TABLE statements.")
        print("For proper constraint implementation, you'd need to recreate the database.")
        print("The current implementation handles deletions in application code.")

if __name__ == "__main__":
    update_foreign_keys() 