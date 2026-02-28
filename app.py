from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import uuid
import secrets
from apscheduler.schedulers.background import BackgroundScheduler
from extensions import db, login_manager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-key-for-dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///investment.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)

# Import models - must be done after db is defined
from models import User, Deposit, Earning, Withdrawal, Notification, Referral, TwoFactorAuth

# Make sure SQLAlchemy's metadata reflects the actual database schema
with app.app_context():
    db.create_all()  # This will create any missing tables and columns
    print("Database tables created/updated.")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add a context processor for passing variables to templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.context_processor
def inject_unread_notifications():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter(
            ((Notification.user_id == current_user.id) | (Notification.is_global == True)) &
            (Notification.is_read == False)
        ).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}

# Function to create tables (replaces @app.before_first_request)
def create_tables():
    with app.app_context():
        db.create_all()
        print("All database tables have been created.")

# Function to calculate daily earnings
def calculate_daily_earnings():
    with app.app_context():
        # Get all active deposits
        active_deposits = Deposit.query.filter_by(status='approved').all()
        
        for deposit in active_deposits:
            # Calculate 2% daily earnings
            daily_amount = deposit.amount * 0.02
            
            # Create earning record
            earning = Earning(
                user_id=deposit.user_id,
                deposit_id=deposit.id,
                amount=daily_amount,
                description="Daily earning (2%)"
            )
            
            # Update user's earning balance
            user = User.query.get(deposit.user_id)
            user.earning_balance += daily_amount
            
            db.session.add(earning)
        
        db.session.commit()
        print(f"Daily earnings calculated at {datetime.now()}")

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=calculate_daily_earnings, trigger="interval", hours=24)
scheduler.start()

if __name__ == '__main__':
    # Create tables before running app
    create_tables()
    
    # Import routes here to avoid circular imports
    from routes import *
    from admin_routes import *
    from two_factor_routes import *
    
    app.run(debug=True, port=5000, host='0.0.0.0') 