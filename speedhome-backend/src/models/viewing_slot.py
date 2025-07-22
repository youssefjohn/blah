from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .user import db

class ViewingSlot(db.Model):
    """Model for individual viewing time slots - landlord-based"""
    __tablename__ = 'viewing_slots'
    
    id = Column(Integer, primary_key=True)
    landlord_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Changed from property_id to landlord_id
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    booked_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    booked_for_property_id = Column(Integer, ForeignKey('properties.id'), nullable=True)  # Which property was booked (if any)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    # Relationships
    landlord = relationship("User", back_populates="landlord_slots", foreign_keys=[landlord_id])
    booked_by = relationship("User", back_populates="booked_slots", foreign_keys=[booked_by_user_id])
    booked_property = relationship("Property", back_populates="viewing_slots", foreign_keys=[booked_for_property_id])
    
    def __repr__(self):
        return f'<ViewingSlot {self.id}: Landlord {self.landlord_id} on {self.date} at {self.start_time}-{self.end_time}>'
    
    def to_dict(self):
        """Convert ViewingSlot to dictionary"""
        return {
            'id': self.id,
            'landlord_id': self.landlord_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'is_available': self.is_available,
            'booked_by_user_id': self.booked_by_user_id,
            'booked_for_property_id': self.booked_for_property_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

