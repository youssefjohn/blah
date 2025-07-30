"""
Webhook Routes for External Service Integration
Handles webhooks from SignWell, Stripe, and other external services
"""

from flask import Blueprint, request, jsonify
import logging

from ..services.signwell_service import signwell_service
from ..services.stripe_service import stripe_service
from ..services.workflow_coordinator import workflow_coordinator

logger = logging.getLogger(__name__)

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/signwell', methods=['POST'])
def signwell_webhook():
    """Handle SignWell webhooks"""
    try:
        webhook_data = request.get_json()
        
        if not webhook_data:
            return jsonify({'error': 'No data provided'}), 400
        
        logger.info(f"Received SignWell webhook: {webhook_data.get('event', 'unknown')}")
        
        # Process webhook through SignWell service
        result = signwell_service.process_webhook(webhook_data)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        # Handle specific events through workflow coordinator
        event_type = webhook_data.get('event')
        signature_request_id = webhook_data.get('signature_request', {}).get('id')
        
        if event_type == 'signature_request.completed' and signature_request_id:
            # Handle signature completion
            completion_result = workflow_coordinator.handle_signature_completion(signature_request_id)
            
            if not completion_result['success']:
                logger.error(f"Failed to handle signature completion: {completion_result['error']}")
                # Don't return error to SignWell - we've acknowledged the webhook
        
        return jsonify({'status': 'success', 'message': 'Webhook processed'}), 200
        
    except Exception as e:
        logger.error(f"Error processing SignWell webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@webhooks_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature')
        
        if not signature:
            return jsonify({'error': 'Missing signature'}), 400
        
        logger.info("Received Stripe webhook")
        
        # Process webhook through Stripe service
        result = stripe_service.process_webhook(payload, signature)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        # Extract event data for workflow coordination
        try:
            import stripe
            event = stripe.Webhook.construct_event(
                payload, signature, stripe_service.webhook_secret
            )
            
            event_type = event['type']
            
            if event_type == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                payment_intent_id = payment_intent['id']
                
                # Handle payment completion
                completion_result = workflow_coordinator.handle_payment_completion(payment_intent_id)
                
                if not completion_result['success']:
                    logger.error(f"Failed to handle payment completion: {completion_result['error']}")
                    # Don't return error to Stripe - we've acknowledged the webhook
                    
        except Exception as e:
            logger.error(f"Error processing Stripe webhook event: {str(e)}")
        
        return jsonify({'status': 'success', 'message': 'Webhook processed'}), 200
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@webhooks_bp.route('/test', methods=['POST'])
def test_webhook():
    """Test webhook endpoint for development"""
    try:
        data = request.get_json()
        logger.info(f"Test webhook received: {data}")
        
        return jsonify({
            'status': 'success',
            'message': 'Test webhook processed',
            'received_data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing test webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@webhooks_bp.route('/status', methods=['GET'])
def webhook_status():
    """Get webhook service status"""
    try:
        service_status = workflow_coordinator.get_service_status()
        
        return jsonify({
            'status': 'operational',
            'services': service_status,
            'webhook_endpoints': {
                'signwell': '/api/webhooks/signwell',
                'stripe': '/api/webhooks/stripe',
                'test': '/api/webhooks/test'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting webhook status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

