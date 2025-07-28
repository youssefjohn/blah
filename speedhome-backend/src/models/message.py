from datetime import datetime
from .user import db

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Message content and metadata
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    
    # Message type and status
    message_type = db.Column(db.String(20), default='text')  # 'text', 'image', 'file', 'system'
    is_read = db.Column(db.Boolean, default=False)
    is_edited = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # File attachment support (for future enhancement)
    attachment_url = db.Column(db.String(500), nullable=True)
    attachment_type = db.Column(db.String(50), nullable=True)  # 'image', 'document', etc.
    attachment_size = db.Column(db.Integer, nullable=True)  # in bytes
    
    # Relationships
    sender = db.relationship('User', backref='sent_messages')
    
    def __repr__(self):
        return f'<Message {self.id} - From:{self.sender_id} Conv:{self.conversation_id}>'
    
    def to_dict(self):
        """Convert message to dictionary for API responses"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'message_body': self.message_body,
            'message_type': self.message_type,
            'is_read': self.is_read,
            'is_edited': self.is_edited,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'sender_name': f"{self.sender.first_name} {self.sender.last_name}" if self.sender else None,
            'sender_role': self.sender.role if self.sender else None,
            'attachment_url': self.attachment_url,
            'attachment_type': self.attachment_type,
            'attachment_size': self.attachment_size
        }
    
    def mark_as_read(self, reader_id):
        """Mark message as read by a specific user"""
        # Only mark as read if the reader is not the sender
        if reader_id != self.sender_id and not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    def can_edit(self, user_id):
        """Check if a user can edit this message"""
        # Only sender can edit, and only within a reasonable time frame (e.g., 15 minutes)
        if user_id != self.sender_id:
            return False
        
        # Check if message is recent enough to edit (15 minutes)
        time_limit = datetime.utcnow() - self.created_at
        return time_limit.total_seconds() < 900  # 15 minutes
    
    def can_delete(self, user_id):
        """Check if a user can delete this message"""
        # Only sender can delete their own messages
        return user_id == self.sender_id

