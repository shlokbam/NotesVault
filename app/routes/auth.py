from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.note import Note
from app.models.note_view import NoteView
from werkzeug.security import generate_password_hash
import re
from app.models.credit_transaction import CreditTransaction
from datetime import datetime
from flask import current_app

bp = Blueprint('auth', __name__)

def is_valid_college_email(email):
    return email.endswith('vit.edu')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        college = request.form.get('college')
        department = request.form.get('department')

        # Strictly enforce VIT email
        if not email.endswith('vit.edu'):
            flash('Only VIT email addresses are allowed for registration.', 'error')
            return render_template('auth/register.html')

        # Check if email is already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')

        # Create user with unverified status
        user = User(
            email=email,
            name=name,
            college=college,
            department=department,
            credits=0,  # Start with 0 credits
            is_verified=False  # Explicitly set as unverified
        )
        user.set_password(password)
        user.generate_verification_code()  # Generate verification code
        db.session.add(user)
        db.session.commit()

        # Add initial credits and record the transaction
        user.add_credits(
            amount=10,
            transaction_type='initial',
            description='Initial credits for new user registration'
        )

        # Send verification email
        from app.utils.email import send_verification_email
        send_verification_email(user)

        flash('Registration successful! Please check your VIT email for the verification code.', 'success')
        return redirect(f'/verify-email?email={email}')

    return render_template('auth/register.html')

@bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    email = request.args.get('email')  # Get email from URL parameters
    if not email:
        flash('Email address is required for verification.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        code = request.form.get('verification_code')
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email not found.', 'error')
            return render_template('auth/verify_email.html', email=email)
        
        if user.is_verified:
            flash('Email already verified. Please login.', 'info')
            return redirect(url_for('auth.login'))
        
        if user.verify_email(code):
            flash('Email verified successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired verification code.', 'error')
            return render_template('auth/verify_email.html', email=email)
    
    return render_template('auth/verify_email.html', email=email)

@bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not found.', 'error')
            return render_template('auth/resend_verification.html')
        
        if user.is_verified:
            flash('Email already verified. Please login.', 'info')
            return redirect(url_for('auth.login'))
        
        user.generate_verification_code()
        from app.utils.email import send_verification_email
        send_verification_email(user)
        
        flash('New verification code sent. Please check your email.', 'success')
        return redirect(url_for('auth.verify_email'))
    
    return render_template('auth/resend_verification.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html')
        
        # If everything is okay, log in the user
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', Note=Note, NoteView=NoteView)

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        college = request.form.get('college')
        department = request.form.get('department')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Update basic info
        current_user.name = name
        current_user.college = college
        current_user.department = department

        # Update password if provided
        if current_password and new_password and confirm_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('auth/edit_profile.html')
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return render_template('auth/edit_profile.html')
            
            current_user.set_password(new_password)
            flash('Password updated successfully.', 'success')

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/edit_profile.html')

@bp.route('/credit-history')
@login_required
def credit_history():
    transactions = CreditTransaction.query.filter_by(user_id=current_user.id).order_by(CreditTransaction.created_at.desc()).all()
    return render_template('auth/credit_history.html', transactions=transactions)

@bp.route('/gift-credits', methods=['GET', 'POST'])
@login_required
def gift_credits():
    if request.method == 'POST':
        recipient_email = request.form.get('recipient_email')
        credit_amount = int(request.form.get('credit_amount'))
        
        # Validate recipient email
        if not recipient_email.endswith('vit.edu'):
            flash('Only VIT email addresses are allowed.', 'error')
            return redirect(url_for('auth.gift_credits'))
        
        # Check if recipient exists
        recipient = User.query.filter_by(email=recipient_email).first()
        if not recipient:
            flash('Recipient not found. Please make sure they have registered with NotesVault.', 'error')
            return redirect(url_for('auth.gift_credits'))
        
        # Check if sender has enough credits
        if current_user.credits < credit_amount:
            flash('You do not have enough credits to make this gift.', 'error')
            return redirect(url_for('auth.gift_credits'))
        
        # Record transactions for both users
        current_user.use_credits(
            credit_amount,
            'gift_sent',
            f'Gifted credits to {recipient.name}'
        )
        
        recipient.add_credits(
            credit_amount,
            'gift_received',
            f'Received credits from {current_user.name}',
            related_user=current_user
        )
        
        # Send email notification to recipient
        from app.utils.email import send_credit_gift_email
        send_credit_gift_email(recipient, current_user, credit_amount)
        
        flash(f'Successfully gifted {credit_amount} credits to {recipient_email}!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/gift_credits.html')

@bp.route('/buy-credits', methods=['GET', 'POST'])
@login_required
def buy_credits():
    return redirect(url_for('payment.buy_credits'))
