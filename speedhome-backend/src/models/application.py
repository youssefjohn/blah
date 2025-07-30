# src/models/application.py

from .user import db
from datetime import datetime


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False, default='pending') # pending, approved, rejected
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    is_seen_by_landlord = db.Column(db.Boolean, default=False, nullable=False)

    # Enhanced Application Form Fields
    # Personal Information
    full_name = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    emergency_contact_name = db.Column(db.String(255), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)

    # Employment Information
    employment_status = db.Column(db.String(100), nullable=True)  # employed, self-employed, unemployed, student, retired
    employer_name = db.Column(db.String(255), nullable=True)
    job_title = db.Column(db.String(255), nullable=True)
    employment_duration = db.Column(db.String(100), nullable=True)
    monthly_income = db.Column(db.Numeric(10, 2), nullable=True)
    additional_income = db.Column(db.Numeric(10, 2), nullable=True)
    additional_income_source = db.Column(db.String(255), nullable=True)

    # Financial Information
    bank_name = db.Column(db.String(255), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)
    credit_score = db.Column(db.Integer, nullable=True)
    monthly_expenses = db.Column(db.Numeric(10, 2), nullable=True)
    current_rent = db.Column(db.Numeric(10, 2), nullable=True)

    # Rental History
    previous_address = db.Column(db.Text, nullable=True)
    previous_landlord_name = db.Column(db.String(255), nullable=True)
    previous_landlord_phone = db.Column(db.String(20), nullable=True)
    reason_for_moving = db.Column(db.Text, nullable=True)
    rental_duration = db.Column(db.String(100), nullable=True)

    # Preferences and Additional Info
    move_in_date = db.Column(db.Date, nullable=True)
    lease_duration_preference = db.Column(db.String(100), nullable=True)
    number_of_occupants = db.Column(db.Integer, nullable=True)
    pets = db.Column(db.Boolean, default=False)
    pet_details = db.Column(db.Text, nullable=True)
    smoking = db.Column(db.Boolean, default=False)
    additional_notes = db.Column(db.Text, nullable=True)

    # Document Upload Fields
    id_document_path = db.Column(db.String(500), nullable=True)
    income_proof_path = db.Column(db.String(500), nullable=True)
    employment_letter_path = db.Column(db.String(500), nullable=True)
    bank_statement_path = db.Column(db.String(500), nullable=True)
    reference_letter_path = db.Column(db.String(500), nullable=True)
    credit_check_path = db.Column(db.String(500), nullable=True)
    additional_documents_path = db.Column(db.Text, nullable=True)  # JSON array of file paths

    # Application Completion Status
    step_completed = db.Column(db.Integer, default=0)  # Track which step user is on (0-6)
    is_complete = db.Column(db.Boolean, default=False)

    # Relationships
    tenant = db.relationship('User', foreign_keys=[tenant_id], backref='sent_applications')
    property = db.relationship('Property', foreign_keys=[property_id], backref='applications')

    def to_dict(self):
        """Serializes the object to a dictionary."""
        return {
            'id': self.id,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'property_id': self.property_id,
            'is_seen_by_landlord': self.is_seen_by_landlord,
            'property': self.property.to_dict() if self.property else None,
            'tenant': self.tenant.to_dict() if self.tenant else None,
            
            # Enhanced fields
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            
            'employment_status': self.employment_status,
            'employer_name': self.employer_name,
            'job_title': self.job_title,
            'employment_duration': self.employment_duration,
            'monthly_income': float(self.monthly_income) if self.monthly_income else None,
            'additional_income': float(self.additional_income) if self.additional_income else None,
            'additional_income_source': self.additional_income_source,
            
            'bank_name': self.bank_name,
            'account_number': self.account_number,
            'credit_score': self.credit_score,
            'monthly_expenses': float(self.monthly_expenses) if self.monthly_expenses else None,
            'current_rent': float(self.current_rent) if self.current_rent else None,
            
            'previous_address': self.previous_address,
            'previous_landlord_name': self.previous_landlord_name,
            'previous_landlord_phone': self.previous_landlord_phone,
            'reason_for_moving': self.reason_for_moving,
            'rental_duration': self.rental_duration,
            
            'move_in_date': self.move_in_date.isoformat() if self.move_in_date else None,
            'lease_duration_preference': self.lease_duration_preference,
            'number_of_occupants': self.number_of_occupants,
            'pets': self.pets,
            'pet_details': self.pet_details,
            'smoking': self.smoking,
            'additional_notes': self.additional_notes,
            
            'id_document_path': self.id_document_path,
            'income_proof_path': self.income_proof_path,
            'employment_letter_path': self.employment_letter_path,
            'bank_statement_path': self.bank_statement_path,
            'reference_letter_path': self.reference_letter_path,
            'additional_documents_path': self.additional_documents_path,
            
            'step_completed': self.step_completed,
            'is_complete': self.is_complete,
            
            # Calculated fields
            'rent_to_income_ratio': self.calculate_rent_to_income_ratio()
        }
    
    def calculate_rent_to_income_ratio(self):
        """Calculate rent-to-income ratio for financial analysis."""
        if self.monthly_income and self.property and self.property.price:
            total_income = float(self.monthly_income)
            if self.additional_income:
                total_income += float(self.additional_income)
            
            if total_income > 0:
                ratio = (float(self.property.price) / total_income) * 100
                return round(ratio, 2)
        return None
