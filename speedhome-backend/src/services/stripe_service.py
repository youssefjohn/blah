"""
Stripe Service for Payment Processing
Handles agreement fee payments and subscription management
"""

import os
import stripe
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)

class StripeService:
    """Service for managing payments with Stripe"""
    
    def __init__(self):
        self.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if self.api_key:
            stripe.api_key = self.api_key
        else:
            logger.warning("Stripe API key not configured")
    
    def create_payment_intent(self, agreement):
        """
        Create a payment intent for agreement fee
        
        Args:
            agreement: TenancyAgreement model instance
            
        Returns:
            dict: Payment intent response
        """
        try:
            # Convert RM to cents (Stripe uses smallest currency unit)
            amount_cents = int(float(agreement.payment_required) * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='myr',
                metadata={
                    'agreement_id': str(agreement.id),
                    'property_address': agreement.property_address,
                    'tenant_email': agreement.tenant_email,
                    'landlord_email': agreement.landlord_email
                },
                description=f"Tenancy Agreement Fee - {agreement.property_address}",
                receipt_email=agreement.tenant_email,
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            logger.info(f"Created Stripe payment intent {payment_intent.id} for agreement {agreement.id}")
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': agreement.payment_required,
                'currency': 'MYR'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def confirm_payment_intent(self, payment_intent_id):
        """
        Confirm a payment intent
        
        Args:
            payment_intent_id: Stripe payment intent ID
            
        Returns:
            dict: Confirmation result
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            return {
                'success': True,
                'status': payment_intent.status,
                'payment_intent': payment_intent
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error confirming payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_payment_intent(self, payment_intent_id):
        """
        Retrieve a payment intent
        
        Args:
            payment_intent_id: Stripe payment intent ID
            
        Returns:
            dict: Payment intent data
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'success': True,
                'payment_intent': payment_intent,
                'status': payment_intent.status,
                'amount': payment_intent.amount / 100,  # Convert back to RM
                'currency': payment_intent.currency.upper()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment intent: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_customer(self, tenant_email, tenant_name):
        """
        Create a Stripe customer
        
        Args:
            tenant_email: Customer email
            tenant_name: Customer name
            
        Returns:
            dict: Customer creation result
        """
        try:
            customer = stripe.Customer.create(
                email=tenant_email,
                name=tenant_name,
                description=f"SpeedHome Tenant - {tenant_name}"
            )
            
            logger.info(f"Created Stripe customer {customer.id} for {tenant_email}")
            
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_setup_intent(self, customer_id):
        """
        Create a setup intent for saving payment methods
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            dict: Setup intent response
        """
        try:
            setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=['card'],
                usage='off_session'
            )
            
            return {
                'success': True,
                'setup_intent_id': setup_intent.id,
                'client_secret': setup_intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating setup intent: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_webhook(self, payload, signature):
        """
        Process Stripe webhook
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            dict: Processing result
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            event_type = event['type']
            logger.info(f"Processing Stripe webhook: {event_type}")
            
            if event_type == 'payment_intent.succeeded':
                return self._handle_payment_succeeded(event['data']['object'])
            elif event_type == 'payment_intent.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            elif event_type == 'payment_intent.canceled':
                return self._handle_payment_canceled(event['data']['object'])
            else:
                logger.info(f"Unhandled Stripe webhook event: {event_type}")
                return {'success': True, 'message': 'Event acknowledged'}
                
        except ValueError as e:
            logger.error(f"Invalid Stripe webhook payload: {str(e)}")
            return {'success': False, 'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid Stripe webhook signature: {str(e)}")
            return {'success': False, 'error': 'Invalid signature'}
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _handle_payment_succeeded(self, payment_intent):
        """Handle successful payment"""
        agreement_id = payment_intent.get('metadata', {}).get('agreement_id')
        logger.info(f"Payment succeeded for agreement {agreement_id}: {payment_intent['id']}")
        
        # This will be implemented in the workflow coordinator
        return {'success': True, 'message': 'Payment processed'}
    
    def _handle_payment_failed(self, payment_intent):
        """Handle failed payment"""
        agreement_id = payment_intent.get('metadata', {}).get('agreement_id')
        logger.warning(f"Payment failed for agreement {agreement_id}: {payment_intent['id']}")
        
        # This will be implemented in the workflow coordinator
        return {'success': True, 'message': 'Payment failure processed'}
    
    def _handle_payment_canceled(self, payment_intent):
        """Handle canceled payment"""
        agreement_id = payment_intent.get('metadata', {}).get('agreement_id')
        logger.info(f"Payment canceled for agreement {agreement_id}: {payment_intent['id']}")
        
        # This will be implemented in the workflow coordinator
        return {'success': True, 'message': 'Payment cancellation processed'}
    
    def refund_payment(self, payment_intent_id, amount=None, reason=None):
        """
        Refund a payment
        
        Args:
            payment_intent_id: Stripe payment intent ID
            amount: Amount to refund in cents (None for full refund)
            reason: Reason for refund
            
        Returns:
            dict: Refund result
        """
        try:
            refund_data = {
                'payment_intent': payment_intent_id
            }
            
            if amount:
                refund_data['amount'] = amount
            
            if reason:
                refund_data['reason'] = reason
            
            refund = stripe.Refund.create(**refund_data)
            
            logger.info(f"Created refund {refund.id} for payment intent {payment_intent_id}")
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating refund: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_publishable_key(self):
        """Get Stripe publishable key for frontend"""
        return self.publishable_key

# Global instance
stripe_service = StripeService()

