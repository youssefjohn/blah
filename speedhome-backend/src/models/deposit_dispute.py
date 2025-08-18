from datetime import datetime, timedelta
from .user import db
from enum import Enum

class DepositDisputeStatus(Enum):
    PENDING = "pending"
    TENANT_RESPONDED = "tenant_responded"
    UNDER_MEDIATION = "under_mediation"
    AWAITING_EVIDENCE = "awaiting_evidence"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"

class DepositDisputeResponse(Enum):
    ACCEPT = "accept"
    PARTIAL_ACCEPT = "partial_accept"
    REJECT = "reject"

class DepositDispute(db.Model):
    __tablename__ = 'deposit_disputes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core references - integrate with existing models
    deposit_claim_id = db.Column(db.Integer, db.ForeignKey('deposit_claims.id'), nullable=False)
    deposit_transaction_id = db.Column(db.Integer, db.ForeignKey('deposit_transactions.id'), nullable=False)
    tenancy_agreement_id = db.Column(db.Integer, db.ForeignKey('tenancy_agreements.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Integrate with existing messaging system
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    
    # Dispute details
    tenant_response = db.Column(db.Enum(DepositDisputeResponse), nullable=False)
    tenant_response_reason = db.Column(db.Text, nullable=False)
    tenant_counter_amount = db.Column(db.Numeric(10, 2), nullable=True)  # For partial acceptance
    
    # Status and workflow
    status = db.Column(db.Enum(DepositDisputeStatus), default=DepositDisputeStatus.PENDING)
    
    # Counter-evidence from tenant
    counter_evidence_photos = db.Column(db.JSON, default=list)  # Tenant's evidence
    counter_evidence_documents = db.Column(db.JSON, default=list)
    counter_evidence_description = db.Column(db.Text, nullable=True)
    
    # Mediation and resolution
    mediation_started_at = db.Column(db.DateTime, nullable=True)
    mediation_deadline = db.Column(db.DateTime, nullable=True)  # 14 days for mediation
    escalation_deadline = db.Column(db.DateTime, nullable=True)  # Auto-escalate if unresolved
    
    # Messages and communication - integrate with existing messaging
    messages = db.Column(db.JSON, default=list)  # Dispute-specific messages
    last_message_at = db.Column(db.DateTime, nullable=True)
    last_message_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Resolution tracking
    resolved_at = db.Column(db.DateTime, nullable=True)
    final_amount = db.Column(db.Numeric(10, 2), nullable=True)
    resolution_method = db.Column(db.String(50), nullable=True)  # 'mediation', 'admin', 'auto'
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with existing models
    deposit_claim = db.relationship('DepositClaim', backref='dispute')
    deposit_transaction = db.relationship('DepositTransaction', backref='disputes')
    tenancy_agreement = db.relationship('TenancyAgreement', backref='deposit_disputes')
    property = db.relationship('Property', backref='deposit_disputes')
    tenant = db.relationship('User', foreign_keys=[tenant_id], backref='tenant_disputes')
    landlord = db.relationship('User', foreign_keys=[landlord_id], backref='landlord_disputes')
    conversation = db.relationship('Conversation', backref='deposit_disputes')
    last_message_user = db.relationship('User', foreign_keys=[last_message_by], backref='last_dispute_messages')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_disputes')
    
    def __repr__(self):
        return f'<DepositDispute {self.id} - Claim {self.deposit_claim_id} - {self.tenant_response.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'deposit_claim_id': self.deposit_claim_id,
            'deposit_transaction_id': self.deposit_transaction_id,
            'tenancy_agreement_id': self.tenancy_agreement_id,
            'property_id': self.property_id,
            'tenant_id': self.tenant_id,
            'landlord_id': self.landlord_id,
            'conversation_id': self.conversation_id,
            'tenant_response': self.tenant_response.value if self.tenant_response else None,
            'tenant_response_reason': self.tenant_response_reason,
            'tenant_counter_amount': float(self.tenant_counter_amount) if self.tenant_counter_amount else None,
            'status': self.status.value if self.status else 'pending',
            'counter_evidence_photos': self.counter_evidence_photos or [],
            'counter_evidence_documents': self.counter_evidence_documents or [],
            'counter_evidence_description': self.counter_evidence_description,
            'mediation_started_at': self.mediation_started_at.isoformat() if self.mediation_started_at else None,
            'mediation_deadline': self.mediation_deadline.isoformat() if self.mediation_deadline else None,
            'escalation_deadline': self.escalation_deadline.isoformat() if self.escalation_deadline else None,
            'messages': self.messages or [],
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'final_amount': float(self.final_amount) if self.final_amount else None,
            'resolution_method': self.resolution_method,
            'resolution_notes': self.resolution_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            
            # Related data
            'tenant_name': f"{self.tenant.first_name} {self.tenant.last_name}" if self.tenant else None,
            'landlord_name': f"{self.landlord.first_name} {self.landlord.last_name}" if self.landlord else None,
            'property_address': self.property.address if self.property else None,
            'days_until_mediation_deadline': self.days_until_mediation_deadline,
            'is_mediation_overdue': self.is_mediation_overdue,
            'can_escalate': self.can_escalate,
            'message_count': len(self.messages) if self.messages else 0,
        }
    
    def add_message(self, sender_id, message_content, message_type='text'):
        """Add message to dispute conversation"""
        if not self.messages:
            self.messages = []
        
        message = {
            'id': len(self.messages) + 1,
            'sender_id': sender_id,
            'content': message_content,
            'type': message_type,
            'timestamp': datetime.utcnow().isoformat(),
            'is_system': sender_id is None
        }
        
        self.messages.append(message)
        self.last_message_at = datetime.utcnow()
        self.last_message_by = sender_id
        self.updated_at = datetime.utcnow()
    
    @property
    def days_until_mediation_deadline(self):
        """Calculate days until mediation deadline"""
        if not self.mediation_deadline:
            return None
        
        delta = self.mediation_deadline - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def is_mediation_overdue(self):
        """Check if mediation deadline is overdue"""
        if not self.mediation_deadline:
            return False
        
        return datetime.utcnow() > self.mediation_deadline
    
    @property
    def can_escalate(self):
        """Check if dispute can be escalated"""
        return (self.status == DepositDisputeStatus.UNDER_MEDIATION and
                self.escalation_deadline and
                datetime.utcnow() > self.escalation_deadline)

