from flask import Blueprint, request, jsonify, session
from ..models.user import db, User

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get profile: {str(e)}'
        }), 500

@profile_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            user.last_name = data['last_name'].strip()
        if 'phone' in data:
            user.phone = data['phone'].strip()
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
        if 'preferences' in data:
            user.set_preferences(data['preferences'])
        
        # Update username if provided and not taken
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username != user.username:
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    return jsonify({
                        'success': False,
                        'error': 'Username already taken'
                    }), 400
                user.username = new_username
                session['username'] = new_username
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to update profile: {str(e)}'
        }), 500

@profile_bp.route('/profile/picture', methods=['POST'])
def upload_profile_picture():
    """Upload profile picture"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        if 'image_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Image data is required'
            }), 400
        
        # Store base64 image data
        user.profile_picture = data['image_data']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile picture updated successfully',
            'profile_picture': user.profile_picture
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to upload profile picture: {str(e)}'
        }), 500

@profile_bp.route('/users/<int:user_id>', methods=['GET'])
def get_public_profile(user_id):
    """Get public profile of a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': user.to_public_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get profile: {str(e)}'
        }), 500

@profile_bp.route('/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'preferences': user.get_preferences()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get preferences: {str(e)}'
        }), 500

@profile_bp.route('/preferences', methods=['PUT'])
def update_preferences():
    """Update user preferences"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        user.set_preferences(data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully',
            'preferences': user.get_preferences()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to update preferences: {str(e)}'
        }), 500

