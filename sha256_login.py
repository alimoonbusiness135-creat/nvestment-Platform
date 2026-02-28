import hashlib
import sqlite3
import os
from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_login import LoginManager, login_user

app = Flask(__name__)
app.secret_key = 'testing_key'

# Set up database connection
def get_db_connection():
    conn = sqlite3.connect('investment.db')
    conn.row_factory = sqlite3.Row
    return conn

# Custom User class for flask-login
class User:
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return str(self.id)

# Test login with SHA-256 hash
def test_login(email, password):
    # Hash the password with SHA-256
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Connect to the database
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM user WHERE email = ?', (email,)
    ).fetchone()
    conn.close()
    
    if user and user['password'] == password_hash:
        return User(user['id'], user['username'], user['email'])
    return None

# Run the test
def run_test():
    # Test admin login
    admin_email = 'admin@example.com'
    admin_password = 'adminpassword'
    admin_user = test_login(admin_email, admin_password)
    
    if admin_user:
        print(f"✅ Admin login successful: {admin_user.username}")
        
        # Verify all fields including recovery information
        conn = get_db_connection()
        admin_data = conn.execute(
            'SELECT * FROM user WHERE id = ?', (admin_user.id,)
        ).fetchone()
        conn.close()
        
        print("\nAdmin User Data:")
        for key in admin_data.keys():
            print(f"{key}: {admin_data[key]}")
    else:
        print("❌ Admin login failed!")
    
    # Test regular user login
    user_email = 'test@example.com'
    user_password = 'testpassword'
    test_user = test_login(user_email, user_password)
    
    if test_user:
        print(f"\n✅ Test user login successful: {test_user.username}")
        
        # Verify all fields including recovery information
        conn = get_db_connection()
        user_data = conn.execute(
            'SELECT * FROM user WHERE id = ?', (test_user.id,)
        ).fetchone()
        conn.close()
        
        print("\nTest User Data:")
        for key in user_data.keys():
            print(f"{key}: {user_data[key]}")
    else:
        print("\n❌ Test user login failed!")

if __name__ == "__main__":
    run_test() 