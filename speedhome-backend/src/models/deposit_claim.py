from datetime import datetime, timedelta
from .user import db
from enum import Enum

class DepositClaimStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    TENANT_NOTIFIED = "tenant_notified"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    DISPUTED = "disputed"
    RESOLVED = "resolved"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class DepositClaimType(Enum):
    DAMAGE = "damage"
    CLEANING = "cleaning"
    UNPAID_RENT = "unpaid_rent"
    UNPAID_UTILITIES = "unpaid_utilities"
    EARLY_TERMINATION = "early_termination"
    OTHER = "other"

class DepositClaim(db.Model):
    __tablename__ = 'deposit_claims'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core references - integrate with existing models
    deposit_transaction_id = db.Column(db.Integer, db.ForeignKey('deposit_transactions.id'), nullable=False)
    tenancy_agreement_id = db.Column(db.Integer, db.ForeignKey('tenancy_agreements.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Integrate with existing messaging system
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)
    
    # Claim details
    claim_type = db.Column(db.Enum(DepositClaimType), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    claimed_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Status and workflow
    status = db.Column(db.Enum(DepositClaimStatus), default=DepositClaimStatus.DRAFT)
    
    # Evidence and documentation
    evidence_photos = db.Column(db.JSON, default=list)  # List of S3 URLs
    evidence_documents = db.Column(db.JSON, default=list)  # Receipts, invoices, etc.
    evidence_description = db.Column(db.Text, nullable=True)
    
    # Timeline and deadlines
    submitted_at = db.Column(db.DateTime, nullable=True)
    tenant_response_deadline = db.Column(db.DateTime, nullable=True)  # 7 days from submission
    auto_approve_at = db.Column(db.DateTime, nullable=True)  # Auto-approve if no response
    
    # Resolution tracking
    resolved_at = db.Column(db.DateTime, nullable=True)
    approved_amount = db.Column(db.Numeric(10, 2), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin or system
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with existing models
    deposit_transaction = db.relationship('DepositTransaction', backref='claims')
    tenancy_agreement = db.relationship('TenancyAgreement', backref='deposit_claims')
    property = db.relationship('Property', backref='deposit_claims')
    landlord = db.relationship('User', foreign_keys=[landlord_id], backref='submitted_claims')
    tenant = db.relationship('User', foreign_keys=[tenant_id], backref='received_claims')
    conversation = db.relationship('Conversation', backref='deposit_claims')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_claims')
    
    def __repr__(self):
        return f'<DepositClaim {self.id} - {self.claim_type.value} - MYR {self.claimed_amount}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'deposit_transaction_id': self.deposit_transaction_id,
            'tenancy_agreement_id': self.tenancy_agreement_id,
            'property_id': self.property_id,
            'landlord_id': self.landlord_id,
            'tenant_id': self.tenant_id,
            'conversation_id': self.conversation_id,
            'claim_type': self.claim_type.value if self.claim_type else None,
            'title': self.title,
            'description': self.description,
            'claimed_amount': float(self.claimed_amount) if self.claimed_amount else 0,
            'status': self.status.value if self.status else 'draft',
            'evidence_photos': self.evidence_photos or [],
            'evidence_documents': self.evidence_documents or [],
            'evidence_description': self.evidence_description,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'tenant_response_deadline': self.tenant_response_deadline.isoformat() if self.tenant_response_deadline else None,
            'auto_approve_at': self.auto_approve_at.isoformat() if self.auto_approve_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'approved_amount': float(self.approved_amount) if self.approved_amount else None,
            'resolution_notes': self.resolution_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            
            # Related data
            'landlord_name': f"{self.landlord.first_name} {self.landlord.last_name}" if self.landlord else None,
            'tenant_name': f"{self.tenant.first_name} {self.tenant.last_name}" if self.tenant else None,
            'property_address': self.property.address if self.property else None,
            'days_until_deadline': self.days_until_response_deadline,
            'is_overdue': self.is_response_overdue,
            'can_auto_approve': self.can_auto_approve,
        }
    
    def submit_claim(self):
        """Submit the claim and set deadlines"""
        if self.status != DepositClaimStatus.DRAFT:
            raise ValueError("Only draft claims can be submitted")
        
        self.status = DepositClaimStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        
        # Set 7-day response deadline
        self.tenant_response_deadline = datetime.utcnow() + timedelta(days=7)
        self.auto_approve_at = datetime.utcnow() + timedelta(days=7, hours=1)  # 1 hour grace period
        
        self.updated_at = datetime.utcnow()
        
        # Create conversation for this claim if not exists
        if not self.conversation_id:
            self._create_claim_conversation()
    
    def _create_claim_conversation(self):
        """Create a conversation for this deposit claim"""
        from .conversation import Conversation
        
        # Check if there's already a conversation for this tenancy agreement
        existing_conversation = Conversation.query.filter_by(
            tenant_id=self.tenant_id,
            landlord_id=self.landlord_id,
            property_id=self.property_id
        ).first()
        
        if existing_conversation:
            self.conversation_id = existing_conversation.id
        else:
            # Create new conversation for deposit claim
            conversation = Conversation(
                tenant_id=self.tenant_id,
                landlord_id=self.landlord_id,
                property_id=self.property_id,
                booking_id=None,  # No booking for deposit claims
                status='active'
            )
            db.session.add(conversation)
            db.session.flush()  # Get the ID
            self.conversation_id = conversation.id
    
    @property
    def days_until_response_deadline(self):
        """Calculate days until tenant response deadline"""
        if not self.tenant_response_deadline:
            return None
        
        delta = self.tenant_response_deadline - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def is_response_overdue(self):
        """Check if tenant response is overdue"""
        if not self.tenant_response_deadline:
            return False
        
        return datetime.utcnow() > self.tenant_response_deadline
    
    @property
    def can_auto_approve(self):
        """Check if claim can be auto-approved"""
        return (self.status in [DepositClaimStatus.SUBMITTED, DepositClaimStatus.TENANT_NOTIFIED] and
                self.auto_approve_at and
                datetime.utcnow() > self.auto_approve_at)

