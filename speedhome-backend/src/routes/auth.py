from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import re
from ..models.user import db, User

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field.capitalize()} is required'
                }), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        role = data['role'].lower()
        
        # Validate role
        if role not in ['landlord', 'tenant']:
            return jsonify({
                'success': False,
                'error': 'Role must be either "landlord" or "tenant"'
            }), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'error': 'Username already exists'
            }), 400
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role=role,
            first_name=data.get('first_name', '').strip(),
            last_name=data.get('last_name', '').strip(),
            phone=data.get('phone', '').strip()
        )
        user.set_password(password)
        
        # Generate verification token
        verification_token = user.generate_verification_token()
        
        # Save user to database
        db.session.add(user)
        db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session.permanent = True
        
        # For landlords, include KYC setup requirements
        response_data = {
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'verification_token': verification_token  # In production, send via email
        }
        
        # Add KYC setup guidance for landlords
        if user.role == 'landlord':
            response_data.update({
                'setup_required': True,
                'setup_message': 'Complete your payment account setup to start receiving deposit payments',
                'next_steps': {
                    'step_1': 'Verify your identity and bank details',
                    'step_2': 'Complete KYC verification (takes 2-3 minutes)',
                    'step_3': 'Start listing properties and receiving payments'
                },
                'kyc_endpoint': '/api/stripe-connect/create-landlord-account',
                'setup_priority': 'high'
            })
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Registration failed: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Account is deactivated'
            }), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Logout failed: {str(e)}'
        }), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get user: {str(e)}'
        }), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Verification token is required'
            }), 400
        
        user = User.query.filter_by(verification_token=token).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid verification token'
            }), 400
        
        if user.verify_email(token):
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Email verified successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Verification token expired or invalid'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Email verification failed: {str(e)}'
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        user = User.query.filter_by(email=email).first()
        if user:
            reset_token = user.generate_reset_token()
            db.session.commit()
            
            # In production, send email with reset link
            return jsonify({
                'success': True,
                'message': 'Password reset instructions sent to your email',
                'reset_token': reset_token  # In production, don't return this
            }), 200
        else:
            # Don't reveal if email exists or not for security
            return jsonify({
                'success': True,
                'message': 'Password reset instructions sent to your email'
            }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Password reset request failed: {str(e)}'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({
                'success': False,
                'error': 'Token and new password are required'
            }), 400
        
        # Validate password strength
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        user = User.query.filter_by(reset_token=token).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid reset token'
            }), 400
        
        if user.reset_password(token, new_password):
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Password reset successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Reset token expired or invalid'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Password reset failed: {str(e)}'
        }), 500

@auth_bp.route('/request-email-verification', methods=['POST'])
def request_email_verification():
    """Request email verification for user"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if user.email_verified:
            return jsonify({
                'success': False,
                'error': 'Email is already verified'
            }), 400
        
        # Generate new verification token
        verification_token = user.generate_verification_token()
        db.session.commit()
        
        # In a real application, you would send an email here
        # For now, we'll just return success
        return jsonify({
            'success': True,
            'message': 'Verification email sent successfully',
            'verification_token': verification_token  # Remove this in production
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change password for authenticated user"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Current password and new password are required'
            }), 400
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if not user.check_password(current_password):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 400
        
        # Validate new password strength
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Password change failed: {str(e)}'
        }), 500

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check if user session is valid and return setup requirements"""
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.is_active:
                response_data = {
                    'success': True,
                    'authenticated': True,
                    'user': user.to_dict()
                }
                
                # For landlords, check if they need KYC setup
                if user.role == 'landlord':
                    kyc_required = not (user.stripe_account_id and user.stripe_charges_enabled)
                    
                    response_data.update({
                        'kyc_status': {
                            'required': kyc_required,
                            'account_exists': bool(user.stripe_account_id),
                            'charges_enabled': bool(user.stripe_charges_enabled),
                            'onboarding_completed': bool(user.stripe_onboarding_completed)
                        }
                    })
                    
                    if kyc_required:
                        response_data.update({
                            'setup_required': True,
                            'setup_message': 'Complete your payment account setup to receive deposit payments',
                            'setup_action': 'Complete KYC verification to activate your landlord account'
                        })
                
                return jsonify(response_data), 200
        
        return jsonify({
            'success': True,
            'authenticated': False
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Session check failed: {str(e)}'
        }), 500

@auth_bp.route('/kyc-status', methods=['GET'])
def get_kyc_status():
    """Get detailed KYC status for landlords"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'landlord':
            return jsonify({
                'success': False,
                'error': 'Only landlords can check KYC status'
            }), 403
        
        # Determine KYC status
        has_account = bool(user.stripe_account_id)
        is_verified = bool(user.stripe_charges_enabled)
        onboarding_completed = bool(user.stripe_onboarding_completed)
        
        if is_verified:
            status = 'completed'
            message = 'Your payment account is fully verified and ready to receive deposits'
            action_required = False
        elif has_account and onboarding_completed:
            status = 'pending_approval'
            message = 'Your documents are being reviewed by our payment processor'
            action_required = False
        elif has_account:
            status = 'incomplete'
            message = 'Complete your onboarding process to start receiving payments'
            action_required = True
        else:
            status = 'not_started'
            message = 'Set up your payment account to receive deposit payments from tenants'
            action_required = True
        
        return jsonify({
            'success': True,
            'kyc_status': {
                'status': status,
                'message': message,
                'action_required': action_required,
                'account_exists': has_account,
                'charges_enabled': is_verified,
                'onboarding_completed': onboarding_completed
            },
            'next_steps': {
                'create_account': not has_account,
                'complete_onboarding': has_account and not onboarding_completed,
                'wait_for_approval': has_account and onboarding_completed and not is_verified
            },
            'endpoints': {
                'create_account': '/api/stripe-connect/create-landlord-account',
                'onboarding_link': '/api/stripe-connect/onboarding-link',
                'check_status': '/api/stripe-connect/account-status'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'KYC status check failed: {str(e)}'
        }), 500

