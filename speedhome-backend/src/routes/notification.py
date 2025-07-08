from flask import Blueprint, request, jsonify, session
from ..models.notification import Notification, db
from ..models.user import User

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Get all unread notifications for the logged-in user."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    user_id = session['user_id']
    
    notifications = Notification.query.filter_by(recipient_id=user_id, is_read=False).order_by(Notification.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'notifications': [n.to_dict() for n in notifications]
    })

@notification_bp.route('/notifications/mark-as-read', methods=['POST'])
def mark_as_read():
    """Mark specific notifications as read."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    data = request.get_json()
    notification_ids = data.get('ids', [])

    if not notification_ids:
        return jsonify({'success': False, 'error': 'No notification IDs provided'}), 400

    # Ensure the user can only mark their own notifications as read
    Notification.query.filter(
        Notification.id.in_(notification_ids),
        Notification.recipient_id == session['user_id']
    ).update({'is_read': True}, synchronize_session=False)

    db.session.commit()

    return jsonify({'success': True, 'message': 'Notifications marked as read.'})
