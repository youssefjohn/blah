"""
Stripe Connect Service for Escrow-like Deposit Management
Handles landlord account creation, deposit holds, and conditional releases
"""

import os
import stripe
import logging
from datetime import datetime
from flask import current_app
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class StripeConnectService:
    """Service for managing escrow-like deposits using Stripe Connect"""
    
    def __init__(self):
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        logger.info(f"Initializing Stripe Connect Service")
        logger.info(f"STRIPE_SECRET_KEY present: {bool(self.stripe_secret_key)}")
        logger.info(f"STRIPE_SECRET_KEY value: {self.stripe_secret_key[:20] if self.stripe_secret_key else 'None'}...")
        logger.info(f"Available environment variables: {[k for k in os.environ.keys() if 'STRIPE' in k]}")
        
        if self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
            logger.info(f"Stripe API key configured successfully")
        else:
            logger.error("Stripe API key not configured - this will cause API failures")
            logger.error(f"All env vars: {list(os.environ.keys())}")
    
    def create_landlord_connect_account(self, landlord_data: Dict) -> Dict:
        """
        Create a Stripe Connect Express account for a landlord
        
        Args:
            landlord_data: Dictionary containing landlord information
            {
                'email': 'landlord@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+60123456789',
                'business_name': 'John Property Management' (optional)
            }
            
        Returns:
            dict: Account creation result
        """
        try:
            logger.info(f"Creating Stripe Connect account for landlord with data: {landlord_data}")
            
            # Debug: Check Stripe configuration
            logger.info(f"Stripe API Key present: {bool(self.stripe_secret_key)}")
            logger.info(f"Stripe API Key set globally: {bool(stripe.api_key)}")
            
            if not self.stripe_secret_key:
                logger.error("No Stripe API key available")
                return {
                    'success': False,
                    'error': 'Stripe API key not configured'
                }
            
            # Test Stripe connection first
            try:
                test_response = stripe.Account.list(limit=1)
                logger.info(f"Stripe connection test successful")
            except Exception as test_error:
                logger.error(f"Stripe connection test failed: {str(test_error)}")
                logger.error(f"Error type: {type(test_error)}")
                return {
                    'success': False,
                    'error': f"Stripe connection failed: {str(test_error)}"
                }
            
            # Prepare phone number in international format
            phone = landlord_data.get('phone', '')
            if phone and not phone.startswith('+'):
                # If no country code, assume Malaysian format for backwards compatibility
                if phone.startswith('0'):
                    phone = '+60' + phone[1:]  # Malaysia country code +60, remove leading 0
                else:
                    phone = '+60' + phone  # Add Malaysian country code
            # Phone number should already be in international format from frontend
            
            # Prepare account data
            account_data = {
                'type': 'express',
                'country': 'SG',  # Singapore (MY not supported for onboarding yet)
                'email': landlord_data.get('email'),
                'business_type': 'individual',  # Can be 'company' if business
                'individual': {
                    'first_name': landlord_data.get('first_name'),
                    'last_name': landlord_data.get('last_name'),
                    'email': landlord_data.get('email'),
                    'phone': phone,
                },
                'business_profile': {
                    'name': landlord_data.get('business_name', f"{landlord_data.get('first_name')} {landlord_data.get('last_name')}"),
                    'product_description': 'Property rental services',
                    'mcc': '6513',  # Real estate agents and managers
                },
                'capabilities': {
                    'transfers': {'requested': True},
                    'card_payments': {'requested': True},
                },
                'settings': {
                    'payouts': {
                        'schedule': {
                            'interval': 'manual'  # We control when payouts happen
                        }
                    }
                }
            }
            
            logger.info(f"Account creation data: {account_data}")
            
            # Create Express account for easy onboarding  
            account = stripe.Account.create(**account_data)
            
            logger.info(f"Created Stripe Connect account {account.id} for {landlord_data.get('email')}")
            
            return {
                'success': True,
                'account_id': account.id,
                'account': account
            }
            
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Stripe InvalidRequestError: {str(e)}")
            logger.error(f"Error code: {getattr(e, 'code', 'No code')}")
            logger.error(f"Error param: {getattr(e, 'param', 'No param')}")
            logger.error(f"Error details: {getattr(e, 'json_body', 'No details')}")
            return {
                'success': False,
                'error': f"Invalid request: {str(e)}"
            }
        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe AuthenticationError: {str(e)}")
            return {
                'success': False,
                'error': f"Authentication failed: Check your Stripe API keys"
            }
        except stripe.error.PermissionError as e:
            logger.error(f"Stripe PermissionError: {str(e)}")
            return {
                'success': False,
                'error': f"Permission denied: {str(e)}"
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating Connect account: {str(e)}")
            logger.error(f"Stripe error type: {type(e)}")
            logger.error(f"Stripe error details: {getattr(e, 'json_body', 'No details')}")
            return {
                'success': False,
                'error': f"Stripe error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"General error creating Connect account: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def create_account_link(self, account_id: str, refresh_url: str, return_url: str) -> Dict:
        """
        Create an account link for landlord onboarding
        
        Args:
            account_id: Stripe Connect account ID
            refresh_url: URL to return to if refresh is needed
            return_url: URL to return to after onboarding
            
        Returns:
            dict: Account link result
        """
        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type='account_onboarding',
            )
            
            return {
                'success': True,
                'url': account_link.url
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating account link: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_account_status(self, account_id: str) -> Dict:
        """
        Check the status of a Connect account
        
        Args:
            account_id: Stripe Connect account ID
            
        Returns:
            dict: Account status information
        """
        try:
            account = stripe.Account.retrieve(account_id)
            
            # Check if account can receive payments
            charges_enabled = account.charges_enabled
            details_submitted = account.details_submitted
            payouts_enabled = account.payouts_enabled
            
            return {
                'success': True,
                'account_id': account_id,
                'charges_enabled': charges_enabled,
                'details_submitted': details_submitted,
                'payouts_enabled': payouts_enabled,
                'requirements': account.requirements,
                'email': account.email
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving account: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment_intent(self, payment_intent_id: str) -> Dict:
        """Verify payment intent status"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'success': True,
                'status': payment_intent.status,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'payment_intent_id': payment_intent.id
            }
        except Exception as e:
            logger.error(f"Failed to verify payment intent {payment_intent_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_payment_intent_details(self, payment_intent_id: str) -> Dict:
        """Get full payment intent details including metadata"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'id': payment_intent.id,
                'status': payment_intent.status,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'metadata': payment_intent.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get payment intent details {payment_intent_id}: {e}")
            return None
    
    def create_deposit_payment_intent(self, deposit_data: Dict) -> Dict:
        """
        Create a payment intent for deposit that goes to landlord's Connect account
        
        Args:
            deposit_data: Dictionary containing deposit information
            {
                'amount': 3750.00,  # Amount in MYR
                'landlord_account_id': 'acct_xxx',
                'tenant_email': 'tenant@example.com',
                'property_address': '123 Main St',
                'agreement_id': 1,
                'application_fee': 100.00  # Optional platform fee
            }
            
        Returns:
            dict: Payment intent result
        """
        try:
            # Convert to cents
            amount_cents = int(deposit_data['amount'] * 100)
            application_fee_cents = int(deposit_data.get('application_fee', 0) * 100)
            
            payment_intent_data = {
                'amount': amount_cents,
                'currency': 'myr',
                'metadata': {
                    'agreement_id': str(deposit_data['agreement_id']),
                    'payment_type': 'deposit',
                    'property_address': deposit_data['property_address'],
                    'tenant_email': deposit_data['tenant_email']
                },
                'description': f"Security Deposit - {deposit_data['property_address']}",
                'receipt_email': deposit_data['tenant_email'],
                'automatic_payment_methods': {
                    'enabled': True,
                },
                'on_behalf_of': deposit_data['landlord_account_id'],
                'transfer_data': {
                    'destination': deposit_data['landlord_account_id'],
                },
            }
            
            # Add application fee if specified
            if application_fee_cents > 0:
                payment_intent_data['application_fee_amount'] = application_fee_cents
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)
            
            logger.info(f"Created deposit payment intent {payment_intent.id} for agreement {deposit_data['agreement_id']}")
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': deposit_data['amount'],
                'currency': 'MYR'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating deposit payment intent: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def hold_deposit_funds(self, account_id: str) -> Dict:
        """
        Put the Connect account in manual payout mode to hold funds
        
        Args:
            account_id: Stripe Connect account ID
            
        Returns:
            dict: Hold operation result
        """
        try:
            # Update account to manual payouts (holds all funds)
            account = stripe.Account.modify(
                account_id,
                settings={
                    'payouts': {
                        'schedule': {
                            'interval': 'manual'
                        }
                    }
                }
            )
            
            logger.info(f"Deposit funds held for account {account_id}")
            
            return {
                'success': True,
                'message': 'Funds are now held pending dispute resolution'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error holding funds: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_pending_deposit_payment_intent(self, deposit_data: Dict) -> Dict:
        """
        Create a payment intent that goes to platform account temporarily
        while landlord verifies their Connect account
        
        Args:
            deposit_data (Dict): Payment details with pending_account_id
        
        Returns:
            Dict: Payment intent details
        """
        try:
            # Create payment intent to platform account (not Connect account)
            payment_intent = stripe.PaymentIntent.create(
                amount=int(deposit_data['amount'] * 100),  # Convert to cents
                currency='myr',
                metadata={
                    'type': 'deposit_pending_verification',
                    'agreement_id': deposit_data['agreement_id'],
                    'landlord_id': deposit_data['landlord_id'],
                    'pending_account_id': deposit_data['pending_account_id'],
                    'tenant_email': deposit_data['tenant_email'],
                    'property_address': deposit_data['property_address']
                },
                receipt_email=deposit_data['tenant_email']
            )
            
            logger.info(f"Created pending deposit payment intent: {payment_intent.id}")
            
            return {
                'success': True,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'amount': deposit_data['amount'],
                'status': 'pending_verification'
            }
            
        except Exception as e:
            logger.error(f"Failed to create pending deposit payment intent: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def release_deposit_to_landlord(self, account_id: str, amount: float = None) -> Dict:
        """
        Release held funds to landlord (trigger manual payout)
        
        Args:
            account_id: Stripe Connect account ID
            amount: Amount to release (None for all available funds)
            
        Returns:
            dict: Release operation result
        """
        try:
            # Get account balance
            balance = stripe.Balance.retrieve(stripe_account=account_id)
            available_amount = balance.available[0].amount  # Amount in cents
            
            # Determine payout amount
            if amount is None:
                payout_amount = available_amount
            else:
                payout_amount = min(int(amount * 100), available_amount)
            
            if payout_amount <= 0:
                return {
                    'success': False,
                    'error': 'No funds available to release'
                }
            
            # Create manual payout
            payout = stripe.Payout.create(
                amount=payout_amount,
                currency='myr',
                method='instant',  # If available, otherwise standard
                stripe_account=account_id
            )
            
            logger.info(f"Released RM{payout_amount/100} to landlord account {account_id}")
            
            return {
                'success': True,
                'payout_id': payout.id,
                'amount': payout_amount / 100,
                'currency': 'MYR',
                'status': payout.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error releasing funds: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_deposit_to_tenant(self, payment_intent_id: str, amount: float = None, reason: str = None) -> Dict:
        """
        Refund deposit back to tenant
        
        Args:
            payment_intent_id: Original payment intent ID
            amount: Amount to refund (None for full refund)
            reason: Reason for refund
            
        Returns:
            dict: Refund result
        """
        try:
            refund_data = {
                'payment_intent': payment_intent_id
            }
            
            if amount is not None:
                refund_data['amount'] = int(amount * 100)  # Convert to cents
            
            if reason:
                refund_data['reason'] = reason
                refund_data['metadata'] = {'dispute_reason': reason}
            
            refund = stripe.Refund.create(**refund_data)
            
            logger.info(f"Refunded RM{refund.amount/100} to tenant for payment intent {payment_intent_id}")
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status,
                'reason': reason
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating refund: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_account_balance(self, account_id: str) -> Dict:
        """
        Get the current balance of a Connect account
        
        Args:
            account_id: Stripe Connect account ID
            
        Returns:
            dict: Balance information
        """
        try:
            balance = stripe.Balance.retrieve(stripe_account=account_id)
            
            available_myr = 0
            pending_myr = 0
            
            for balance_item in balance.available:
                if balance_item.currency == 'myr':
                    available_myr = balance_item.amount / 100
                    
            for balance_item in balance.pending:
                if balance_item.currency == 'myr':
                    pending_myr = balance_item.amount / 100
            
            return {
                'success': True,
                'available_balance': available_myr,
                'pending_balance': pending_myr,
                'currency': 'MYR'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving balance: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def transfer_deposit_to_connect_account(self, transfer_data: Dict) -> Dict:
        """Transfer funds from platform account to landlord's Connect account"""
        try:
            # Create transfer to Connect account
            transfer = stripe.Transfer.create(
                amount=int(transfer_data['amount'] * 100),  # Convert to cents
                currency='myr',
                destination=transfer_data['landlord_account_id'],
                metadata={
                    'deposit_id': transfer_data['deposit_id'],
                    'type': 'pending_deposit_transfer'
                }
            )
            
            logger.info(f"Successfully transferred deposit funds to Connect account: {transfer.id}")
            
            return {
                'success': True,
                'transfer_id': transfer.id,
                'amount': transfer_data['amount']
            }
            
        except Exception as e:
            logger.error(f"Failed to transfer deposit to Connect account: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_payment_intent(self, refund_data: Dict) -> Dict:
        """Refund a payment intent"""
        try:
            refund = stripe.Refund.create(
                payment_intent=refund_data['payment_intent_id'],
                amount=int(refund_data['amount'] * 100),  # Convert to cents
                reason=refund_data['reason'],
                metadata={
                    'deposit_id': refund_data['deposit_id'],
                    'refund_type': 'landlord_verification_expired'
                }
            )
            
            logger.info(f"Successfully refunded payment intent: {refund.id}")
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund_data['amount']
            }
            
        except Exception as e:
            logger.error(f"Failed to refund payment intent: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_webhook(self, payload: bytes, signature: str) -> Dict:
        """
        Process Stripe Connect webhook events
        
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
            logger.info(f"Processing Stripe Connect webhook: {event_type}")
            
            if event_type == 'payment_intent.succeeded':
                return self._handle_deposit_payment_succeeded(event['data']['object'])
            elif event_type == 'account.updated':
                return self._handle_account_updated(event['data']['object'])
            elif event_type == 'payout.created':
                return self._handle_payout_created(event['data']['object'])
            elif event_type == 'payout.paid':
                return self._handle_payout_paid(event['data']['object'])
            else:
                logger.info(f"Unhandled Stripe Connect webhook event: {event_type}")
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
    
    def _handle_deposit_payment_succeeded(self, payment_intent) -> Dict:
        """Handle successful deposit payment"""
        agreement_id = payment_intent.get('metadata', {}).get('agreement_id')
        logger.info(f"Deposit payment succeeded for agreement {agreement_id}: {payment_intent['id']}")
        
        # This will trigger automatic hold of funds since account is in manual payout mode
        return {'success': True, 'message': 'Deposit payment processed and held'}
    
    def _handle_account_updated(self, account) -> Dict:
        """Handle Connect account updates"""
        logger.info(f"Connect account updated: {account['id']}")
        return {'success': True, 'message': 'Account update processed'}
    
    def _handle_payout_created(self, payout) -> Dict:
        """Handle payout creation"""
        logger.info(f"Payout created: {payout['id']} for RM{payout['amount']/100}")
        return {'success': True, 'message': 'Payout creation processed'}
    
    def _handle_payout_paid(self, payout) -> Dict:
        """Handle payout completion"""
        logger.info(f"Payout completed: {payout['id']} for RM{payout['amount']/100}")
        return {'success': True, 'message': 'Payout completion processed'}

# Global instance
stripe_connect_service = StripeConnectService()