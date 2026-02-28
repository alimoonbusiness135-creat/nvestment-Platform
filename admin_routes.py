from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
import datetime
from functools import wraps
from app import app
from extensions import db
from models import User, Deposit, Earning, Withdrawal, Notification, Referral, DeletedAccount

# Admin decorator to restrict access to admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:  # Assuming admin has ID 1
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Get statistics for admin dashboard
    total_users = User.query.count()
    total_deposits = Deposit.query.filter_by(status='approved').count()
    total_deposit_amount = db.session.query(db.func.sum(Deposit.amount)).filter_by(status='approved').scalar() or 0
    total_withdrawals = Withdrawal.query.filter_by(status='approved').count()
    total_withdrawal_amount = db.session.query(db.func.sum(Withdrawal.amount)).filter_by(status='approved').scalar() or 0
    
    # Get pending requests
    pending_deposits = Deposit.query.filter_by(status='pending').count()
    pending_withdrawals = Withdrawal.query.filter_by(status='pending').count()
    
    # Get recent registrations
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_deposits=total_deposits,
        total_deposit_amount=total_deposit_amount,
        total_withdrawals=total_withdrawals,
        total_withdrawal_amount=total_withdrawal_amount,
        pending_deposits=pending_deposits,
        pending_withdrawals=pending_withdrawals,
        recent_users=recent_users
    )

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def admin_user_detail(user_id):
    user = User.query.get_or_404(user_id)
    deposits = Deposit.query.filter_by(user_id=user_id).order_by(Deposit.created_at.desc()).all()
    withdrawals = Withdrawal.query.filter_by(user_id=user_id).order_by(Withdrawal.created_at.desc()).all()
    earnings = Earning.query.filter_by(user_id=user_id).order_by(Earning.created_at.desc()).all()
    
    return render_template(
        'admin/user_detail.html',
        user=user,
        deposits=deposits,
        withdrawals=withdrawals,
        earnings=earnings
    )

@app.route('/admin/deposits')
@login_required
@admin_required
def admin_deposits():
    status = request.args.get('status', 'all')
    
    if status == 'all':
        deposits = Deposit.query.order_by(Deposit.created_at.desc()).all()
    else:
        deposits = Deposit.query.filter_by(status=status).order_by(Deposit.created_at.desc()).all()
    
    return render_template('admin/deposits.html', deposits=deposits, status=status)

@app.route('/admin/approve_deposit/<int:deposit_id>', methods=['POST'])
@login_required
@admin_required
def admin_approve_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    
    if deposit.status != 'pending':
        flash('This deposit has already been processed', 'warning')
        return redirect(url_for('admin_deposits'))
    
    # Approve the deposit
    deposit.status = 'approved'
    deposit.updated_at = datetime.datetime.now()
    
    # Update user's deposit balance
    user = User.query.get(deposit.user_id)
    user.deposit_balance += deposit.amount
    
    # Calculate referral commissions
    from routes import calculate_referral_commission
    calculate_referral_commission(deposit.user_id, deposit.amount)
    
    # Create notification for the user
    notification = Notification(
        user_id=deposit.user_id,
        title='Deposit Approved',
        message=f'Your deposit of ${deposit.amount} has been approved.'
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash(f'Deposit of ${deposit.amount} for {user.username} has been approved', 'success')
    return redirect(url_for('admin_deposits'))

@app.route('/admin/reject_deposit/<int:deposit_id>', methods=['POST'])
@login_required
@admin_required
def admin_reject_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    
    if deposit.status != 'pending':
        flash('This deposit has already been processed', 'warning')
        return redirect(url_for('admin_deposits'))
    
    # Reject the deposit
    deposit.status = 'rejected'
    deposit.updated_at = datetime.datetime.now()
    
    # Create notification for the user
    notification = Notification(
        user_id=deposit.user_id,
        title='Deposit Rejected',
        message=f'Your deposit of ${deposit.amount} has been rejected. Please contact support for assistance.'
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash(f'Deposit of ${deposit.amount} has been rejected', 'success')
    return redirect(url_for('admin_deposits'))

@app.route('/admin/withdrawals')
@login_required
@admin_required
def admin_withdrawals():
    status = request.args.get('status', 'all')
    
    if status == 'all':
        withdrawals = Withdrawal.query.order_by(Withdrawal.created_at.desc()).all()
    else:
        withdrawals = Withdrawal.query.filter_by(status=status).order_by(Withdrawal.created_at.desc()).all()
    
    return render_template('admin/withdrawals.html', withdrawals=withdrawals, status=status)

@app.route('/admin/approve_withdrawal/<int:withdrawal_id>', methods=['POST'])
@login_required
@admin_required
def admin_approve_withdrawal(withdrawal_id):
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    
    if withdrawal.status != 'pending':
        flash('This withdrawal has already been processed', 'warning')
        return redirect(url_for('admin_withdrawals'))
    
    # Approve the withdrawal
    withdrawal.status = 'approved'
    withdrawal.updated_at = datetime.datetime.now()
    
    # Update user's total withdrawn amount
    user = User.query.get(withdrawal.user_id)
    user.total_withdrawn += withdrawal.amount
    
    # Create notification for the user
    notification = Notification(
        user_id=withdrawal.user_id,
        title='Withdrawal Approved',
        message=f'Your withdrawal of ${withdrawal.amount} has been approved and sent to your account.'
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash(f'Withdrawal of ${withdrawal.amount} for {user.username} has been approved', 'success')
    return redirect(url_for('admin_withdrawals'))

@app.route('/admin/reject_withdrawal/<int:withdrawal_id>', methods=['POST'])
@login_required
@admin_required
def admin_reject_withdrawal(withdrawal_id):
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    
    if withdrawal.status != 'pending':
        flash('This withdrawal has already been processed', 'warning')
        return redirect(url_for('admin_withdrawals'))
    
    # Reject the withdrawal
    withdrawal.status = 'rejected'
    withdrawal.updated_at = datetime.datetime.now()
    
    # Refund the amount to the user's earning balance
    user = User.query.get(withdrawal.user_id)
    user.earning_balance += withdrawal.amount
    
    # Create notification for the user
    notification = Notification(
        user_id=withdrawal.user_id,
        title='Withdrawal Rejected',
        message=f'Your withdrawal of ${withdrawal.amount} has been rejected. The amount has been credited back to your account. Please contact support for assistance.'
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash(f'Withdrawal of ${withdrawal.amount} has been rejected and refunded', 'success')
    return redirect(url_for('admin_withdrawals'))

@app.route('/admin/notifications', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_notifications():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        is_global = request.form.get('is_global') == 'on'
        user_id = request.form.get('user_id')
        
        if not title or not message:
            flash('Title and message are required', 'danger')
            return redirect(url_for('admin_notifications'))
        
        if is_global:
            # Create global notification
            notification = Notification(
                user_id=current_user.id,  # Admin user ID
                title=title,
                message=message,
                is_global=True
            )
            
            db.session.add(notification)
            flash('Global notification sent to all users', 'success')
        elif user_id:
            # Create notification for specific user
            user = User.query.get(user_id)
            if not user:
                flash('User not found', 'danger')
                return redirect(url_for('admin_notifications'))
            
            notification = Notification(
                user_id=user.id,
                title=title,
                message=message
            )
            
            db.session.add(notification)
            flash(f'Notification sent to {user.username}', 'success')
        
        db.session.commit()
        return redirect(url_for('admin_notifications'))
    
    # Get all notifications
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    users = User.query.order_by(User.username).all()
    
    return render_template('admin/notifications.html', notifications=notifications, users=users)

@app.route('/admin/add_bonus', methods=['POST'])
@login_required
@admin_required
def admin_add_bonus():
    user_id = request.form.get('user_id')
    amount = float(request.form.get('amount', 0))
    description = request.form.get('description', 'Admin bonus')
    
    if not user_id or amount <= 0:
        flash('User ID and a positive amount are required', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin_users'))
    
    # Add bonus to user's earning balance
    user.earning_balance += amount
    
    # Create earning record
    earning = Earning(
        user_id=user.id,
        amount=amount,
        description=description
    )
    
    # Create notification for the user
    notification = Notification(
        user_id=user.id,
        title='Bonus Added',
        message=f'A bonus of ${amount} has been added to your account: {description}'
    )
    
    db.session.add(earning)
    db.session.add(notification)
    db.session.commit()
    
    flash(f'Bonus of ${amount} added to {user.username}', 'success')
    return redirect(url_for('admin_user_detail', user_id=user_id))

@app.route('/admin/add_penalty', methods=['POST'])
@login_required
@admin_required
def admin_add_penalty():
    user_id = request.form.get('user_id')
    amount = float(request.form.get('amount', 0))
    description = request.form.get('description', 'Admin penalty')
    
    if not user_id or amount <= 0:
        flash('User ID and a positive amount are required', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin_users'))
    
    # Subtract penalty from user's earning balance
    if user.earning_balance >= amount:
        user.earning_balance -= amount
    else:
        # If not enough balance, set to zero
        amount = user.earning_balance
        user.earning_balance = 0
    
    # Create earning record (negative amount)
    earning = Earning(
        user_id=user.id,
        amount=-amount,
        description=description
    )
    
    # Create notification for the user
    notification = Notification(
        user_id=user.id,
        title='Penalty Applied',
        message=f'A penalty of ${amount} has been deducted from your account: {description}'
    )
    
    db.session.add(earning)
    db.session.add(notification)
    db.session.commit()
    
    flash(f'Penalty of ${amount} applied to {user.username}', 'success')
    return redirect(url_for('admin_user_detail', user_id=user_id))

@app.route('/admin/deleted-accounts')
@login_required
@admin_required
def admin_deleted_accounts():
    # Get deleted accounts, most recent first
    deleted_accounts = DeletedAccount.query.order_by(DeletedAccount.deleted_at.desc()).all()
    
    return render_template('admin/deleted_accounts.html', deleted_accounts=deleted_accounts) 