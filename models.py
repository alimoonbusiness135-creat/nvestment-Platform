from extensions import db
from flask_login import UserMixin
from datetime import datetime
import uuid

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    fullname = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    profile_image = db.Column(db.String(100), nullable=True, default='default.jpg')
    
    # Two-factor authentication
    two_factor_enabled = db.Column(db.Boolean, default=False)
    
    # Recovery information
    recovery_email = db.Column(db.String(120), nullable=True)
    recovery_phone = db.Column(db.String(20), nullable=True)
    
    # Financial information
    deposit_balance = db.Column(db.Float, default=0.0)
    earning_balance = db.Column(db.Float, default=0.0)
    total_withdrawn = db.Column(db.Float, default=0.0)
    
    # Referral system
    referral_code = db.Column(db.String(10), unique=True, nullable=False)
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deposits = db.relationship('Deposit', backref='user', lazy=True)
    earnings = db.relationship('Earning', backref='user', lazy=True)
    withdrawals = db.relationship('Withdrawal', backref='user', lazy=True)
    referrals = db.relationship('Referral', backref='referrer', lazy=True, foreign_keys='Referral.referrer_id')
    children = db.relationship('User', backref=db.backref('parent', remote_side=[id]), lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    two_factor = db.relationship('TwoFactorAuth', backref='user', uselist=False, lazy=True)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.referral_code:
            self.referral_code = ''.join(str(uuid.uuid4().int)[:8])
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    transaction_id = db.Column(db.String(100), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    earnings = db.relationship('Earning', backref='deposit', lazy=True)
    
    def __repr__(self):
        return f"Deposit(User: {self.user_id}, Amount: ${self.amount}, Status: {self.status})"

class Earning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deposit_id = db.Column(db.Integer, db.ForeignKey('deposit.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Earning(User: {self.user_id}, Amount: ${self.amount})"

class Withdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    payment_method = db.Column(db.String(50), nullable=True)
    wallet_address = db.Column(db.String(100), nullable=True)
    transaction_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"Withdrawal(User: {self.user_id}, Amount: ${self.amount}, Status: {self.status})"

class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    commission = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Referral(Referrer: {self.referrer_id}, Referred: {self.referred_id}, Level: {self.level})"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    is_global = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Notification(User: {self.user_id}, Title: {self.title})"

class DeletedAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_by = db.Column(db.String(20), default="user")  # "user" or "admin"
    reason = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"DeletedAccount('{self.username}', '{self.email}', deleted at '{self.deleted_at}')"

class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"PasswordReset('{self.email}', '{self.token}')"

class ProfitCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('profit_collections', lazy=True))
    
    def __repr__(self):
        return f"ProfitCollection(User: {self.user_id}, Amount: ${self.amount}, Collected: {self.collected_at})"

class ReferralBonus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    milestone = db.Column(db.Integer, nullable=False)  # 50 or 100 referrals
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, claimed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    claimed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('referral_bonuses', lazy=True))
    
    def __repr__(self):
        return f"ReferralBonus(User: {self.user_id}, Milestone: {self.milestone}, Amount: ${self.amount}, Status: {self.status})"

class TwoFactorAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    secret_key = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    backup_codes = db.Column(db.Text, nullable=True)  # Stored as JSON string
    
    def __repr__(self):
        return f"TwoFactorAuth(User: {self.user_id}, Created: {self.created_at})" 