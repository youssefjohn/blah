"""
Stripe Configuration Routes
Provides Stripe configuration for frontend integration
"""

from flask import Blueprint, jsonify
from ..services.stripe_service import stripe_service
import logging

logger = logging.getLogger(__name__)

stripe_config_bp = Blueprint('stripe_config', __name__)

@stripe_config_bp.route('/config', methods=['GET'])
def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    try:
        publishable_key = stripe_service.get_publishable_key()
        
        if not publishable_key:
            return jsonify({
                'success': False,
                'error': 'Stripe not configured'
            }), 503
        
        return jsonify({
            'success': True,
            'publishable_key': publishable_key
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting Stripe config: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

