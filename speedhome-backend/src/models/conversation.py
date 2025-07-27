from datetime import datetime
from .user import db


class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)

    # Participants
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Booking context
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)

    # Conversation status and metadata
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Last message info for quick access
    last_message_at = db.Column(db.DateTime, nullable=True)
    last_message_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # --- ADD THIS NEW COLUMN ---
    last_message_body = db.Column(db.String(255), nullable=True)

    # Relationships
    tenant = db.relationship('User', foreign_keys=[tenant_id], backref='tenant_conversations')
    landlord = db.relationship('User', foreign_keys=[landlord_id], backref='landlord_conversations')
    booking = db.relationship('Booking', backref='conversation')
    property = db.relationship('Property', backref='conversations')
    messages = db.relationship('Message', backref='conversation', cascade='all, delete-orphan',
                               order_by='Message.created_at')

    __table_args__ = (
    db.UniqueConstraint('tenant_id', 'landlord_id', 'booking_id', name='unique_conversation_per_booking'),)

    def __repr__(self):
        return f'<Conversation {self.id} - Tenant:{self.tenant_id} Landlord:{self.landlord_id} Booking:{self.booking_id}>'

    def to_dict(self):
        """Convert conversation to dictionary for API responses"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'landlord_id': self.landlord_id,
            'booking_id': self.booking_id,
            'property_id': self.property_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'last_message_by': self.last_message_by,

            # --- ADD THIS NEW FIELD TO THE RESPONSE ---
            'last_message_body': self.last_message_body,

            'tenant_name': f"{self.tenant.first_name} {self.tenant.last_name}" if self.tenant else None,
            'landlord_name': f"{self.landlord.first_name} {self.landlord.last_name}" if self.landlord else None,
            'property_title': self.property.title if self.property else None,
            'message_count': len(self.messages) if self.messages else 0
        }

    def can_send_message(self, user_id, booking_status):
        # ... (this function remains the same) ...
        if user_id not in [self.tenant_id, self.landlord_id]:
            return False
        if self.status in ['closed', 'read_only']:
            return False
        if booking_status in ['pending', 'confirmed']:
            return True
        if booking_status in ['cancelled', 'declined', 'completed']:
            self.status = 'read_only'
            db.session.commit()
            return False
        return False

    def get_other_participant(self, user_id):
        # ... (this function remains the same) ...
        if user_id == self.tenant_id:
            return self.landlord
        elif user_id == self.landlord_id:
            return self.tenant
        return None