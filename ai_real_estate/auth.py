"""
Authentication Blueprint
Handles user registration, login, logout, and profile management
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
import re

auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    return True, "Password is strong."


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('login.html')

            login_user(user, remember=bool(remember))
            flash(f'Welcome back, {user.full_name}!', 'success')

            # Redirect to the page user was trying to access
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []

        if not full_name or len(full_name) < 2:
            errors.append('Please enter your full name (at least 2 characters).')

        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')

        if not validate_email(email):
            errors.append('Please enter a valid email address.')

        is_valid_pwd, pwd_msg = validate_password(password)
        if not is_valid_pwd:
            errors.append(pwd_msg)

        if password != confirm_password:
            errors.append('Passwords do not match.')

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            errors.append('This username is already taken.')

        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')

        # Create new user
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone if phone else None,
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    from models import Favorite, SearchHistory
    favorites_count = Favorite.query.filter_by(user_id=current_user.id).count()
    searches_count = SearchHistory.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html',
                           favorites_count=favorites_count,
                           searches_count=searches_count)


@auth_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()

    if full_name and len(full_name) >= 2:
        current_user.full_name = full_name

    current_user.phone = phone if phone else None

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('auth.profile'))

    is_valid, msg = validate_password(new_password)
    if not is_valid:
        flash(msg, 'error')
        return redirect(url_for('auth.profile'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('auth.profile'))

    current_user.set_password(new_password)
    db.session.commit()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.profile'))
