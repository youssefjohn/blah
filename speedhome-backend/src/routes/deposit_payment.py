from flask import Blueprint, request, jsonify, current_app, session
from src.models import db
from src.models.tenancy_agreement import TenancyAgreement
from src.models.deposit_transaction import DepositTransaction, DepositTransactionStatus
from src.models.property import Property
from src.models.user import User
from src.services.deposit_service import DepositService
from src.services.stripe_connect_service import stripe_connect_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

deposit_payment_bp = Blueprint('deposit_payment', __name__)

@deposit_payment_bp.route('/api/deposit-payment/initiate/<int:agreement_id>', methods=['POST'])
def initiate_deposit_payment(agreement_id):
    """
    Initiate deposit payment by creating Stripe payment intent
    """
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        
        # Get the agreement
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({
                'success': False,
                'error': 'Agreement not found'
            }), 404
        
        # Verify user is the tenant
        if agreement.tenant_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403
        
        # Verify agreement is in correct status (website fee paid)
        if agreement.status != 'website_fee_paid':
            return jsonify({
                'success': False,
                'error': f'Agreement must be in website_fee_paid status. Current status: {agreement.status}'
            }), 400
        
        # Calculate deposit amount (2 months + 0.5 month utility)
        monthly_rent = float(agreement.monthly_rent)
        security_deposit = monthly_rent * 2
        utility_deposit = monthly_rent * 0.5
        total_deposit = security_deposit + utility_deposit
        
        # Get landlord information
        landlord = User.query.get(agreement.landlord_id)
        if not landlord:
            return jsonify({
                'success': False,
                'error': 'Landlord not found'
            }), 404
        
        # Auto-create Stripe Connect account if landlord doesn't have one
        if not landlord.stripe_account_id:
            landlord_data = {
                'email': landlord.email,
                'first_name': landlord.first_name or 'Landlord',
                'last_name': landlord.last_name or landlord.username,
                'phone': landlord.phone or '+60123456789',
                'business_name': landlord.company_name
            }
            
            account_result = stripe_connect_service.create_landlord_connect_account(landlord_data)
            
            if not account_result['success']:
                return jsonify({
                    'success': False,
                    'error': f'Failed to create landlord payment account: {account_result["error"]}'
                }), 400
            
            # Update landlord record
            landlord.stripe_account_id = account_result['account_id']
            landlord.stripe_account_status = 'pending'
            landlord.stripe_onboarding_completed = False
            landlord.stripe_charges_enabled = False
            landlord.stripe_payouts_enabled = False
            db.session.commit()
            
            logger.info(f"Auto-created Stripe Connect account {account_result['account_id']} for landlord {landlord.id}")
        
        # Check if landlord's account can receive payments
        account_status = stripe_connect_service.get_account_status(landlord.stripe_account_id)
        account_ready = account_status['success'] and account_status['charges_enabled']
        
        if not account_ready:
            # Account not ready - we'll create payment intent but mark as pending verification
            logger.info(f"Landlord {landlord.id} account not ready for charges. Payment will be held pending verification.")
        
        # Create payment intent based on account status
        property_obj = Property.query.get(agreement.property_id)
        
        if account_ready:
            # Normal flow - payment goes directly to landlord's verified account
            deposit_data = {
                'amount': total_deposit,
                'landlord_account_id': landlord.stripe_account_id,
                'tenant_email': agreement.tenant_email,
                'property_address': property_obj.address if property_obj else 'Property Address',
                'agreement_id': agreement_id,
                'application_fee': 0
            }
            
            result = stripe_connect_service.create_deposit_payment_intent(deposit_data)
            
            if not result['success']:
                return jsonify({
                    'success': False,
                    'error': f'Failed to create payment: {result["error"]}'
                }), 400
        else:
            # Pending verification flow - create regular payment intent to platform
            result = stripe_connect_service.create_pending_deposit_payment_intent({
                'amount': total_deposit,
                'tenant_email': agreement.tenant_email,
                'property_address': property_obj.address if property_obj else 'Property Address',
                'agreement_id': agreement_id,
                'landlord_id': landlord.id,
                'pending_account_id': landlord.stripe_account_id
            })
            
            if not result['success']:
                return jsonify({
                    'success': False,
                    'error': f'Failed to create payment: {result["error"]}'
                }), 400
        
        return jsonify({
            'success': True,
            'client_secret': result['client_secret'],
            'amount': result['amount'],
            'payment_intent_id': result['payment_intent_id'],
            'requires_landlord_verification': not account_ready,
            'message': 'Payment will be held until landlord completes account verification.' if not account_ready else None
        })
        
    except Exception as e:
        logger.error(f"Error initiating deposit payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to initiate deposit payment'
        }), 500

@deposit_payment_bp.route('/api/deposit-payment/complete/<int:agreement_id>', methods=['POST'])
def complete_deposit_payment(agreement_id):
    """
    Complete deposit payment and activate the tenancy agreement
    """
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        
        # Get the agreement
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({
                'success': False,
                'error': 'Agreement not found'
            }), 404
        
        # Verify user is the tenant
        if agreement.tenant_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403
        
        # Verify agreement is in correct status (website fee paid)
        if agreement.status != 'website_fee_paid':
            return jsonify({
                'success': False,
                'error': f'Agreement must be in website_fee_paid status. Current status: {agreement.status}'
            }), 400
        
        # Get payment data from request
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        
        if not payment_intent_id:
            return jsonify({
                'success': False,
                'error': 'Payment intent ID is required'
            }), 400
        
        # Verify payment with Stripe Connect service
        payment_result = stripe_connect_service.verify_payment_intent(payment_intent_id)
        
        if not payment_result['success']:
            return jsonify({
                'success': False,
                'error': payment_result['error']
            }), 400
            
        if payment_result['status'] != 'succeeded':
            return jsonify({
                'success': False,
                'error': 'Payment not completed'
            }), 400
        
        # Check if this is a pending verification payment
        is_pending_verification = False
        payment_intent = stripe_connect_service._get_payment_intent_details(payment_intent_id)
        if payment_intent and payment_intent.get('metadata', {}).get('type') == 'deposit_pending_verification':
            is_pending_verification = True
        
        # Get landlord for Stripe Connect account info
        landlord = User.query.get(agreement.landlord_id)
        if not landlord or not landlord.stripe_account_id:
            return jsonify({
                'success': False,
                'error': 'Landlord Connect account not found'
            }), 400
        
        # Create or update deposit transaction
        deposit = DepositTransaction.query.filter_by(tenancy_agreement_id=agreement_id).first()
        
        if not deposit:
            # Calculate amounts
            monthly_rent = float(agreement.monthly_rent)
            security_deposit = monthly_rent * 2
            utility_deposit = monthly_rent * 0.5
            total_amount = security_deposit + utility_deposit
            
            # Create new deposit transaction
            deposit_status = DepositTransactionStatus.PENDING_LANDLORD_VERIFICATION if is_pending_verification else DepositTransactionStatus.HELD_IN_ESCROW
            
            deposit = DepositTransaction(
                tenancy_agreement_id=agreement_id,
                tenant_id=user_id,
                landlord_id=agreement.landlord_id,
                property_id=agreement.property_id,
                amount=total_amount,
                calculation_base=monthly_rent,
                calculation_multiplier=2.5,  # 2 months security + 0.5 month utility
                status=deposit_status,
                payment_method='stripe_connect' if not is_pending_verification else 'stripe_pending',
                payment_intent_id=payment_intent_id,
                landlord_stripe_account_id=landlord.stripe_account_id,
                paid_at=datetime.utcnow()
            )
            db.session.add(deposit)
        else:
            # Update existing deposit
            deposit_status = DepositTransactionStatus.PENDING_LANDLORD_VERIFICATION if is_pending_verification else DepositTransactionStatus.HELD_IN_ESCROW
            deposit.status = deposit_status
            deposit.payment_method = 'stripe_connect' if not is_pending_verification else 'stripe_pending'
            deposit.payment_intent_id = payment_intent_id
            deposit.landlord_stripe_account_id = landlord.stripe_account_id
            deposit.paid_at = datetime.utcnow()
        
        # Activate the tenancy agreement (or set to pending if waiting for landlord verification)
        if is_pending_verification:
            agreement.status = 'deposit_paid_pending_verification'
            logger.info(f"Agreement {agreement_id} waiting for landlord verification")
            
            # Send urgent notification to landlord
            from ..services.deposit_notification_service import DepositNotificationService
            property_address = f"{property.title}, {property.location}" if property else 'Your Property'
            tenant = User.query.get(user_id)
            tenant_name = tenant.get_full_name() if tenant else 'Tenant'
            
            DepositNotificationService.notify_landlord_verification_required(
                landlord_id=landlord.id,
                agreement_id=agreement_id,
                tenant_name=tenant_name,
                property_address=property_address,
                deposit_amount=float(total_amount)
            )
            
            # Also notify tenant about protection guarantee
            DepositNotificationService.notify_tenant_deposit_protection(
                tenant_id=user_id,
                agreement_id=agreement_id,
                landlord_name=landlord.get_full_name(),
                property_address=property_address,
                deposit_amount=float(total_amount)
            )
        else:
            agreement.status = 'active'
            agreement.activated_at = datetime.utcnow()
        
        # Update property status to RENTED (only if fully activated)
        from ..models.property import Property, PropertyStatus
        property = Property.query.get(agreement.property_id)
        if property and not is_pending_verification:
            property.transition_to_rented()
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Deposit payment completed for agreement {agreement_id}")
        
        return jsonify({
            'success': True,
            'message': 'Deposit payment completed successfully' if not is_pending_verification else 'Deposit payment completed. Waiting for landlord verification.',
            'agreement_status': agreement.status,
            'deposit_id': deposit.id,
            'requires_landlord_verification': is_pending_verification,
            'verification_note': 'Landlord will receive an email to complete account setup. Funds will be transferred once verified.' if is_pending_verification else None,
            'protection_guarantee': 'Your deposit will be automatically refunded if the landlord doesn\'t complete verification within 3 days - guaranteed!' if is_pending_verification else None
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error completing deposit payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to complete deposit payment'
        }), 500

@deposit_payment_bp.route('/api/deposit-payment/<int:agreement_id>', methods=['POST'])
def process_deposit_payment(agreement_id):
    """
    Process deposit payment and activate the tenancy agreement
    """
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        
        # Get the agreement
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({
                'success': False,
                'error': 'Agreement not found'
            }), 404
        
        # Verify user is the tenant
        if agreement.tenant_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403
        
        # Verify agreement is in correct status (website fee paid)
        if agreement.status != 'website_fee_paid':
            return jsonify({
                'success': False,
                'error': f'Agreement must be in website_fee_paid status. Current status: {agreement.status}'
            }), 400
        
        # Get payment data from request
        data = request.get_json()
        payment_method = data.get('payment_method', 'credit_card')
        payment_data = data.get('payment_data', {})
        
        # Find existing deposit transaction
        deposit = DepositTransaction.query.filter_by(tenancy_agreement_id=agreement_id).first()
        if not deposit:
            return jsonify({
                'success': False,
                'error': 'Deposit transaction not found'
            }), 404
        
        # Get landlord for Stripe Connect verification
        landlord = User.query.get(agreement.landlord_id)
        if not landlord or not landlord.stripe_account_id:
            return jsonify({
                'success': False,
                'error': 'Landlord Connect account not found'
            }), 400
        
        # Verify payment intent if provided
        payment_intent_id = payment_data.get('payment_intent_id')
        if payment_intent_id:
            payment_result = stripe_connect_service.verify_payment_intent(payment_intent_id)
            if not payment_result['success'] or payment_result['status'] != 'succeeded':
                return jsonify({
                    'success': False,
                    'error': 'Payment verification failed'
                }), 400
        
        now = datetime.utcnow()
        
        # Update deposit transaction for Stripe Connect
        deposit.status = DepositTransactionStatus.HELD_IN_ESCROW
        deposit.payment_method = 'stripe_connect'
        deposit.payment_intent_id = payment_intent_id
        deposit.landlord_stripe_account_id = landlord.stripe_account_id
        deposit.paid_at = now
        deposit.escrow_status = 'held'
        deposit.escrow_held_at = now
        deposit.updated_at = now
        
        # Activate the tenancy agreement
        agreement.status = 'active'
        agreement.updated_at = now
        
        # Transition property to rented status
        property_obj = Property.query.get(agreement.property_id)
        if property_obj:
            if property_obj.transition_to_rented():
                logger.info(f"Property {property_obj.id} transitioned to rented status")
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Deposit payment processed for agreement {agreement_id}: RM{deposit.amount}")
        logger.info(f"Agreement {agreement_id} activated successfully")
        
        return jsonify({
            'success': True,
            'message': 'Deposit payment processed successfully',
            'agreement': {
                'id': agreement.id,
                'status': agreement.status,
                'updated_at': agreement.updated_at.isoformat()
            },
            'deposit': {
                'id': deposit.id,
                'amount': float(deposit.amount),
                'status': deposit.status.value,
                'paid_at': deposit.paid_at.isoformat() if deposit.paid_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing deposit payment for agreement {agreement_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@deposit_payment_bp.route('/api/deposit-payment/<int:agreement_id>/calculate', methods=['GET'])
def calculate_deposit_amount(agreement_id):
    """
    Calculate deposit amount for an agreement
    """
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        
        # Get the agreement
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({
                'success': False,
                'error': 'Agreement not found'
            }), 404
        
        # Verify user is the tenant
        if agreement.tenant_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403
        
        # Calculate deposit amounts
        monthly_rent = float(agreement.monthly_rent) if agreement.monthly_rent else 0.0
        security_deposit = monthly_rent * 2.0  # 2 months
        utility_deposit = monthly_rent * 0.5   # 0.5 month
        total_deposit = security_deposit + utility_deposit
        
        return jsonify({
            'success': True,
            'calculation': {
                'monthly_rent': monthly_rent,
                'security_deposit': security_deposit,
                'utility_deposit': utility_deposit,
                'total_deposit': total_deposit,
                'currency': 'MYR',
                'calculation_method': 'malaysian_standard_2_months'
            }
        })
        
    except Exception as e:
        logger.error(f"Error calculating deposit for agreement {agreement_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

