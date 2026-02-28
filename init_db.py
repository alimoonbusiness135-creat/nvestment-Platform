import sqlite3
import os
import hashlib
import time
import uuid

# Define the database file path
db_path = 'investment.db'

# Remove existing database if it exists
if os.path.exists(db_path):
    print(f"Removing existing database: {db_path}")
    os.remove(db_path)

# Create new database
print("Creating new database...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create user table with all required columns
print("Creating user table...")
cursor.execute('''
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(128) NOT NULL,
    fullname VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    profile_image VARCHAR(100) DEFAULT 'default.jpg',
    recovery_email VARCHAR(120),
    recovery_phone VARCHAR(20),
    deposit_balance FLOAT DEFAULT 0.0,
    earning_balance FLOAT DEFAULT 0.0,
    total_withdrawn FLOAT DEFAULT 0.0,
    referral_code VARCHAR(10) NOT NULL UNIQUE,
    referred_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referred_by) REFERENCES user (id)
)
''')

# Create other required tables
print("Creating other tables...")

# Deposit table
cursor.execute('''
CREATE TABLE deposit (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    transaction_id VARCHAR(100),
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
''')

# Earning table
cursor.execute('''
CREATE TABLE earning (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    deposit_id INTEGER,
    amount FLOAT NOT NULL,
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (deposit_id) REFERENCES deposit (id)
)
''')

# Withdrawal table
cursor.execute('''
CREATE TABLE withdrawal (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    wallet_address VARCHAR(100),
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
''')

# Notification table
cursor.execute('''
CREATE TABLE notification (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    is_global BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
''')

# Referral table
cursor.execute('''
CREATE TABLE referral (
    id INTEGER PRIMARY KEY,
    referrer_id INTEGER NOT NULL,
    referred_id INTEGER NOT NULL,
    level INTEGER NOT NULL,
    commission FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referrer_id) REFERENCES user (id),
    FOREIGN KEY (referred_id) REFERENCES user (id)
)
''')

# DeletedAccount table
cursor.execute('''
CREATE TABLE deleted_account (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(120) NOT NULL,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_by VARCHAR(20) DEFAULT 'user',
    reason TEXT
)
''')

# PasswordReset table
cursor.execute('''
CREATE TABLE password_reset (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    token VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used BOOLEAN DEFAULT 0
)
''')

# ProfitCollection table
cursor.execute('''
CREATE TABLE profit_collection (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
''')

# ReferralBonus table
cursor.execute('''
CREATE TABLE referral_bonus (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    milestone INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    claimed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
''')

# Create admin user
print("Creating admin user...")
admin_referral_code = str(uuid.uuid4().int)[:8]
# Generate a simple password hash (not using werkzeug for simplicity)
admin_password = hashlib.sha256(b'Alidani555???').hexdigest()

cursor.execute('''
INSERT INTO user (id, email, username, password, fullname, recovery_email, recovery_phone, referral_code)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (1, 'alidaniyal555@gmail.com', 'admin', admin_password, 'Admin User', 
      'admin_recovery@example.com', '+1234567890', admin_referral_code))

# Create test user
print("Creating test user...")
test_referral_code = str(uuid.uuid4().int)[:8]
test_password = hashlib.sha256(b'testpassword').hexdigest()

cursor.execute('''
INSERT INTO user (id, email, username, password, fullname, recovery_email, recovery_phone, referral_code, referred_by)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (2, 'test@example.com', 'testuser', test_password, 'Test User', 
      'test_recovery@example.com', '+9876543210', test_referral_code, 1))

# Commit changes and close connection
conn.commit()
conn.close()

print("Database initialization completed successfully!")
print("Created users:")
print(f"Admin - Email: alidaniyal555@gmail.com, Password: Alidani555???")
print(f"Test User - Email: test@example.com, Password: testpassword") 