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
            'property_id': self.property_id,
            'property': self.property.to_dict() if self.property else None,
            'tenant': self.tenant.to_dict() if self.tenant else None
        }
