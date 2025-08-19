from datetime import datetime
from .user import db
from enum import Enum

class DepositTransactionStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    HELD_IN_ESCROW = "held_in_escrow"
    RELEASED = "released"
    REFUNDED = "refunded"
    PARTIALLY_RELEASED = "partially_released"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class DepositTransaction(db.Model):
    __tablename__ = 'deposit_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core references - integrate with existing models
    tenancy_agreement_id = db.Column(db.Integer, db.ForeignKey('tenancy_agreements.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Deposit details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    calculation_base = db.Column(db.Numeric(10, 2), nullable=False)  # Monthly rent used for calculation
    calculation_multiplier = db.Column(db.Numeric(3, 1), default=2.0)  # Usually 2 months
    adjustments = db.Column(db.JSON, default=dict)  # Risk adjustments and explanations
    
    # Status and workflow
    status = db.Column(db.Enum(DepositTransactionStatus), default=DepositTransactionStatus.PENDING)
    
    # Payment integration - use existing Stripe system
    payment_intent_id = db.Column(db.String(255), nullable=True)  # Stripe payment intent
    payment_method = db.Column(db.String(50), nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    # Escrow integration
    escrow_transaction_id = db.Column(db.String(255), nullable=True)
    escrow_status = db.Column(db.String(50), nullable=True)
    escrow_held_at = db.Column(db.DateTime, nullable=True)
    
    # Release/refund tracking
    released_amount = db.Column(db.Numeric(10, 2), default=0.00)
    refunded_amount = db.Column(db.Numeric(10, 2), default=0.00)
    released_at = db.Column(db.DateTime, nullable=True)
    refunded_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with existing models (using string references to avoid import issues)
    tenancy_agreement = db.relationship('TenancyAgreement', backref='deposit_transaction', lazy=True)
    property = db.relationship('Property', backref='deposit_transactions', lazy=True)
    tenant = db.relationship('User', foreign_keys=[tenant_id], backref='tenant_deposits', lazy=True)
    landlord = db.relationship('User', foreign_keys=[landlord_id], backref='landlord_deposits', lazy=True)
    
    def __repr__(self):
        return f'<DepositTransaction {self.id} - {self.amount} for Agreement {self.tenancy_agreement_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenancy_agreement_id': self.tenancy_agreement_id,
            'property_id': self.property_id,
            'tenant_id': self.tenant_id,
            'landlord_id': self.landlord_id,
            'amount': float(self.amount) if self.amount else 0,
            'calculation_base': float(self.calculation_base) if self.calculation_base else 0,
            'calculation_multiplier': float(self.calculation_multiplier) if self.calculation_multiplier else 2.0,
            'adjustments': self.adjustments or {},
            'status': self.status.value if self.status else 'pending',
            'payment_intent_id': self.payment_intent_id,
            'payment_method': self.payment_method,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'escrow_transaction_id': self.escrow_transaction_id,
            'escrow_status': self.escrow_status,
            'escrow_held_at': self.escrow_held_at.isoformat() if self.escrow_held_at else None,
            'released_amount': float(self.released_amount) if self.released_amount else 0,
            'refunded_amount': float(self.refunded_amount) if self.refunded_amount else 0,
            'released_at': self.released_at.isoformat() if self.released_at else None,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            
            # Related data
            'tenant_name': f"{self.tenant.first_name} {self.tenant.last_name}" if self.tenant else None,
            'landlord_name': f"{self.landlord.first_name} {self.landlord.last_name}" if self.landlord else None,
            'property_address': self.property.address if self.property else None,
        }
    
    @classmethod
    def calculate_deposit_amount(cls, monthly_rent, tenant_profile=None, property_details=None):
        """
        Calculate deposit amount using Malaysian 2-month standard with adjustments
        """
        base_amount = monthly_rent * 2.0  # Malaysian standard: 2 months rent
        
        adjustments = {
            'base_calculation': f"2 months × MYR {monthly_rent:,.2f}",
            'base_amount': float(base_amount),
            'adjustments': [],
            'total_adjustment': 0.0
        }
        
        # Risk-based adjustments (±20% max)
        adjustment_amount = 0.0
        
        # Tenant profile adjustments
        if tenant_profile:
            if tenant_profile.get('employment_type') == 'corporate':
                adjustment_amount -= base_amount * 0.1  # -10% for corporate tenants
                adjustments['adjustments'].append({
                    'type': 'Corporate tenant',
                    'amount': -base_amount * 0.1,
                    'reason': 'Stable employment with established company'
                })
            
            if tenant_profile.get('credit_score', 0) > 750:
                adjustment_amount -= base_amount * 0.05  # -5% for excellent credit
                adjustments['adjustments'].append({
                    'type': 'Excellent credit score',
                    'amount': -base_amount * 0.05,
                    'reason': 'Credit score above 750'
                })
        
        # Property-based adjustments
        if property_details:
            if property_details.get('monthly_rent', 0) > 8000:
                adjustment_amount += base_amount * 0.1  # +10% for luxury properties
                adjustments['adjustments'].append({
                    'type': 'Luxury property premium',
                    'amount': base_amount * 0.1,
                    'reason': 'High-value property above MYR 8,000/month'
                })
        
        # Cap adjustments at ±20%
        max_adjustment = base_amount * 0.2
        adjustment_amount = max(-max_adjustment, min(max_adjustment, adjustment_amount))
        
        final_amount = base_amount + adjustment_amount
        
        # Ensure minimum 1.5 months, maximum 2.5 months
        min_amount = monthly_rent * 1.5
        max_amount = monthly_rent * 2.5
        final_amount = max(min_amount, min(max_amount, final_amount))
        
        adjustments['total_adjustment'] = float(adjustment_amount)
        adjustments['final_amount'] = float(final_amount)
        adjustments['final_multiplier'] = round(final_amount / monthly_rent, 1)
        
        return final_amount, adjustments
    
    def mark_as_paid(self, payment_intent_id, payment_method):
        """Mark deposit as paid and update status"""
        self.status = DepositTransactionStatus.PAID
        self.payment_intent_id = payment_intent_id
        self.payment_method = payment_method
        self.paid_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_held_in_escrow(self, escrow_transaction_id):
        """Mark deposit as held in escrow"""
        self.status = DepositTransactionStatus.HELD_IN_ESCROW
        self.escrow_transaction_id = escrow_transaction_id
        self.escrow_held_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def process_release(self, amount, release_type='full'):
        """Process deposit release"""
        if release_type == 'full':
            self.status = DepositTransactionStatus.RELEASED
            self.released_amount = self.amount
        elif release_type == 'partial':
            self.status = DepositTransactionStatus.PARTIALLY_RELEASED
            self.released_amount = amount
        
        self.released_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def process_refund(self, amount, refund_type='full'):
        """Process deposit refund"""
        if refund_type == 'full':
            self.status = DepositTransactionStatus.REFUNDED
            self.refunded_amount = self.amount
        elif refund_type == 'partial':
            self.status = DepositTransactionStatus.PARTIALLY_RELEASED
            self.refunded_amount = amount
        
        self.refunded_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @property
    def remaining_amount(self):
        """Calculate remaining deposit amount"""
        return float(self.amount) - float(self.released_amount or 0) - float(self.refunded_amount or 0)
    
    @property
    def is_fully_resolved(self):
        """Check if deposit is fully resolved"""
        return self.remaining_amount <= 0
    
    @property
    def can_be_claimed(self):
        """Check if deposit can be claimed by landlord"""
        return (self.status == DepositTransactionStatus.HELD_IN_ESCROW and 
                self.tenancy_agreement and 
                self.tenancy_agreement.lease_end_date < datetime.utcnow().date())

