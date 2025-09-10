from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.Text, nullable=True)  # Base64 or URL
    bio = db.Column(db.Text, nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    company_name = db.Column(db.String(100), nullable=True)
    
    # Role and status
    role = db.Column(db.String(20), nullable=False, default='tenant')  # 'landlord', 'tenant', or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Email verification
    verification_token = db.Column(db.String(100), nullable=True)
    verification_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Password reset
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Stripe Connect integration (for landlords)
    stripe_account_id = db.Column(db.String(100), nullable=True)  # Stripe Connect account ID
    stripe_account_status = db.Column(db.String(50), nullable=True)  # pending, active, restricted
    stripe_onboarding_completed = db.Column(db.Boolean, default=False)
    stripe_charges_enabled = db.Column(db.Boolean, default=False)
    stripe_payouts_enabled = db.Column(db.Boolean, default=False)
    
    # Preferences (JSON field)
    preferences = db.Column(db.Text, nullable=True)  # JSON string

    booked_slots = db.relationship('ViewingSlot', back_populates='booked_by',
                                   foreign_keys='ViewingSlot.booked_by_user_id')
    landlord_slots = db.relationship('ViewingSlot', back_populates='landlord',
                                    foreign_keys='ViewingSlot.landlord_id')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self):
        """Generate email verification token"""
        self.verification_token = secrets.token_urlsafe(32)
        self.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        return self.verification_token

    def generate_reset_token(self):
        """Generate password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    def verify_email(self, token):
        """Verify email with token"""
        if (self.verification_token == token and 
            self.verification_token_expires and 
            datetime.utcnow() < self.verification_token_expires):
            self.is_verified = True
            self.verification_token = None
            self.verification_token_expires = None
            return True
        return False

    def reset_password(self, token, new_password):
        """Reset password with token"""
        if (self.reset_token == token and 
            self.reset_token_expires and 
            datetime.utcnow() < self.reset_token_expires):
            self.set_password(new_password)
            self.reset_token = None
            self.reset_token_expires = None
            return True
        return False

    def get_preferences(self):
        """Get user preferences as dict"""
        if self.preferences:
            try:
                return json.loads(self.preferences)
            except:
                return {}
        return {}

    def set_preferences(self, prefs_dict):
        """Set user preferences from dict"""
        self.preferences = json.dumps(prefs_dict)

    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'occupation': self.occupation, 
            'company_name': self.company_name, 
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'full_name': self.get_full_name(),
            'preferences': self.get_preferences()
        }
        
        if include_sensitive:
            data.update({
                'verification_token': self.verification_token,
                'reset_token': self.reset_token
            })
        
        return data

    def to_public_dict(self):
        """Convert user to public dictionary (safe for other users)"""
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'occupation': self.occupation,
            'role': self.role,
            'full_name': self.get_full_name(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
