from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
import pyotp
import qrcode
import io
import base64
import json
import secrets
from app import app, db
from models import User, TwoFactorAuth, Notification

@app.route('/settings/2fa', methods=['GET'])
@login_required
def two_factor_settings():
    """Show the 2FA settings page with QR code if not enabled yet"""
    if current_user.two_factor_enabled:
        # If 2FA is already enabled, just show the settings
        return render_template('two_factor_settings.html', enabled=True)
    
    # Generate a new secret key if one doesn't exist
    if not hasattr(current_user, 'two_factor') or not current_user.two_factor:
        secret = pyotp.random_base32()
        new_2fa = TwoFactorAuth(user_id=current_user.id, secret_key=secret)
        db.session.add(new_2fa)
        db.session.commit()
    else:
        secret = current_user.two_factor.secret_key
    
    # Generate the QR code
    totp = pyotp.TOTP(secret)
    provisioning_url = totp.provisioning_uri(
        name=current_user.email,
        issuer_name="Investment Platform"
    )
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered)
    qr_code = base64.b64encode(buffered.getvalue()).decode()
    
    # Generate backup codes if they don't exist
    if not current_user.two_factor.backup_codes:
        backup_codes = []
        for _ in range(8):
            backup_codes.append(secrets.token_hex(4).upper())
        current_user.two_factor.backup_codes = json.dumps(backup_codes)
        db.session.commit()
    else:
        backup_codes = json.loads(current_user.two_factor.backup_codes)
    
    return render_template(
        'two_factor_settings.html',
        enabled=False,
        qr_code=qr_code,
        secret=secret,
        backup_codes=backup_codes
    )

@app.route('/settings/2fa/enable', methods=['POST'])
@login_required
def enable_2fa():
    """Enable 2FA for the current user"""
    if current_user.two_factor_enabled:
        flash('Two-factor authentication is already enabled.', 'info')
        return redirect(url_for('two_factor_settings'))
    
    # Verify the provided code
    verification_code = request.form.get('code')
    
    if not verification_code:
        flash('Verification code is required.', 'danger')
        return redirect(url_for('two_factor_settings'))
    
    # Get the user's secret
    if not current_user.two_factor:
        flash('Two-factor authentication setup is required first.', 'danger')
        return redirect(url_for('two_factor_settings'))
    
    secret = current_user.two_factor.secret_key
    totp = pyotp.TOTP(secret)
    
    # Verify the code
    if totp.verify(verification_code):
        # Enable 2FA for the user
        current_user.two_factor_enabled = True
        db.session.commit()
        
        # Create notification for the user
        notification = Notification(
            user_id=current_user.id,
            title='Two-Factor Authentication Enabled',
            message='Your account is now protected with two-factor authentication.'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Two-factor authentication has been enabled for your account.', 'success')
        return redirect(url_for('settings'))
    else:
        flash('Invalid verification code. Please try again.', 'danger')
        return redirect(url_for('two_factor_settings'))

@app.route('/settings/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    """Disable 2FA for the current user"""
    if not current_user.two_factor_enabled:
        flash('Two-factor authentication is not enabled.', 'info')
        return redirect(url_for('settings'))
    
    # Verify the provided code
    verification_code = request.form.get('code')
    
    if not verification_code:
        flash('Verification code is required.', 'danger')
        return redirect(url_for('two_factor_settings'))
    
    # Get the user's secret
    if not current_user.two_factor:
        flash('Two-factor authentication is not set up for this account.', 'danger')
        return redirect(url_for('settings'))
    
    secret = current_user.two_factor.secret_key
    totp = pyotp.TOTP(secret)
    
    # Check if it's a backup code
    is_backup_code = False
    if current_user.two_factor.backup_codes:
        backup_codes = json.loads(current_user.two_factor.backup_codes)
        if verification_code in backup_codes:
            is_backup_code = True
            # Remove the used backup code
            backup_codes.remove(verification_code)
            current_user.two_factor.backup_codes = json.dumps(backup_codes)
    
    # Verify the code
    if totp.verify(verification_code) or is_backup_code:
        # Disable 2FA for the user
        current_user.two_factor_enabled = False
        
        # Optional: remove the 2FA record entirely
        if current_user.two_factor:
            db.session.delete(current_user.two_factor)
        
        db.session.commit()
        
        # Create notification for the user
        notification = Notification(
            user_id=current_user.id,
            title='Two-Factor Authentication Disabled',
            message='Two-factor authentication has been disabled for your account.'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Two-factor authentication has been disabled for your account.', 'success')
        return redirect(url_for('settings'))
    else:
        flash('Invalid verification code. Please try again.', 'danger')
        return redirect(url_for('two_factor_settings'))

@app.route('/2fa/verify', methods=['GET', 'POST'])
def verify_2fa():
    """Verify 2FA code during login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Check if user_id is in session (set during login)
    user_id = session.get('two_factor_user_id')
    if not user_id:
        flash('Authentication error. Please log in again.', 'danger')
        return redirect(url_for('login'))
    
    # Get the user
    user = User.query.get(user_id)
    if not user or not user.two_factor_enabled or not user.two_factor:
        session.pop('two_factor_user_id', None)
        flash('Authentication error. Please log in again.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        verification_code = request.form.get('code')
        
        if not verification_code:
            flash('Verification code is required.', 'danger')
            return redirect(url_for('verify_2fa'))
        
        # Check if it's a backup code
        is_backup_code = False
        if user.two_factor.backup_codes:
            backup_codes = json.loads(user.two_factor.backup_codes)
            if verification_code in backup_codes:
                is_backup_code = True
                # Remove the used backup code
                backup_codes.remove(verification_code)
                user.two_factor.backup_codes = json.dumps(backup_codes)
                db.session.commit()
        
        # Verify the code
        secret = user.two_factor.secret_key
        totp = pyotp.TOTP(secret)
        
        if totp.verify(verification_code) or is_backup_code:
            # Complete the login process
            from flask_login import login_user
            login_user(user)
            
            # Clear the session
            session.pop('two_factor_user_id', None)
            
            next_page = session.pop('next_url', None)
            flash('Logged in successfully!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')
            return redirect(url_for('verify_2fa'))
        
    return render_template('verify_2fa.html') 