# speedhome-backend/src/models/booking.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Booking details
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=True)
    
    # Appointment details
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)

    occupation = db.Column(db.String(100), nullable=True)
    monthly_income = db.Column(db.Integer, nullable=True)
    number_of_occupants = db.Column(db.Integer, nullable=True)
    
    # Status and management
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Reschedule information
    reschedule_requested_by = db.Column(db.String(20), nullable=True)
    proposed_date = db.Column(db.Date, nullable=True)
    proposed_time = db.Column(db.Time, nullable=True)
    original_date = db.Column(db.Date, nullable=True)
    original_time = db.Column(db.Time, nullable=True)

    def __repr__(self):
        return f'<Booking {self.id} - {self.name}>'

    def to_dict(self):
        # ✅ REVERTED THIS METHOD TO MATCH THE MODEL DEFINITION
        return {
            'id': self.id,
            'user_id': self.user_id,
            'property_id': self.property_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'reschedule_requested_by': self.reschedule_requested_by,
            'proposed_date': self.proposed_date.isoformat() if self.proposed_date else None,
            'proposed_time': self.proposed_time.strftime('%H:%M') if self.proposed_time else None,
            'original_date': self.original_date.isoformat() if self.original_date else None,
            'original_time': self.original_time.strftime('%H:%M') if self.original_time else None,
            'occupation': self.occupation,
            'monthly_income': self.monthly_income,
            'number_of_occupants': self.number_of_occupants,
        }