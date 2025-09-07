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

    # --- FIX: Add the missing category column ---
    category = db.Column(db.String(100), nullable=True)

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

    # Tenant response tracking
    tenant_response = db.Column(db.String(50), nullable=True)  # 'accept', 'partial_accept', 'reject'
    tenant_explanation = db.Column(db.Text, nullable=True)  # Tenant's explanation for their response
    tenant_counter_amount = db.Column(db.Numeric(10, 2), nullable=True)  # Amount tenant agrees to pay (for partial_accept)
    tenant_responded_at = db.Column(db.DateTime, nullable=True)  # When tenant submitted their response

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships with existing models (using string references and lazy loading)
    deposit_transaction = db.relationship('DepositTransaction', backref='claims', lazy=True)
    tenancy_agreement = db.relationship('TenancyAgreement', backref='deposit_claims', lazy=True)
    property = db.relationship('Property', backref='deposit_claims', lazy=True)
    landlord = db.relationship('User', foreign_keys=[landlord_id], backref='submitted_claims', lazy=True)
    tenant = db.relationship('User', foreign_keys=[tenant_id], backref='received_claims', lazy=True)
    conversation = db.relationship('Conversation', backref='deposit_claims', lazy=True)
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_claims', lazy=True)

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
            'category': self.category,  # <-- Also add it to the dictionary output
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
            'tenant_response': self.tenant_response,
            'tenant_explanation': self.tenant_explanation,
            'tenant_counter_amount': float(self.tenant_counter_amount) if self.tenant_counter_amount else None,
            'tenant_responded_at': self.tenant_responded_at.isoformat() if self.tenant_responded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,

            # Related data
            'landlord_name': f"{self.landlord.first_name} {self.landlord.last_name}" if self.landlord else None,
            'tenant_name': f"{self.tenant.first_name} {self.tenant.last_name}" if self.tenant else None,
            'property_address': f"{self.property.title}, {self.property.location}" if self.property else None,
            # Using regular methods instead of properties to avoid SQLAlchemy conflicts
            'days_until_deadline': self.get_days_until_response_deadline(),
            'is_overdue': self.is_response_overdue(),
            'can_auto_approve': self.can_auto_approve(),
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

    # Restored as regular methods to avoid SQLAlchemy conflicts
    def get_days_until_response_deadline(self):
        """Calculate days until tenant response deadline"""
        if not self.tenant_response_deadline:
            return None

        delta = self.tenant_response_deadline - datetime.utcnow()
        return max(0, delta.days)

    def is_response_overdue(self):
        """Check if tenant response is overdue"""
        if not self.tenant_response_deadline:
            return False

        return datetime.utcnow() > self.tenant_response_deadline

    def can_auto_approve(self):
        """Check if claim can be auto-approved"""
        if self.status != DepositClaimStatus.SUBMITTED:
            return False

        # Auto-approve if tenant hasn't responded within deadline
        return self.is_response_overdue()

    def auto_approve_claim(self):
        """
        Auto-approve the claim when tenant doesn't respond within deadline
        Returns True if successfully auto-approved, False otherwise
        """
        if not self.can_auto_approve():
            return False
        
        try:
            # Update claim status and resolution details
            self.status = DepositClaimStatus.RESOLVED
            self.approved_amount = self.claimed_amount  # Approve full amount
            self.resolved_at = datetime.utcnow()
            self.resolution_notes = "Auto-approved due to no tenant response within 7-day deadline"
            self.resolved_by = None  # System auto-approval
            
            # Update the deposit transaction to reflect the approved claim
            if self.deposit_transaction:
                # Use the fund release service to properly handle the approved claim
                from src.services.fund_release_service import FundReleaseService
                
                try:
                    # Release the approved amount to landlord
                    release_result = FundReleaseService.release_accepted_claim(self.deposit_transaction, self)
                    
                    if not release_result['success']:
                        raise Exception(f"Failed to release funds: {release_result.get('error', 'Unknown error')}")
                    
                    # Update transaction status if this was the last pending claim
                    from src.models.deposit_claim import DepositClaim
                    pending_claims = DepositClaim.query.filter(
                        DepositClaim.deposit_transaction_id == self.deposit_transaction_id,
                        DepositClaim.status.in_([DepositClaimStatus.SUBMITTED, DepositClaimStatus.TENANT_NOTIFIED])
                    ).count()
                    
                    if pending_claims <= 1:  # This claim will be resolved, so check if it's the last one
                        # Check if all funds have been processed
                        from src.models.deposit_transaction import DepositTransactionStatus
                        total_processed = (self.deposit_transaction.released_amount or 0) + (self.deposit_transaction.refunded_amount or 0)
                        if total_processed >= self.deposit_transaction.amount:
                            self.deposit_transaction.status = DepositTransactionStatus.RELEASED
                        else:
                            self.deposit_transaction.status = DepositTransactionStatus.PARTIALLY_RELEASED
                        
                        self.deposit_transaction.resolved_at = datetime.utcnow()
                        self.deposit_transaction.is_fully_resolved = True
                        
                except Exception as fund_error:
                    # If fund release fails, still mark claim as resolved but log the error
                    print(f"Warning: Fund release failed for auto-approved claim {self.id}: {str(fund_error)}")
                    # Continue with basic status update
            
            # Commit the changes
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e

