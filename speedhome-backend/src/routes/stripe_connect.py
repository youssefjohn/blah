"""
Stripe Connect API Routes
Handles landlord account creation, onboarding, and status checking
"""

from flask import Blueprint, request, jsonify, session, url_for, current_app
from src.models import db
from src.models.user import User
from src.services.stripe_connect_service import stripe_connect_service
import logging

logger = logging.getLogger(__name__)

stripe_connect_bp = Blueprint('stripe_connect', __name__, url_prefix='/api/stripe-connect')

@stripe_connect_bp.route('/create-landlord-account', methods=['POST'])
def create_landlord_account():
    """
    Create a Stripe Connect account for a landlord
    """
    logger.info(f"=== Starting create_landlord_account request ===")
    
    if 'user_id' not in session:
        logger.info("No user_id in session - authentication failed")
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    logger.info(f"User ID from session: {user_id}")
    
    try:
        # Get the user and verify they're a landlord
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'landlord':
            return jsonify({'error': 'Only landlords can create Connect accounts'}), 403
        
        # Check if user already has a Connect account
        if user.stripe_account_id:
            return jsonify({
                'success': True,
                'account_id': user.stripe_account_id,
                'message': 'Connect account already exists'
            })
        
        # Get additional data from request
        data = request.get_json() or {}
        
        # Prepare landlord data
        landlord_data = {
            'email': user.email,
            'first_name': user.first_name or 'Landlord',
            'last_name': user.last_name or user.username,
            'phone': user.phone or '+60123456789',  # Default Malaysian number format
            'business_name': data.get('business_name') or user.company_name
        }
        
        # Debug logging before Stripe call
        logger.info(f"About to call stripe_connect_service.create_landlord_connect_account with data: {landlord_data}")
        
        # Create Connect account
        result = stripe_connect_service.create_landlord_connect_account(landlord_data)
        
        logger.info(f"Stripe service returned: {result}")
        
        if result['success']:
            # Update user record
            user.stripe_account_id = result['account_id']
            user.stripe_account_status = 'pending'
            user.stripe_onboarding_completed = False
            user.stripe_charges_enabled = False
            user.stripe_payouts_enabled = False
            
            db.session.commit()
            
            logger.info(f"Created Stripe Connect account for landlord {user_id}")
            
            return jsonify({
                'success': True,
                'account_id': result['account_id'],
                'message': 'Connect account created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating Connect account for user {user_id}: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Failed to create Connect account'
        }), 500

@stripe_connect_bp.route('/onboarding-link', methods=['POST'])
def create_onboarding_link():
    """
    Create an onboarding link for a landlord's Connect account
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'landlord':
            return jsonify({'error': 'Only landlords can access Connect onboarding'}), 403
        
        if not user.stripe_account_id:
            return jsonify({'error': 'No Connect account found. Please create one first.'}), 400
        
        # Create onboarding URLs
        base_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        refresh_url = f"{base_url}/landlord/stripe/refresh"
        return_url = f"{base_url}/landlord/stripe/complete"
        
        # Create account link
        result = stripe_connect_service.create_account_link(
            user.stripe_account_id, 
            refresh_url, 
            return_url
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'onboarding_url': result['url']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error creating onboarding link for user {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create onboarding link'
        }), 500

@stripe_connect_bp.route('/account-status', methods=['GET'])
def get_account_status():
    """
    Get the current status of a landlord's Connect account
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'landlord':
            return jsonify({'error': 'Only landlords can check Connect account status'}), 403
        
        if not user.stripe_account_id:
            return jsonify({
                'success': True,
                'has_account': False,
                'account_status': 'not_created'
            })
        
        # Get account status from Stripe
        result = stripe_connect_service.get_account_status(user.stripe_account_id)
        
        if result['success']:
            # Update user record with latest status
            user.stripe_charges_enabled = result['charges_enabled']
            user.stripe_payouts_enabled = result['payouts_enabled']
            user.stripe_onboarding_completed = result['details_submitted']
            
            if result['charges_enabled'] and result['payouts_enabled']:
                user.stripe_account_status = 'active'
            elif result['details_submitted']:
                user.stripe_account_status = 'pending_verification'
            else:
                user.stripe_account_status = 'pending'
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'has_account': True,
                'account_id': user.stripe_account_id,
                'account_status': user.stripe_account_status,
                'charges_enabled': result['charges_enabled'],
                'payouts_enabled': result['payouts_enabled'],
                'details_submitted': result['details_submitted'],
                'onboarding_completed': user.stripe_onboarding_completed,
                'requirements': result.get('requirements', {})
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error getting account status for user {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get account status'
        }), 500

@stripe_connect_bp.route('/account-balance', methods=['GET'])
def get_account_balance():
    """
    Get the current balance of a landlord's Connect account
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'landlord':
            return jsonify({'error': 'Only landlords can check Connect account balance'}), 403
        
        if not user.stripe_account_id:
            return jsonify({'error': 'No Connect account found'}), 400
        
        # Get account balance from Stripe
        result = stripe_connect_service.get_account_balance(user.stripe_account_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'available_balance': result['available_balance'],
                'pending_balance': result['pending_balance'],
                'currency': result['currency']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error getting account balance for user {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get account balance'
        }), 500

@stripe_connect_bp.route('/refresh-onboarding', methods=['POST'])
def refresh_onboarding():
    """
    Refresh the onboarding link when it expires or needs to be refreshed
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get the user
        user = User.query.get(user_id)
        if not user or user.role != 'landlord':
            return jsonify({'error': 'Invalid user'}), 403
        
        if not user.stripe_account_id:
            return jsonify({'error': 'No Connect account found'}), 400
        
        # Create fresh onboarding link
        base_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        refresh_url = f"{base_url}/landlord/stripe/refresh"
        return_url = f"{base_url}/landlord/stripe/complete"
        
        result = stripe_connect_service.create_account_link(
            user.stripe_account_id, 
            refresh_url, 
            return_url
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'onboarding_url': result['url']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error refreshing onboarding for user {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to refresh onboarding link'
        }), 500

@stripe_connect_bp.route('/webhook', methods=['POST'])
def handle_connect_webhook():
    """
    Handle Stripe Connect webhooks
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        if not sig_header:
            return jsonify({'error': 'No signature header'}), 400
        
        # Process webhook
        result = stripe_connect_service.process_webhook(payload, sig_header)
        
        if result['success']:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error handling Connect webhook: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500