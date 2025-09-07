from .user import db
from datetime import datetime


class TenancyAgreement(db.Model):
    __tablename__ = 'tenancy_agreements'

    id = db.Column(db.Integer, primary_key=True)
    
    # Core References
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, unique=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Agreement Status and Workflow
    status = db.Column(db.String(50), nullable=False, default='pending_signatures')
    version = db.Column(db.Integer, nullable=False, default=1)
    
    # Timestamps for Workflow Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Signature Tracking
    landlord_signed_at = db.Column(db.DateTime, nullable=True)
    tenant_signed_at = db.Column(db.DateTime, nullable=True)
    landlord_signature_id = db.Column(db.String(255), nullable=True)  # SignWell signature ID
    tenant_signature_id = db.Column(db.String(255), nullable=True)    # SignWell signature ID
    
    # Payment Tracking
    payment_required = db.Column(db.Numeric(10, 2), nullable=False, default=399.00)  # RM 399 agreement fee
    payment_completed_at = db.Column(db.DateTime, nullable=True)
    payment_intent_id = db.Column(db.String(255), nullable=True)  # Stripe payment intent ID
    payment_method = db.Column(db.String(50), nullable=True)      # credit_card, fpx, etc.
    
    # Agreement Terms (copied from application and property at time of creation)
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False)
    security_deposit = db.Column(db.Numeric(10, 2), nullable=True)
    lease_start_date = db.Column(db.Date, nullable=False)
    lease_end_date = db.Column(db.Date, nullable=False)
    lease_duration_months = db.Column(db.Integer, nullable=False)
    
    # Property Details (snapshot at agreement time)
    property_address = db.Column(db.Text, nullable=False)
    property_type = db.Column(db.String(100), nullable=False)
    property_bedrooms = db.Column(db.Integer, nullable=True)
    property_bathrooms = db.Column(db.Integer, nullable=True)
    property_sqft = db.Column(db.Integer, nullable=True)
    
    # Tenant Details (snapshot at agreement time)
    tenant_full_name = db.Column(db.String(255), nullable=False)
    tenant_phone = db.Column(db.String(20), nullable=False)
    tenant_email = db.Column(db.String(255), nullable=False)
    tenant_ic_number = db.Column(db.String(20), nullable=True)
    
    # Landlord Details (snapshot at agreement time)
    landlord_full_name = db.Column(db.String(255), nullable=False)
    landlord_phone = db.Column(db.String(20), nullable=False)
    landlord_email = db.Column(db.String(255), nullable=False)
    landlord_ic_number = db.Column(db.String(20), nullable=True)
    
    # Document Storage
    draft_pdf_path = db.Column(db.String(500), nullable=True)     # S3 path to draft PDF
    final_pdf_path = db.Column(db.String(500), nullable=True)     # S3 path to final PDF
    signwell_document_id = db.Column(db.String(255), nullable=True)  # SignWell document ID
    
    # Additional Terms and Conditions
    special_terms = db.Column(db.Text, nullable=True)             # Any special clauses
    utilities_included = db.Column(db.Boolean, default=False)
    parking_included = db.Column(db.Boolean, default=False)
    furnished_status = db.Column(db.String(50), nullable=True)    # unfurnished, partially, fully
    
    # Cancellation and Expiry
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    cancellation_reason = db.Column(db.Text, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)            # Auto-expire if not completed
    
    # Withdrawal Tracking
    landlord_withdrawn_at = db.Column(db.DateTime, nullable=True)  # When landlord withdrew offer
    tenant_withdrawn_at = db.Column(db.DateTime, nullable=True)    # When tenant withdrew signature
    withdrawal_reason = db.Column(db.Text, nullable=True)          # Reason for withdrawal
    withdrawn_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Who withdrew

    def __repr__(self):
        return f'<TenancyAgreement {self.id}: {self.tenant_full_name} - {self.property_address}>'

    @property
    def is_fully_signed(self):
        """Check if both parties have signed the agreement"""
        return self.landlord_signed_at is not None and self.tenant_signed_at is not None

    @property
    def is_payment_completed(self):
        """Check if payment has been completed"""
        return self.payment_completed_at is not None

    @property
    def can_be_activated(self):
        """Check if agreement can be activated (fully signed and paid)"""
        return self.is_fully_signed and self.is_payment_completed

    @property
    def days_until_expiry(self):
        """Calculate days until agreement expires (if expires_at is set)"""
        if self.expires_at:
            delta = self.expires_at - datetime.utcnow()
            return max(0, delta.days)
        return None

    @property
    def hours_until_expiry(self):
        """Calculate hours until agreement expires (if expires_at is set)"""
        if self.expires_at:
            delta = self.expires_at - datetime.utcnow()
            return max(0, delta.total_seconds() / 3600)
        return None

    @property
    def is_expired(self):
        """Check if agreement has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    @property
    def is_withdrawn(self):
        """Check if agreement has been withdrawn by either party"""
        return self.landlord_withdrawn_at is not None or self.tenant_withdrawn_at is not None

    @property
    def can_landlord_withdraw(self):
        """Check if landlord can withdraw the offer"""
        # Landlord can withdraw if tenant hasn't signed yet and agreement isn't expired/cancelled
        return (self.tenant_signed_at is None and 
                not self.is_expired and 
                not self.is_withdrawn and 
                self.cancelled_at is None)

    @property
    def can_tenant_withdraw(self):
        """Check if tenant can withdraw their signature"""
        # Tenant can withdraw if they've signed but landlord hasn't counter-signed yet
        return (self.tenant_signed_at is not None and 
                self.landlord_signed_at is None and 
                not self.is_expired and 
                not self.is_withdrawn and 
                self.cancelled_at is None)

    @property
    def withdrawal_window_closed(self):
        """Check if withdrawal window is closed (both parties signed)"""
        return self.is_fully_signed

    def to_dict(self):
        """Serialize the agreement to a dictionary"""
        return {
            'id': self.id,
            'application_id': self.application_id,
            'property_id': self.property_id,
            'tenant_id': self.tenant_id,
            'landlord_id': self.landlord_id,
            
            'status': self.status,
            'version': self.version,
            
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            
            # Signature status
            'landlord_signed_at': self.landlord_signed_at.isoformat() if self.landlord_signed_at else None,
            'tenant_signed_at': self.tenant_signed_at.isoformat() if self.tenant_signed_at else None,
            'is_fully_signed': self.is_fully_signed,
            
            # Payment status
            'payment_required': float(self.payment_required) if self.payment_required else None,
            'payment_completed_at': self.payment_completed_at.isoformat() if self.payment_completed_at else None,
            'is_payment_completed': self.is_payment_completed,
            'payment_method': self.payment_method,
            
            # Agreement terms
            'monthly_rent': float(self.monthly_rent) if self.monthly_rent else None,
            'security_deposit': float(self.security_deposit) if self.security_deposit else None,
            'lease_start_date': self.lease_start_date.isoformat() if self.lease_start_date else None,
            'lease_end_date': self.lease_end_date.isoformat() if self.lease_end_date else None,
            'lease_duration_months': self.lease_duration_months,
            
            # Property details
            'property_address': self.property_address,
            'property_type': self.property_type,
            'property_bedrooms': self.property_bedrooms,
            'property_bathrooms': self.property_bathrooms,
            'property_sqft': self.property_sqft,
            
            # Tenant details
            'tenant_full_name': self.tenant_full_name,
            'tenant_phone': self.tenant_phone,
            'tenant_email': self.tenant_email,
            
            # Landlord details
            'landlord_full_name': self.landlord_full_name,
            'landlord_phone': self.landlord_phone,
            'landlord_email': self.landlord_email,
            
            # Document paths
            'draft_pdf_path': self.draft_pdf_path,
            'final_pdf_path': self.final_pdf_path,
            
            # Additional info
            'special_terms': self.special_terms,
            'utilities_included': self.utilities_included,
            'parking_included': self.parking_included,
            'furnished_status': self.furnished_status,
            
            # Status checks
            'can_be_activated': self.can_be_activated,
            'days_until_expiry': self.days_until_expiry,
            'hours_until_expiry': self.hours_until_expiry,
            'is_expired': self.is_expired,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            
            # Withdrawal info
            'is_withdrawn': self.is_withdrawn,
            'can_landlord_withdraw': self.can_landlord_withdraw,
            'can_tenant_withdraw': self.can_tenant_withdraw,
            'withdrawal_window_closed': self.withdrawal_window_closed,
            'landlord_withdrawn_at': self.landlord_withdrawn_at.isoformat() if self.landlord_withdrawn_at else None,
            'tenant_withdrawn_at': self.tenant_withdrawn_at.isoformat() if self.tenant_withdrawn_at else None,
            'withdrawal_reason': self.withdrawal_reason,
            
            # Cancellation info
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancellation_reason': self.cancellation_reason,
            
            # Deposit transaction info with enhanced data
            'deposit_transaction': self._get_enhanced_deposit_data() if hasattr(self, 'deposit_transaction') and self.deposit_transaction else None,
        }

    def _get_enhanced_deposit_data(self):
        """Get deposit transaction data with additional calculated fields like fund_breakdown"""
        if not self.deposit_transaction:
            return None
            
        deposit = self.deposit_transaction[0]
        deposit_data = deposit.to_dict()
        
        # Add tenancy status
        from datetime import datetime
        tenancy_has_ended = False
        if self.lease_end_date:
            tenancy_has_ended = datetime.now().date() > self.lease_end_date
        deposit_data['tenancy_has_ended'] = tenancy_has_ended
        
        # Add fund breakdown if available
        try:
            from src.services.fund_release_service import fund_release_service
            fund_breakdown = fund_release_service.get_deposit_breakdown(deposit)
            deposit_data['fund_breakdown'] = fund_breakdown
        except Exception as e:
            # If fund breakdown service fails, continue without it
            pass
            
        return deposit_data

