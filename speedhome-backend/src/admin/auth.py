from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from src.models.user import User

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin/auth')

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect('/admin/')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('admin/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password) and user.role == 'admin':
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page or '/admin/')
        else:
            flash('Invalid credentials or insufficient privileges.', 'error')
    
    return render_template('admin/login.html')

@admin_auth_bp.route('/logout')
def logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin_auth.login'))

@admin_auth_bp.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    """Create the first admin user (only if no admin exists)"""
    existing_admin = User.query.filter_by(role='admin').first()
    if existing_admin:
        flash('Admin user already exists. Please contact the existing admin.', 'error')
        return redirect(url_for('admin_auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if not all([username, email, password, first_name, last_name]):
            flash('All fields are required.', 'error')
            return render_template('admin/create_admin.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('admin/create_admin.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('admin/create_admin.html')
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='admin'
        )
        admin_user.set_password(password)
        
        from src.models.user import db
        db.session.add(admin_user)
        db.session.commit()
        
        flash('Admin user created successfully! You can now log in.', 'success')
        return redirect(url_for('admin_auth.login'))
    
    return render_template('admin/create_admin.html')

