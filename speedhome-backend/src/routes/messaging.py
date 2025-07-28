from flask import Blueprint, request, jsonify, session
from datetime import datetime
from ..models.user import db, User
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.booking import Booking
from ..models.property import Property

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/conversations', methods=['GET'])
def get_user_conversations():
    """Get all conversations for the current user"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get conversations where user is either tenant or landlord
        conversations = Conversation.query.filter(
            (Conversation.tenant_id == user_id) | (Conversation.landlord_id == user_id)
        ).order_by(Conversation.last_message_at.desc().nullslast(), Conversation.updated_at.desc()).all()
        
        conversations_data = []
        for conv in conversations:
            conv_dict = conv.to_dict()
            
            # Add unread message count for this user
            unread_count = Message.query.filter(
                Message.conversation_id == conv.id,
                Message.sender_id != user_id,
                Message.is_read == False
            ).count()
            conv_dict['unread_count'] = unread_count
            
            # Add the other participant's info
            other_participant = conv.get_other_participant(user_id)
            if other_participant:
                conv_dict['other_participant'] = {
                    'id': other_participant.id,
                    'name': f"{other_participant.first_name} {other_participant.last_name}",
                    'role': other_participant.role,
                    'profile_picture': other_participant.profile_picture
                }
            
            # Add booking status for context
            conv_dict['booking_status'] = conv.booking.status if conv.booking else None
            
            conversations_data.append(conv_dict)
        
        return jsonify({
            'success': True,
            'conversations': conversations_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

@messaging_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    """Get all messages for a specific conversation"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        
        # Verify user has access to this conversation
        conversation = Conversation.query.filter(
            Conversation.id == conversation_id,
            (Conversation.tenant_id == user_id) | (Conversation.landlord_id == user_id)
        ).first()
        
        if not conversation:
            return jsonify({'success': False, 'error': 'Conversation not found or access denied'}), 404
        
        # Get messages with pagination support
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        messages_query = Message.query.filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
        
        messages = messages_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        messages_data = [message.to_dict() for message in messages.items]
        
        # Mark unread messages as read
        unread_messages = Message.query.filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.is_read == False
        ).all()
        
        for message in unread_messages:
            message.mark_as_read(user_id)
        
        return jsonify({
            'success': True,
            'messages': messages_data,
            'pagination': {
                'page': messages.page,
                'pages': messages.pages,
                'per_page': messages.per_page,
                'total': messages.total,
                'has_next': messages.has_next,
                'has_prev': messages.has_prev
            },
            'conversation': conversation.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

@messaging_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """Send a new message in a conversation"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        data = request.get_json()
        
        if not data or 'message_body' not in data:
            return jsonify({'success': False, 'error': 'Message body is required'}), 400
        
        message_body = data['message_body'].strip()
        if not message_body:
            return jsonify({'success': False, 'error': 'Message cannot be empty'}), 400
        
        # Verify user has access to this conversation
        conversation = Conversation.query.filter(
            Conversation.id == conversation_id,
            (Conversation.tenant_id == user_id) | (Conversation.landlord_id == user_id)
        ).first()
        
        if not conversation:
            return jsonify({'success': False, 'error': 'Conversation not found or access denied'}), 404
        
        # Check if user can send messages (Rules of Engagement)
        booking = conversation.booking
        if not conversation.can_send_message(user_id, booking.status):
            return jsonify({
                'success': False, 
                'error': 'Cannot send messages for this booking. The viewing may be completed, cancelled, or declined.'
            }), 403
        
        # Create the message
        message = Message(
            conversation_id=conversation_id,
            sender_id=user_id,
            message_body=message_body,
            message_type=data.get('message_type', 'text')
        )
        
        db.session.add(message)
        
        # Update conversation metadata
        conversation.last_message_at = datetime.utcnow()
        conversation.last_message_by = user_id

        conversation.last_message_body = message_body

        conversation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

@messaging_bp.route('/conversations/create', methods=['POST'])
def create_conversation():
    """Create a new conversation (usually triggered when a booking is created)"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        data = request.get_json()
        
        if not data or 'booking_id' not in data:
            return jsonify({'success': False, 'error': 'Booking ID is required'}), 400
        
        booking_id = data['booking_id']
        
        # Get the booking and verify access
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Verify user is either the tenant who made the booking or the landlord who owns the property
        property_obj = Property.query.get(booking.property_id)
        if not property_obj:
            return jsonify({'success': False, 'error': 'Property not found'}), 404
        
        if user_id != booking.user_id and user_id != property_obj.owner_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Check if conversation already exists
        existing_conversation = Conversation.query.filter(
            Conversation.tenant_id == booking.user_id,
            Conversation.landlord_id == property_obj.owner_id,
            Conversation.booking_id == booking_id
        ).first()
        
        if existing_conversation:
            return jsonify({
                'success': True,
                'conversation': existing_conversation.to_dict(),
                'message': 'Conversation already exists'
            }), 200
        
        # Create new conversation
        conversation = Conversation(
            tenant_id=booking.user_id,
            landlord_id=property_obj.owner_id,
            booking_id=booking_id,
            property_id=booking.property_id,
            status='active'
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

@messaging_bp.route('/messages/<int:message_id>', methods=['PUT'])
def edit_message(message_id):
    """Edit an existing message"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        data = request.get_json()
        
        if not data or 'message_body' not in data:
            return jsonify({'success': False, 'error': 'Message body is required'}), 400
        
        message = Message.query.get(message_id)
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'}), 404
        
        if not message.can_edit(user_id):
            return jsonify({'success': False, 'error': 'Cannot edit this message'}), 403
        
        message.message_body = data['message_body'].strip()
        message.is_edited = True
        message.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

@messaging_bp.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        
        message = Message.query.get(message_id)
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'}), 404
        
        if not message.can_delete(user_id):
            return jsonify({'success': False, 'error': 'Cannot delete this message'}), 403
        
        conversation_id = message.conversation_id
        db.session.delete(message)
        
        # Update conversation's last message info if this was the last message
        conversation = Conversation.query.get(conversation_id)
        if conversation:
            last_message = Message.query.filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).first()
            
            if last_message:
                conversation.last_message_at = last_message.created_at
                conversation.last_message_by = last_message.sender_id
            else:
                conversation.last_message_at = None
                conversation.last_message_by = None
        
        db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500


@messaging_bp.route('/conversations/<int:conversation_id>/mark-read', methods=['POST'])
def mark_conversation_as_read(conversation_id):
    """Mark all unread messages in a conversation as read for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    # Security check: Ensure the user is a participant in the conversation
    conversation = Conversation.query.get(conversation_id)
    if not conversation or (user_id != conversation.tenant_id and user_id != conversation.landlord_id):
        return jsonify({'success': False, 'error': 'Conversation not found or unauthorized'}), 404

    # --- THIS IS THE FIX ---
    # Find all unread messages sent TO the current user (i.e., where the sender is NOT the current user)
    Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != user_id,  # Changed from recipient_id to sender_id
        Message.is_read == False
    ).update({'is_read': True})

    db.session.commit()

    return jsonify({'success': True, 'message': 'Messages marked as read'}), 200

