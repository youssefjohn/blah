from flask import Blueprint, request, jsonify, current_app, session
from src.models import db
from src.models.tenancy_agreement import TenancyAgreement
from src.models.deposit_transaction import DepositTransaction, DepositTransactionStatus
from src.models.property import Property
from src.services.deposit_service import DepositService
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
        
        # Create Stripe payment intent
        import stripe
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
        
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_deposit * 100),  # Convert to cents
            currency='myr',
            metadata={
                'agreement_id': agreement_id,
                'payment_type': 'deposit',
                'tenant_id': user_id
            }
        )
        
        return jsonify({
            'success': True,
            'client_secret': payment_intent.client_secret,
            'amount': total_deposit,
            'payment_intent_id': payment_intent.id
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
        
        # Verify payment with Stripe
        import stripe
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
        
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.status != 'succeeded':
            return jsonify({
                'success': False,
                'error': 'Payment not completed'
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
            deposit = DepositTransaction(
                tenancy_agreement_id=agreement_id,
                tenant_id=user_id,
                landlord_id=agreement.landlord_id,
                property_id=agreement.property_id,
                amount=total_amount,
                security_deposit_amount=security_deposit,
                utility_deposit_amount=utility_deposit,
                status=DepositTransactionStatus.HELD_IN_ESCROW,
                payment_method='stripe',
                payment_reference=payment_intent_id,
                paid_at=datetime.utcnow()
            )
            db.session.add(deposit)
        else:
            # Update existing deposit
            deposit.status = DepositTransactionStatus.HELD_IN_ESCROW
            deposit.payment_method = 'stripe'
            deposit.payment_reference = payment_intent_id
            deposit.paid_at = datetime.utcnow()
        
        # Activate the tenancy agreement
        agreement.status = 'active'
        agreement.activated_at = datetime.utcnow()
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Deposit payment completed for agreement {agreement_id}")
        
        return jsonify({
            'success': True,
            'message': 'Deposit payment completed successfully',
            'agreement_status': 'active',
            'deposit_id': deposit.id
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
        
        # In a real implementation, you would:
        # 1. Process payment with Stripe/payment gateway
        # 2. Verify payment success
        # 3. Update deposit status
        # 4. Activate agreement
        
        # For now, simulate successful payment
        now = datetime.utcnow()
        
        # Update deposit transaction
        deposit.status = DepositTransactionStatus.PAID
        deposit.payment_method = payment_method
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

