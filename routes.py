from flask import render_template, redirect, url_for, flash, request, jsonify, abort, session
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
import datetime
from app import app
from extensions import db
from models import User, Deposit, Earning, Withdrawal, Notification, Referral, DeletedAccount, PasswordReset, ProfitCollection, ReferralBonus
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
import os

# Helper functions
def get_user_referrals(user_id):
    # Level 1 referrals (direct)
    level1 = User.query.filter_by(referred_by=user_id).all()
    level1_count = len(level1)
    
    # Level 2 referrals
    level2_count = 0
    for ref in level1:
        level2_count += User.query.filter_by(referred_by=ref.id).count()
    
    # Level 3 referrals
    level3_count = 0
    for ref in level1:
        level2_refs = User.query.filter_by(referred_by=ref.id).all()
        for ref2 in level2_refs:
            level3_count += User.query.filter_by(referred_by=ref2.id).count()
    
    return {
        'level1': level1_count,
        'level2': level2_count,
        'level3': level3_count,
        'total': level1_count + level2_count + level3_count
    }

def calculate_referral_commission(user_id, deposit_amount):
    user = User.query.get(user_id)
    if not user or not user.referred_by:
        return
    
    # Level 1 (direct) - 5%
    level1_referrer = User.query.get(user.referred_by)
    if level1_referrer:
        commission_amount = deposit_amount * 0.05
        level1_referrer.earning_balance += commission_amount
        
        # Create referral record
        referral = Referral(
            referrer_id=level1_referrer.id,
            referred_id=user_id,
            level=1,
            commission=commission_amount
        )
        db.session.add(referral)
        
        # Create earning record for commission
        earning = Earning(
            user_id=level1_referrer.id,
            amount=commission_amount,
            description=f"Level 1 referral commission from {user.username}"
        )
        db.session.add(earning)
        
        # Level 2 - 2%
        if level1_referrer.referred_by:
            level2_referrer = User.query.get(level1_referrer.referred_by)
            if level2_referrer:
                commission_amount = deposit_amount * 0.02
                level2_referrer.earning_balance += commission_amount
                
                # Create referral record
                referral = Referral(
                    referrer_id=level2_referrer.id,
                    referred_id=user_id,
                    level=2,
                    commission=commission_amount
                )
                db.session.add(referral)
                
                # Create earning record for commission
                earning = Earning(
                    user_id=level2_referrer.id,
                    amount=commission_amount,
                    description=f"Level 2 referral commission from {user.username}"
                )
                db.session.add(earning)
                
                # Level 3 - 1%
                if level2_referrer.referred_by:
                    level3_referrer = User.query.get(level2_referrer.referred_by)
                    if level3_referrer:
                        commission_amount = deposit_amount * 0.01
                        level3_referrer.earning_balance += commission_amount
                        
                        # Create referral record
                        referral = Referral(
                            referrer_id=level3_referrer.id,
                            referred_id=user_id,
                            level=3,
                            commission=commission_amount
                        )
                        db.session.add(referral)
                        
                        # Create earning record for commission
                        earning = Earning(
                            user_id=level3_referrer.id,
                            amount=commission_amount,
                            description=f"Level 3 referral commission from {user.username}"
                        )
                        db.session.add(earning)
    
    db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/animation-demo')
def animation_demo():
    """Route for the animation demonstration page"""
    return render_template('animation_demo.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        referral_code = request.form.get('referral_code')
        
        # Validation
        if not all([email, username, password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        # Check if email or username exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hashed_password)
        
        # If referral code was provided, process it
        if referral_code:
            referrer = User.query.filter_by(referral_code=referral_code).first()
            if referrer:
                new_user.referred_by = referrer.id
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    # Get referral code from query string if it exists
    referral_code = request.args.get('ref', '')
    return render_template('register.html', referral_code=referral_code)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not email or not password:
            flash('Please enter both email and password', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        # Check for werkzeug password hash
        is_valid_password = check_password_hash(user.password, password)
        
        # If not valid, check for SHA-256 hash (for compatibility with direct DB setup)
        if not is_valid_password:
            import hashlib
            sha256_hash = hashlib.sha256(password.encode()).hexdigest()
            is_valid_password = (user.password == sha256_hash)
        
        if not is_valid_password:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        # Check if two-factor auth is enabled for this user
        if user.two_factor_enabled:
            # Store user ID in session for the 2FA verification step
            session['two_factor_user_id'] = user.id
            # Store next URL if there is one
            next_page = request.args.get('next')
            if next_page:
                session['next_url'] = next_page
            
            # Redirect to 2FA verification page
            return redirect(url_for('verify_2fa'))
        
        # If 2FA is not enabled, complete the login
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        
        flash('Logged in successfully!', 'success')
        return redirect(next_page or url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's active deposits
    active_deposits = Deposit.query.filter_by(user_id=current_user.id, status='approved').all()
    total_active_deposits = sum(deposit.amount for deposit in active_deposits)
    
    # Calculate daily profit
    daily_profit = total_active_deposits * 0.02
    
    # Check if profit can be collected
    can_collect = True
    hours_remaining = 0
    last_collection = ProfitCollection.query.filter_by(user_id=current_user.id).order_by(ProfitCollection.collected_at.desc()).first()
    
    if last_collection:
        time_since_collection = datetime.datetime.utcnow() - last_collection.collected_at
        if time_since_collection.total_seconds() < 86400:  # 24 hours = 86400 seconds
            can_collect = False
            hours_remaining = 24 - (time_since_collection.total_seconds() / 3600)
    
    # Get recent earnings
    recent_earnings = Earning.query.filter_by(user_id=current_user.id).order_by(Earning.created_at.desc()).limit(5).all()
    
    # Get withdrawal history
    withdrawals = Withdrawal.query.filter_by(user_id=current_user.id).order_by(Withdrawal.created_at.desc()).limit(5).all()
    
    # Get referral data
    referral_stats = get_user_referrals(current_user.id)
    referral_earnings = Referral.query.filter_by(referrer_id=current_user.id).all()
    total_referral_earnings = sum(ref.commission for ref in referral_earnings)
    
    # Check referral bonus eligibility
    direct_referrals = referral_stats['level1']
    progress_50 = min(direct_referrals / 50 * 100, 100)
    progress_100 = min(direct_referrals / 100 * 100, 100)
    
    referral_bonuses = {
        50: {'eligible': direct_referrals >= 50, 'claimed': False, 'amount': 500, 'progress': progress_50},
        100: {'eligible': direct_referrals >= 100, 'claimed': False, 'amount': 1000, 'progress': progress_100}
    }
    
    # Check if bonuses have been claimed
    claimed_bonuses = ReferralBonus.query.filter_by(user_id=current_user.id, status='claimed').all()
    for bonus in claimed_bonuses:
        if bonus.milestone in referral_bonuses:
            referral_bonuses[bonus.milestone]['claimed'] = True
    
    # Get unread notifications
    notifications = Notification.query.filter(
        (Notification.user_id == current_user.id) | (Notification.is_global == True)
    ).filter_by(is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template(
        'dashboard.html',
        active_deposits=active_deposits,
        total_active_deposits=total_active_deposits,
        daily_profit=daily_profit,
        can_collect=can_collect,
        hours_remaining=hours_remaining,
        recent_earnings=recent_earnings,
        withdrawals=withdrawals,
        referral_stats=referral_stats,
        total_referral_earnings=total_referral_earnings,
        referral_bonuses=referral_bonuses,
        notifications=notifications
    )

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method')
        
        # Validation
        if amount < 25 or amount > 5000:
            flash('Deposit amount must be between $25 and $5000', 'danger')
            return redirect(url_for('deposit'))
        
        # Handle file upload
        proof_image_filename = None
        if 'proof_image' in request.files:
            file = request.files['proof_image']
            if file and file.filename != '':
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'deposits')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                # Secure filename and add timestamp to avoid collisions
                filename = secure_filename(file.filename)
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                proof_image_filename = f"{timestamp}_{filename}"
                file.save(os.path.join(upload_dir, proof_image_filename))
        
        # Create deposit record
        deposit = Deposit(
            user_id=current_user.id,
            amount=amount,
            payment_method=payment_method,
            status='pending',
            transaction_id=str(uuid.uuid4()),
            proof_image=proof_image_filename
        )
        
        db.session.add(deposit)
        
        # Create detailed notification for admin
        admin_message = (
            f"NEW DEPOSIT REQUEST\n"
            f"User: {current_user.username} (ID: {current_user.id})\n"
            f"Full Name: {current_user.fullname or 'N/A'}\n"
            f"Email: {current_user.email}\n"
            f"Amount: ${amount}\n"
            f"Method: {payment_method}\n"
            f"Trans ID: {deposit.transaction_id}\n"
            f"Proof SS: {'Uploaded ✅' if proof_image_filename else 'No SS ❌'}"
        )
        admin_notification = Notification(
            user_id=1,  # Assuming admin has ID 1
            title='NEW DEPOSIT REQUEST',
            message=admin_message
        )
        db.session.add(admin_notification)
        db.session.commit()
        
        # Send email notification to admin
        try:
            # Email setup
            sender_email = os.getenv('EMAIL_USER')
            password = os.getenv('EMAIL_PASS')
            admin_email = os.getenv('ADMIN_EMAIL')
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = admin_email
            msg['Subject'] = f"New Deposit Request - {current_user.username}"
            
            body = f"""
            <html>
            <body>
                <h2>New Deposit Request</h2>
                <p>A new deposit request has been submitted and requires your approval.</p>
                <h3>Deposit Details:</h3>
                <ul>
                    <li><strong>User:</strong> {current_user.username} (ID: {current_user.id})</li>
                    <li><strong>Amount:</strong> ${deposit.amount}</li>
                    <li><strong>Payment Method:</strong> {deposit.payment_method}</li>
                    <li><strong>Transaction ID:</strong> {deposit.transaction_id}</li>
                    <li><strong>Date:</strong> {deposit.created_at.strftime('%Y-%m-%d %H:%M')}</li>
                </ul>
                <p>Please log in to the admin panel to review and process this request.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, admin_email, text)
            server.quit()
        except Exception as e:
            app.logger.error(f"Error sending admin notification for deposit: {str(e)}")
        
        # Redirect to deposit details page instead of dashboard
        return redirect(url_for('deposit_details', deposit_id=deposit.id))
    
    return render_template('deposit.html')

@app.route('/deposit-details/<int:deposit_id>')
@login_required
def deposit_details(deposit_id):
    # Get the deposit
    deposit = Deposit.query.get_or_404(deposit_id)
    
    # Check if the deposit belongs to the current user
    if deposit.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Generate payment details based on payment method
    payment_details = {
        'jazzcash': 'Wallet Request Sent (Approve in App)',
        'easypaisa': 'Wallet Request Sent (Approve in App)',
        'binance': 'BNB Smart Chain Address: [Enter Your BNB Address Here]',
        'bitget': 'BNB Smart Chain Address: [Enter Your BNB Address Here]'
    }
    
    # Get the payment detail for the selected payment method
    payment_info = payment_details.get(deposit.payment_method, 'Please contact support for payment details')
    
    return render_template('deposit_details.html', 
                          deposit=deposit, 
                          payment_info=payment_info)

@app.route('/upload-deposit-proof/<int:deposit_id>', methods=['POST'])
@login_required
def upload_deposit_proof(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    
    # Check if the deposit belongs to the current user
    if deposit.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if 'proof_image' in request.files:
        file = request.files['proof_image']
        if file and file.filename != '':
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'deposits')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Secure filename and add timestamp to avoid collisions
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            proof_image_filename = f"{timestamp}_{filename}"
            file.save(os.path.join(upload_dir, proof_image_filename))
            
            # Update deposit record
            deposit.proof_image = proof_image_filename
            db.session.commit()
            
            # Create notification for admin
            admin_message = (
                f"PROOF UPLOADED FOR DEPOSIT\n"
                f"User: {current_user.username} (ID: {current_user.id})\n"
                f"Amount: ${deposit.amount}\n"
                f"Method: {deposit.payment_method}\n"
                f"Trans ID: {deposit.transaction_id}\n"
                f"Status: Proof received! ✅"
            )
            admin_notification = Notification(
                user_id=1,  # Assuming admin has ID 1
                title='DEPOSIT PROOF RECEIVED',
                message=admin_message
            )
            db.session.add(admin_notification)
            db.session.commit()
            
            flash('Payment proof uploaded successfully! Our team will verify it shortly.', 'success')
        else:
            flash('No file selected', 'danger')
    else:
        flash('No file part', 'danger')
        
    return redirect(url_for('deposit_details', deposit_id=deposit.id))

@app.route('/withdrawal', methods=['GET', 'POST'])
@login_required
def withdrawal():
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method')
        wallet_address = request.form.get('wallet_address')
        
        # Validation
        if amount <= 0:
            flash('Withdrawal amount must be greater than zero', 'danger')
            return redirect(url_for('withdrawal'))
        
        if amount < 30 or amount > 5000:
            flash('Withdrawal amount must be between $30 and $5000', 'danger')
            return redirect(url_for('withdrawal'))
        
        if amount > current_user.earning_balance:
            flash('Insufficient balance for withdrawal', 'danger')
            return redirect(url_for('withdrawal'))
        
        # Create withdrawal record
        withdrawal = Withdrawal(
            user_id=current_user.id,
            amount=amount,
            payment_method=payment_method,
            wallet_address=wallet_address,
            status='pending'
        )
        
        # Update user's balance
        current_user.earning_balance -= amount
        
        db.session.add(withdrawal)
        
        # Create detailed notification for admin
        admin_message = (
            f"NEW WITHDRAWAL REQUEST\n"
            f"User: {current_user.username} (ID: {current_user.id})\n"
            f"Full Name: {current_user.fullname or 'N/A'}\n"
            f"Email: {current_user.email}\n"
            f"Amount: ${amount}\n"
            f"Method: {payment_method}\n"
            f"Details/Wallet: {wallet_address}"
        )
        admin_notification = Notification(
            user_id=1,  # Assuming admin has ID 1
            title='NEW WITHDRAWAL REQUEST',
            message=admin_message
        )
        db.session.add(admin_notification)
        db.session.commit()
        
        # Send email notification to admin
        try:
            # Email setup
            sender_email = os.getenv('EMAIL_USER')
            password = os.getenv('EMAIL_PASS')
            admin_email = os.getenv('ADMIN_EMAIL')
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = admin_email
            msg['Subject'] = f"New Withdrawal Request - {current_user.username}"
            
            body = f"""
            <html>
            <body>
                <h2>New Withdrawal Request</h2>
                <p>A new withdrawal request has been submitted and requires your approval.</p>
                <h3>Withdrawal Details:</h3>
                <ul>
                    <li><strong>User:</strong> {current_user.username} (ID: {current_user.id})</li>
                    <li><strong>Amount:</strong> ${withdrawal.amount}</li>
                    <li><strong>Payment Method:</strong> {withdrawal.payment_method}</li>
                    <li><strong>Wallet Address:</strong> {withdrawal.wallet_address}</li>
                    <li><strong>Date:</strong> {withdrawal.created_at.strftime('%Y-%m-%d %H:%M')}</li>
                </ul>
                <p>Please log in to the admin panel to review and process this request.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, admin_email, text)
            server.quit()
        except Exception as e:
            app.logger.error(f"Error sending admin notification for withdrawal: {str(e)}")
        
        flash('Withdrawal request submitted successfully! Awaiting approval.', 'success')
        return redirect(url_for('dashboard'))
    
    withdrawals = Withdrawal.query.filter_by(user_id=current_user.id).order_by(Withdrawal.created_at.desc()).all()
    return render_template('withdrawal.html', withdrawals=withdrawals)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Check if username is already taken
        if username != current_user.username and User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('profile'))
        
        # Update user information
        current_user.fullname = fullname
        current_user.username = username
        current_user.phone = phone
        current_user.address = address
        
        # Handle profile image upload
        if 'profile_image' in request.files:
            profile_image = request.files['profile_image']
            if profile_image.filename:
                # Ensure the upload directory exists
                profiles_dir = os.path.join(app.root_path, 'static/images/profiles')
                if not os.path.exists(profiles_dir):
                    os.makedirs(profiles_dir)
                
                filename = secure_filename(f"{current_user.id}_{profile_image.filename}")
                profile_image.save(os.path.join(profiles_dir, filename))
                current_user.profile_image = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Get user history
    deposits = Deposit.query.filter_by(user_id=current_user.id).order_by(Deposit.created_at.desc()).all()
    earnings = Earning.query.filter_by(user_id=current_user.id).order_by(Earning.created_at.desc()).all()
    withdrawals = Withdrawal.query.filter_by(user_id=current_user.id).order_by(Withdrawal.created_at.desc()).all()
    
    return render_template(
        'profile.html', 
        deposits=deposits,
        earnings=earnings,
        withdrawals=withdrawals
    )

@app.route('/referrals')
@login_required
def referrals():
    referral_link = f"{request.host_url}register?ref={current_user.referral_code}"
    
    # Get referral statistics
    referral_stats = get_user_referrals(current_user.id)
    
    # Get referral earnings
    referral_earnings = Referral.query.filter_by(referrer_id=current_user.id).order_by(Referral.created_at.desc()).all()
    total_referral_earnings = sum(ref.commission for ref in referral_earnings)
    
    # Get direct referrals
    direct_referrals = User.query.filter_by(referred_by=current_user.id).all()
    
    # Create a dictionary of referred users for easy lookup in the template
    referred_ids = [earning.referred_id for earning in referral_earnings]
    referred_users_list = User.query.filter(User.id.in_(referred_ids)).all() if referred_ids else []
    referred_users = {user.id: user for user in referred_users_list}
    
    return render_template(
        'referrals.html',
        referral_link=referral_link,
        referral_stats=referral_stats,
        referral_earnings=referral_earnings,
        total_referral_earnings=total_referral_earnings,
        direct_referrals=direct_referrals,
        referred_users=referred_users
    )

@app.route('/notifications')
@login_required
def notifications():
    # Mark notifications as read
    unread_notifications = Notification.query.filter(
        ((Notification.user_id == current_user.id) | (Notification.is_global == True)) &
        (Notification.is_read == False)
    ).all()
    
    for notification in unread_notifications:
        notification.is_read = True
    
    db.session.commit()
    
    # Get all notifications for the user
    user_notifications = Notification.query.filter(
        (Notification.user_id == current_user.id) | (Notification.is_global == True)
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/collect-profit', methods=['POST'])
@login_required
def collect_profit():
    # Check if user has active deposits
    active_deposits = Deposit.query.filter_by(user_id=current_user.id, status='approved').all()
    
    if not active_deposits:
        flash('You have no active deposits to collect profit from.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check if user has collected profit in the last 24 hours
    last_collection = ProfitCollection.query.filter_by(user_id=current_user.id).order_by(ProfitCollection.collected_at.desc()).first()
    
    if last_collection:
        time_since_collection = datetime.datetime.utcnow() - last_collection.collected_at
        if time_since_collection.total_seconds() < 86400:  # 24 hours = 86400 seconds
            hours_remaining = 24 - (time_since_collection.total_seconds() / 3600)
            flash(f'You have already collected your profit today. Please wait {hours_remaining:.1f} hours.', 'warning')
            return redirect(url_for('dashboard'))
    
    # Calculate daily profit (2% of total deposits)
    total_deposits = sum(deposit.amount for deposit in active_deposits)
    daily_profit = total_deposits * 0.02
    
    # Add profit to user's earning balance
    current_user.earning_balance += daily_profit
    
    # Record profit collection
    profit_collection = ProfitCollection(
        user_id=current_user.id,
        amount=daily_profit
    )
    
    # Create earning record
    earning = Earning(
        user_id=current_user.id,
        amount=daily_profit,
        description="Daily profit collection"
    )
    
    db.session.add(profit_collection)
    db.session.add(earning)
    db.session.commit()
    
    flash(f'Successfully collected ${daily_profit:.2f} profit!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Check if it's a password change request
        if 'current_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validation
            if not check_password_hash(current_user.password, current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('settings'))
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return redirect(url_for('settings'))
            
            # Update password
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            
            flash('Password updated successfully!', 'success')
            return redirect(url_for('settings'))
        
        # Check if it's a recovery information update
        elif 'recovery_email' in request.form or 'recovery_phone' in request.form:
            recovery_email = request.form.get('recovery_email')
            recovery_phone = request.form.get('recovery_phone')
            
            # Validation
            if recovery_email and recovery_email == current_user.email:
                flash('Recovery email must be different from your primary email', 'danger')
                return redirect(url_for('settings'))
            
            # Update recovery information
            current_user.recovery_email = recovery_email
            current_user.recovery_phone = recovery_phone
            db.session.commit()
            
            # Create notification for the user
            notification = Notification(
                user_id=current_user.id,
                title='Recovery Information Updated',
                message='Your account recovery information has been updated successfully.'
            )
            db.session.add(notification)
            db.session.commit()
            
            flash('Recovery information updated successfully!', 'success')
            return redirect(url_for('settings'))
    
    return render_template('settings.html')

@app.route('/claim-referral-bonus', methods=['POST'])
@login_required
def claim_referral_bonus():
    milestone = int(request.form.get('milestone', 0))
    
    # Validate milestone
    if milestone not in [50, 100]:
        flash('Invalid milestone specified.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get referral count
    referral_stats = get_user_referrals(current_user.id)
    direct_referrals = referral_stats['level1']
    
    # Check if user has already claimed this bonus
    existing_bonus = ReferralBonus.query.filter_by(
        user_id=current_user.id, 
        milestone=milestone,
        status='claimed'
    ).first()
    
    if existing_bonus:
        flash(f'You have already claimed the ${milestone * 10} bonus for {milestone} referrals.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check if user qualifies for the bonus
    if direct_referrals < milestone:
        flash(f'You need {milestone - direct_referrals} more direct referrals to claim this bonus.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Calculate bonus amount
    bonus_amount = 500 if milestone == 50 else 1000
    
    # Add bonus to user's earning balance
    current_user.earning_balance += bonus_amount
    
    # Create bonus record
    bonus = ReferralBonus(
        user_id=current_user.id,
        milestone=milestone,
        amount=bonus_amount,
        status='claimed',
        claimed_at=datetime.datetime.now()
    )
    
    # Create earning record
    earning = Earning(
        user_id=current_user.id,
        amount=bonus_amount,
        description=f"Bonus for referring {milestone} users"
    )
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        title=f"Referral Bonus Claimed",
        message=f"Congratulations! You've received a ${bonus_amount} bonus for referring {milestone} users."
    )
    
    db.session.add(bonus)
    db.session.add(earning)
    db.session.add(notification)
    db.session.commit()
    
    flash(f'Congratulations! ${bonus_amount} bonus has been added to your balance.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    # Check if the user confirmed deletion
    if not request.form.get('confirm_delete'):
        flash('You must confirm that you understand the consequences of account deletion', 'danger')
        return redirect(url_for('settings'))
    
    # Verify user password
    password = request.form.get('delete_password')
    if not check_password_hash(current_user.password, password):
        flash('Incorrect password', 'danger')
        return redirect(url_for('settings'))
    
    # Store user info for record keeping
    user_id = current_user.id
    username = current_user.username
    email = current_user.email
    
    try:
        # Create a record of the deleted account
        deleted_record = DeletedAccount(
            username=username,
            email=email,
            deleted_by="user",
            reason="User requested account deletion"
        )
        db.session.add(deleted_record)
        
        # Delete two-factor auth record if it exists
        if hasattr(current_user, 'two_factor') and current_user.two_factor:
            db.session.delete(current_user.two_factor)
        
        # Delete profit collections
        ProfitCollection.query.filter_by(user_id=user_id).delete()
        
        # Delete referral bonuses
        ReferralBonus.query.filter_by(user_id=user_id).delete()
        
        # Delete user notifications
        Notification.query.filter_by(user_id=user_id).delete()
        
        # Delete user deposits
        Deposit.query.filter_by(user_id=user_id).delete()
        
        # Delete user earnings
        Earning.query.filter_by(user_id=user_id).delete()
        
        # Delete user withdrawals
        Withdrawal.query.filter_by(user_id=user_id).delete()
        
        # Delete user referrals where they are referrer or referred
        Referral.query.filter_by(referrer_id=user_id).delete()
        Referral.query.filter_by(referred_id=user_id).delete()
        
        # Update any users that were referred by this user
        referred_users = User.query.filter_by(referred_by=user_id).all()
        for referred_user in referred_users:
            referred_user.referred_by = None
        
        # Commit the deletions first to avoid constraint issues
        db.session.commit()
        
        # Now delete the user
        db.session.delete(current_user)
        db.session.commit()
        
        # Log the user out
        logout_user()
        
        flash('Your account has been permanently deleted', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting account for user {username}: {str(e)}")
        flash('An error occurred while deleting your account. Please try again or contact support.', 'danger')
        return redirect(url_for('settings'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        recovery_method = request.form.get('recovery_method')
        
        if recovery_method == 'primary_email':
            email = request.form.get('email')
            
            if not email:
                flash('Please enter your email address', 'danger')
                return redirect(url_for('forgot_password'))
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                flash('No account found with that email address', 'danger')
                return redirect(url_for('forgot_password'))
            
            # Generate a reset token
            token = secrets.token_urlsafe(32)
            
            # Save the token in the database
            reset_record = PasswordReset(email=email, token=token)
            db.session.add(reset_record)
            db.session.commit()
            
            # Send the password reset email
            reset_url = url_for('reset_password', token=token, _external=True)
            
            # Email setup
            sender_email = "dali08091@gmail.com"
            password = "lqpvlctxwwodygqk" 
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = "Password Reset - Investment Platform"
            
            body = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password for your Investment Platform account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>If you did not request this password reset, please ignore this email.</p>
                <p>This link will expire in 24 hours.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.sendmail(sender_email, email, text)
                server.quit()
                
                flash('Password reset instructions have been sent to your email address', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                app.logger.error(f"Error sending password reset email: {str(e)}")
                flash('Error sending password reset email. Please try again later.', 'danger')
                return redirect(url_for('forgot_password'))
        
        elif recovery_method == 'recovery_info':
            recovery_email = request.form.get('recovery_email')
            recovery_phone = request.form.get('recovery_phone')
            
            if not recovery_email and not recovery_phone:
                flash('Please enter either your recovery email or recovery phone number', 'danger')
                return redirect(url_for('forgot_password'))
            
            # Try to find user by recovery information
            user = None
            if recovery_email:
                user = User.query.filter_by(recovery_email=recovery_email).first()
            
            if not user and recovery_phone:
                user = User.query.filter_by(recovery_phone=recovery_phone).first()
            
            if not user:
                flash('No account found with that recovery information', 'danger')
                return redirect(url_for('forgot_password'))
            
            # Generate a reset token
            token = secrets.token_urlsafe(32)
            
            # Save the token in the database
            reset_record = PasswordReset(email=user.email, token=token)
            db.session.add(reset_record)
            db.session.commit()
            
            # Send the password reset email to the user's primary email
            reset_url = url_for('reset_password', token=token, _external=True)
            
            # Email setup
            sender_email = "dali08091@gmail.com"
            password = "lqpvlctxwwodygqk" 
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = user.email
            msg['Subject'] = "Password Reset - Investment Platform"
            
            body = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password for your Investment Platform account using your recovery information.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>If you did not request this password reset, please ignore this email.</p>
                <p>This link will expire in 24 hours.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, password)
                text = msg.as_string()
                server.sendmail(sender_email, user.email, text)
                server.quit()
                
                flash('Password reset instructions have been sent to your primary email address', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                app.logger.error(f"Error sending password reset email: {str(e)}")
                flash('Error sending password reset email. Please try again later.', 'danger')
                return redirect(url_for('forgot_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Check if token exists and is valid
    reset_record = PasswordReset.query.filter_by(token=token, used=False).first()
    
    if not reset_record:
        flash('Invalid or expired password reset link', 'danger')
        return redirect(url_for('login'))
    
    # Check if token is expired (older than 24 hours)
    token_age = datetime.datetime.utcnow() - reset_record.created_at
    if token_age > datetime.timedelta(hours=24):
        reset_record.used = True
        db.session.commit()
        flash('Password reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('reset_password', token=token))
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('reset_password', token=token))
        
        # Update the user's password
        user = User.query.filter_by(email=reset_record.email).first()
        user.password = generate_password_hash(new_password)
        
        # Mark the token as used
        reset_record.used = True
        
        db.session.commit()
        
        flash('Your password has been reset successfully. You can now log in with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    try:
        # Get all unread notifications for the current user
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).all()
        
        # Mark all as read
        for notification in unread_notifications:
            notification.is_read = True
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'All notifications marked as read'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notifications/<int:notification_id>/mark-read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Notification marked as read'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Notification deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/global-presence')
def global_presence():
    return render_template('global_presence.html')

@app.route('/market-analysis')
@login_required
def market_analysis():
    return render_template('market_analysis.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/api/chat/send', methods=['POST'])
@login_required
def chat_send():
    data = request.get_json()
    user_msg = data.get('message', '').lower()
    username = data.get('username', 'Unknown')
    
    reply = ""
    escalated = False
    account_info = None
    
    # Simple bot logic
    if 'details' in user_msg or 'account' in user_msg:
        # Check if email is provided in the message for verification
        # This is a bit simplified, usually we'd track state 'AWAITING_EMAIL'
        if '@' in user_msg:
            email_provided = next((word for word in user_msg.split() if '@' in word), None)
            if email_provided == current_user.email:
                # Get user data
                deposits = Deposit.query.filter_by(user_id=current_user.id).order_by(Deposit.created_at.desc()).limit(5).all()
                withdrawals = Withdrawal.query.filter_by(user_id=current_user.id).order_by(Withdrawal.created_at.desc()).limit(5).all()
                
                account_info = {
                    'username': current_user.username,
                    'email': current_user.email,
                    'deposit_balance': current_user.deposit_balance,
                    'earning_balance': current_user.earning_balance,
                    'deposits': [{'amount': d.amount, 'status': d.status, 'date': d.created_at.strftime('%Y-%m-%d')} for d in deposits],
                    'withdrawals': [{'amount': w.amount, 'status': w.status, 'date': w.created_at.strftime('%Y-%m-%d')} for w in withdrawals]
                }
                reply = "I have verified your identity. Here are your account details below. Note: This info will disappear in 30 seconds for your security!"
            else:
                reply = "The email you provided does not match the account record. Please provide the correct email to see your details."
        else:
            reply = "I can share your account details, but first, please provide your registered **Email Address** for verification."
    elif 'deposit' in user_msg:
        reply = "To make a deposit, go to the 'Deposit' page, choose your method (Stripe, JazzCash, or EasyPaisa), and follow the instructions. Your funds will show up after admin approval."
    elif 'withdrawal' in user_msg or 'withdraw' in user_msg:
        reply = "You can request a withdrawal from the 'Withdraw' page once you have at least $50 in your earning balance. It usually takes 24-48 hours to process."
    elif 'profit' in user_msg or 'earn' in user_msg:
        reply = "Daily profit is 2% of your active deposits. You can collect it every 24 hours from your Dashboard."
    elif 'password' in user_msg:
        reply = "You can change your password from the Profile section or use the 'Forgot Password' link on the login page."
    else:
        reply = "I'm not quite sure about that specific issue. Let me notify the Admin for you so they can help you directly."
        escalated = True
        
        # Notify admin
        try:
            admin_notif = Notification(
                user_id=1,
                title="Support Escalation",
                message=f"User {username} (Loged in as: {current_user.username}) needs help with: '{user_msg}'"
            )
            db.session.add(admin_notif)
            db.session.commit()
        except:
            pass

    return jsonify({
        'reply': reply,
        'escalated': escalated,
        'account_info': account_info
    })