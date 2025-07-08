from datetime import datetime
from .user import db  # ✅ CORRECTED: Import the shared db instance from user.py

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    link = db.Column(db.String(255), nullable=True)  # Optional link for redirection
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to the User model
    recipient = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def __repr__(self):
        return f'<Notification {self.id} for User {self.recipient_id}>'

    def to_dict(self):
        """Converts the notification object to a dictionary."""
        return {
            'id': self.id,
            'recipient_id': self.recipient_id,
            'message': self.message,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat()
        }
