from datetime import datetime
from .user import db  # ✅ CORRECTED: Import the shared db instance from user.py
from enum import Enum

class NotificationType(Enum):
    # Existing notification types
    GENERAL = "general"
    BOOKING = "booking"
    PROPERTY = "property"
    TENANCY = "tenancy"
    
    # New deposit notification types
    DEPOSIT_PAYMENT_REQUIRED = "deposit_payment_required"
    DEPOSIT_PAYMENT_CONFIRMED = "deposit_payment_confirmed"
    DEPOSIT_HELD_IN_ESCROW = "deposit_held_in_escrow"
    LEASE_EXPIRY_ADVANCE = "lease_expiry_advance"
    DEPOSIT_CLAIM_SUBMITTED = "deposit_claim_submitted"
    DEPOSIT_CLAIM_RESPONSE_REQUIRED = "deposit_claim_response_required"
    DEPOSIT_CLAIM_RESPONSE_DEADLINE = "deposit_claim_response_deadline"
    DEPOSIT_DISPUTE_CREATED = "deposit_dispute_created"
    DEPOSIT_MEDIATION_STARTED = "deposit_mediation_started"
    DEPOSIT_MEDIATION_DEADLINE = "deposit_mediation_deadline"
    DEPOSIT_DISPUTE_RESOLVED = "deposit_dispute_resolved"
    DEPOSIT_REFUNDED = "deposit_refunded"
    DEPOSIT_RELEASED = "deposit_released"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    link = db.Column(db.String(255), nullable=True)  # Optional link for redirection
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Extended fields for deposit system
    notification_type = db.Column(db.Enum(NotificationType), default=NotificationType.GENERAL)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Related entity references for deposit notifications (commented out until tables are created)
    # deposit_transaction_id = db.Column(db.Integer, db.ForeignKey('deposit_transactions.id'), nullable=True)
    # deposit_claim_id = db.Column(db.Integer, db.ForeignKey('deposit_claims.id'), nullable=True)
    # deposit_dispute_id = db.Column(db.Integer, db.ForeignKey('deposit_disputes.id'), nullable=True)
    # tenancy_agreement_id = db.Column(db.Integer, db.ForeignKey('tenancy_agreements.id'), nullable=True)
    # property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=True)
    
    # Action tracking
    action_required = db.Column(db.Boolean, default=False)
    action_deadline = db.Column(db.DateTime, nullable=True)
    action_url = db.Column(db.String(500), nullable=True)
    
    # Delivery tracking
    email_sent = db.Column(db.Boolean, default=False)
    sms_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime, nullable=True)
    sms_sent_at = db.Column(db.DateTime, nullable=True)

    # Relationship to the User model
    recipient = db.relationship('User', backref=db.backref('notifications', lazy=True))
    
    # Relationships to deposit models (commented out until deposit tables are created)
    # deposit_transaction = db.relationship('DepositTransaction', backref='notifications', lazy=True)
    # deposit_claim = db.relationship('DepositClaim', backref='notifications', lazy=True)
    # deposit_dispute = db.relationship('DepositDispute', backref='notifications', lazy=True)
    # tenancy_agreement = db.relationship('TenancyAgreement', backref='notifications', lazy=True)
    # property = db.relationship('Property', backref='notifications', lazy=True)

    def __repr__(self):
        return f'<Notification {self.id} for User {self.recipient_id} - {self.notification_type.value}>'

    def to_dict(self):
        """Converts the notification object to a dictionary."""
        return {
            'id': self.id,
            'recipient_id': self.recipient_id,
            'message': self.message,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat(),
            'notification_type': self.notification_type.value if self.notification_type else 'general',
            'priority': self.priority.value if self.priority else 'normal',
            # Deposit fields commented out until tables are created
            # 'deposit_transaction_id': self.deposit_transaction_id,
            # 'deposit_claim_id': self.deposit_claim_id,
            # 'deposit_dispute_id': self.deposit_dispute_id,
            # 'tenancy_agreement_id': self.tenancy_agreement_id,
            # 'property_id': self.property_id,
            'action_required': self.action_required,
            'action_deadline': self.action_deadline.isoformat() if self.action_deadline else None,
            'action_url': self.action_url,
            'email_sent': self.email_sent,
            'sms_sent': self.sms_sent,
            'email_sent_at': self.email_sent_at.isoformat() if self.email_sent_at else None,
            'sms_sent_at': self.sms_sent_at.isoformat() if self.sms_sent_at else None,
        }
    
    def mark_email_sent(self):
        """Mark notification as sent via email"""
        self.email_sent = True
        self.email_sent_at = datetime.utcnow()
    
    def mark_sms_sent(self):
        """Mark notification as sent via SMS"""
        self.sms_sent = True
        self.sms_sent_at = datetime.utcnow()
    
    @property
    def is_urgent(self):
        """Check if notification is urgent"""
        return self.priority == NotificationPriority.URGENT
    
    @property
    def requires_action(self):
        """Check if notification requires user action"""
        return self.action_required
    
    @property
    def is_deadline_approaching(self):
        """Check if action deadline is approaching (within 24 hours)"""
        if not self.action_deadline:
            return False
        
        time_remaining = self.action_deadline - datetime.utcnow()
        return time_remaining.total_seconds() <= 86400  # 24 hours
    
    @property
    def is_overdue(self):
        """Check if action deadline has passed"""
        if not self.action_deadline:
            return False
        
        return datetime.utcnow() > self.action_deadline
