"""
Deposit Management Routes
Handles all deposit-related API endpoints including payments, claims, disputes, and status tracking
"""
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import logging
from ..models.user import db
from ..models.deposit_transaction import DepositTransaction, DepositTransactionStatus
from ..models.deposit_claim import DepositClaim, DepositClaimStatus, DepositClaimType
from ..models.deposit_dispute import DepositDispute, DepositDisputeStatus, DepositDisputeResponse
from ..models.tenancy_agreement import TenancyAgreement
from ..models.property import Property
from ..models.user import User
from decimal import Decimal
from ..models.conversation import Conversation
from ..services.deposit_notification_service import DepositNotificationService
from flask_login import login_required, current_user

# Create blueprint
deposit_bp = Blueprint('deposit', __name__)

@deposit_bp.route('/deposits/<int:deposit_id>/landlord-respond', methods=['POST'])
@login_required
def landlord_respond_to_disputes(deposit_id):
    """Handle landlord's response to tenant disputes"""
    try:
        current_user_id = current_user.id
        data = request.get_json()
        
        print(f"DEBUG: Landlord response for deposit {deposit_id} from user {current_user_id}")
        print(f"DEBUG: Response data: {data}")
        
        # Get the deposit transaction
        deposit = DepositTransaction.query.get_or_404(deposit_id)
        
        # Verify landlord owns this deposit
        if deposit.landlord_id != current_user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        # Process each response
        responses = data.get('responses', [])
        
        for response in responses:
            claim_id = response.get('claim_id')
            landlord_response = response.get('response')  # 'accept_counter', 'reject_counter', 'escalate'
            landlord_notes = response.get('landlord_notes', '')
            
            print(f"DEBUG: Processing claim {claim_id} with response {landlord_response}")
            
            # Get the claim
            claim = DepositClaim.query.get(claim_id)
            if not claim or claim.deposit_transaction_id != deposit_id:
                continue
            
            # Update claim based on landlord response
            if landlord_response == 'accept_counter':
                # Landlord accepts tenant's counter-offer
                if claim.tenant_counter_amount:
                    claim.approved_amount = claim.tenant_counter_amount
                    claim.status = DepositClaimStatus.RESOLVED
                    claim.resolution_notes = f"Landlord accepted tenant's counter-offer of RM {claim.tenant_counter_amount}. {landlord_notes}".strip()
                else:
                    # Tenant fully rejected, landlord accepts (no deduction)
                    claim.approved_amount = 0
                    claim.status = DepositClaimStatus.RESOLVED
                    claim.resolution_notes = f"Landlord accepted tenant's rejection. No deduction applied. {landlord_notes}".strip()
                    
            elif landlord_response == 'reject_counter':
                # Landlord rejects tenant's response, maintains original claim
                claim.status = DepositClaimStatus.DISPUTED
                claim.resolution_notes = f"Landlord rejected tenant's response. Maintaining original claim of RM {claim.claimed_amount}. {landlord_notes}".strip()
                
            elif landlord_response == 'escalate':
                # Escalate to mediation
                claim.status = DepositClaimStatus.MEDIATION
                claim.resolution_notes = f"Dispute escalated to mediation. {landlord_notes}".strip()
            
            claim.resolved_by = current_user_id
            claim.resolved_at = datetime.utcnow()
            claim.updated_at = datetime.utcnow()
            
            print(f"DEBUG: Updated claim {claim_id} status to {claim.status}")
        
        # Update deposit transaction status based on claim resolutions
        all_claims = DepositClaim.query.filter_by(deposit_transaction_id=deposit_id).all()
        
        resolved_count = sum(1 for claim in all_claims if claim.status in [DepositClaimStatus.RESOLVED, DepositClaimStatus.ACCEPTED])
        mediation_count = sum(1 for claim in all_claims if claim.status == DepositClaimStatus.MEDIATION)
        disputed_count = sum(1 for claim in all_claims if claim.status == DepositClaimStatus.DISPUTED)
        
        if mediation_count > 0:
            deposit.status = 'MEDIATION'
        elif disputed_count > 0:
            deposit.status = 'DISPUTED'
        elif resolved_count == len(all_claims):
            deposit.status = 'RESOLVED'
        
        deposit.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"DEBUG: Deposit status updated to {deposit.status}")
        
        return jsonify({
            'message': 'Landlord response submitted successfully',
            'deposit_status': deposit.status,
            'resolved_claims': resolved_count,
            'mediation_claims': mediation_count,
            'disputed_claims': disputed_count
        }), 200
        
    except Exception as e:
        print(f"ERROR: Error processing landlord response: {e}")
        db.session.rollback()
        return jsonify({'message': 'Internal server error'}), 500


from ..services.stripe_service import stripe_service
from ..services.s3_service import s3_service

# Create blueprint
deposit_bp = Blueprint('deposit', __name__, url_prefix='/api/deposits')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DEPOSIT TRANSACTION ROUTES
# ============================================================================

@deposit_bp.route('/', methods=['GET'])
def get_deposits():
    """Get all deposit transactions for the current user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    # Get deposits where user is either tenant or landlord
    deposits = DepositTransaction.query.filter(
        (DepositTransaction.tenant_id == user_id) | 
        (DepositTransaction.landlord_id == user_id)
    ).order_by(DepositTransaction.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'deposits': [deposit.to_dict() for deposit in deposits]
    })

@deposit_bp.route('/<int:deposit_id>', methods=['GET'])
def get_deposit(deposit_id):
    """Get a specific deposit transaction"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    deposit = DepositTransaction.query.get(deposit_id)
    if not deposit:
        return jsonify({'success': False, 'error': 'Deposit not found'}), 404
    
    # Check if user is authorized to view this deposit
    if deposit.tenant_id != user_id and deposit.landlord_id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    return jsonify({
        'success': True,
        'deposit': deposit.to_dict()
    })

@deposit_bp.route('/calculate', methods=['POST'])
def calculate_deposit():
    """Calculate deposit amount for a tenancy agreement"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    data = request.get_json()
    tenancy_agreement_id = data.get('tenancy_agreement_id')
    
    if not tenancy_agreement_id:
        return jsonify({'success': False, 'error': 'Tenancy agreement ID required'}), 400
    
    # Get tenancy agreement
    agreement = TenancyAgreement.query.get(tenancy_agreement_id)
    if not agreement:
        return jsonify({'success': False, 'error': 'Tenancy agreement not found'}), 404
    
    # Check authorization
    user_id = session['user_id']
    if agreement.tenant_id != user_id and agreement.landlord_id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        # Calculate deposit using Malaysian 2-month standard
        monthly_rent = agreement.monthly_rent
        base_deposit = monthly_rent * 2  # 2 months rent
        
        # Apply risk adjustments (simplified version)
        adjustment_factor = 1.0
        adjustment_reasons = []
        
        # Property type adjustments
        if agreement.property.property_type == 'luxury':
            adjustment_factor += 0.2
            adjustment_reasons.append("Luxury property premium (+20%)")
        elif agreement.property.property_type == 'basic':
            adjustment_factor -= 0.1
            adjustment_reasons.append("Basic property discount (-10%)")
        
        # Tenant profile adjustments (simplified)
        tenant = User.query.get(agreement.tenant_id)
        if tenant and hasattr(tenant, 'employment_type'):
            if tenant.employment_type == 'corporate':
                adjustment_factor -= 0.15
                adjustment_reasons.append("Corporate tenant discount (-15%)")
        
        # Apply limits (1.5 to 2.5 months)
        adjustment_factor = max(0.75, min(1.25, adjustment_factor))  # 1.5x to 2.5x multiplier
        
        final_amount = base_deposit * adjustment_factor
        multiplier = final_amount / monthly_rent
        
        return jsonify({
            'success': True,
            'calculation': {
                'monthly_rent': monthly_rent,
                'base_amount': base_deposit,
                'adjustment_factor': adjustment_factor,
                'adjustment_reasons': adjustment_reasons,
                'final_amount': round(final_amount, 2),
                'multiplier': round(multiplier, 1),
                'currency': 'MYR'
            }
        })
        
    except Exception as e:
        logger.error(f"Error calculating deposit: {str(e)}")
        return jsonify({'success': False, 'error': 'Calculation failed'}), 500

@deposit_bp.route('/create', methods=['POST'])
def create_deposit():
    """Create a new deposit transaction"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    data = request.get_json()
    tenancy_agreement_id = data.get('tenancy_agreement_id')
    
    if not tenancy_agreement_id:
        return jsonify({'success': False, 'error': 'Tenancy agreement ID required'}), 400
    
    # Get tenancy agreement
    agreement = TenancyAgreement.query.get(tenancy_agreement_id)
    if not agreement:
        return jsonify({'success': False, 'error': 'Tenancy agreement not found'}), 404
    
    # Check if deposit already exists
    existing_deposit = DepositTransaction.query.filter_by(
        tenancy_agreement_id=tenancy_agreement_id
    ).first()
    
    if existing_deposit:
        return jsonify({'success': False, 'error': 'Deposit already exists for this agreement'}), 400
    
    try:
        # Calculate deposit amount
        monthly_rent = agreement.monthly_rent
        base_deposit = monthly_rent * 2
        adjustment_factor = 1.0  # Simplified for now
        final_amount = base_deposit * adjustment_factor
        
        # Create deposit transaction
        deposit = DepositTransaction(
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=agreement.property_id,
            tenant_id=agreement.tenant_id,
            landlord_id=agreement.landlord_id,
            amount=round(final_amount, 2),
            calculation_base_rent=monthly_rent,
            calculation_multiplier=round(final_amount / monthly_rent, 1),
            calculation_details={
                'base_amount': base_deposit,
                'adjustment_factor': adjustment_factor,
                'adjustment_reasons': []
            },
            status=DepositTransactionStatus.PENDING
        )
        
        db.session.add(deposit)
        db.session.commit()
        
        # Send notification to tenant
        DepositNotificationService.notify_deposit_payment_required(deposit)
        
        logger.info(f"Created deposit transaction {deposit.id} for agreement {tenancy_agreement_id}")
        
        return jsonify({
            'success': True,
            'deposit': deposit.to_dict(),
            'message': 'Deposit transaction created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating deposit: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to create deposit'}), 500

# ============================================================================
# DEPOSIT CLAIM ROUTES
# ============================================================================

@deposit_bp.route('/<int:deposit_id>/claims', methods=['GET'])
def get_deposit_claims(deposit_id):
    """Get all claims for a deposit"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    deposit = DepositTransaction.query.get(deposit_id)
    if not deposit:
        return jsonify({'success': False, 'error': 'Deposit not found'}), 404
    
    # Check authorization
    if deposit.tenant_id != user_id and deposit.landlord_id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    claims = DepositClaim.query.filter_by(deposit_transaction_id=deposit_id).all()
    
    return jsonify({
        'success': True,
        'claims': [claim.to_dict() for claim in claims]
    })


@deposit_bp.route('/<int:deposit_id>/claims', methods=['POST'])
def create_deposit_claims(deposit_id):
    """Create one or more new deposit claims from a list of items."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    user_id = session['user_id']

    deposit = DepositTransaction.query.get(deposit_id)
    if not deposit:
        return jsonify({'success': False, 'error': 'Deposit not found'}), 404

    if deposit.landlord_id != user_id:
        return jsonify({'success': False, 'error': 'Only the landlord can create claims'}), 403

    try:
        data = request.get_json()

        if not data.get('title'):
            return jsonify({'success': False, 'error': 'A top-level claim title is required'}), 400

        claim_items = data.get('claim_items')
        if not claim_items or not isinstance(claim_items, list) or len(claim_items) == 0:
            return jsonify({'success': False, 'error': 'claim_items must be a non-empty list'}), 400

        total_claimed_in_request = sum(Decimal(str(item.get('amount', 0))) for item in claim_items)

        if total_claimed_in_request <= 0:
            return jsonify({'success': False, 'error': 'Total claim amount must be positive'}), 400

        if total_claimed_in_request > deposit.amount:
            return jsonify(
                {'success': False, 'error': 'Total claim amount cannot exceed the total deposit amount'}), 400

        claims_created = []
        for item in claim_items:
            if not all(k in item for k in ['title', 'amount', 'description']):
                continue

            # --- FIX: Convert the incoming reason string to the Enum member ---
            try:
                # The title from the frontend (e.g., "repair_damages") is converted to
                # uppercase to match the Enum member (e.g., DepositClaimType.REPAIR_DAMAGES)
                claim_type_enum = DepositClaimType[item['title'].upper()]
            except KeyError:
                # If the title from the frontend doesn't match any enum, default to OTHER
                claim_type_enum = DepositClaimType.OTHER

            new_claim = DepositClaim(
                deposit_transaction_id=deposit_id,
                tenancy_agreement_id=deposit.tenancy_agreement_id,
                property_id=deposit.property_id,
                landlord_id=deposit.landlord_id,
                tenant_id=deposit.tenant_id,
                title=item['title'],
                description=item.get('description', ''),
                claimed_amount=Decimal(str(item['amount'])),
                category=item.get('title'),
                claim_type=claim_type_enum,  # <-- Sets the required field
                evidence_photos=item.get('evidence_photos', []),
                evidence_documents=item.get('evidence_documents', []),
                status=DepositClaimStatus.SUBMITTED,
                tenant_response_deadline=datetime.utcnow() + timedelta(days=7),
                auto_approve_at=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(new_claim)
            claims_created.append(new_claim)

        if not claims_created:
            return jsonify({'success': False, 'error': 'No valid claim items were provided.'}), 400

        db.session.commit()

        for claim in claims_created:
            # --- FIX: Construct the address from existing fields ---
            full_address = f"{claim.property.title}, {claim.property.location}"

            DepositNotificationService.notify_deposit_claim_submitted(
                deposit_claim_id=claim.id,
                tenant_id=claim.tenant_id,
                claim_title=claim.title,
                claimed_amount=claim.claimed_amount,
                property_address=full_address,
                response_deadline=claim.tenant_response_deadline,
                tenancy_agreement_id=claim.tenancy_agreement_id,
                property_id=claim.property_id
            )

        logger.info(f"Created {len(claims_created)} deposit claim items for deposit {deposit_id}")

        return jsonify({
            'success': True,
            'message': f'Successfully created {len(claims_created)} claim items.'
        }), 201

    except Exception as e:
        logger.error(f"Error creating deposit claim: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to create claim: {str(e)}'}), 500


# ============================================================================
# DEPOSIT DISPUTE ROUTES
# ============================================================================

@deposit_bp.route('/disputes/<int:dispute_id>', methods=['GET'])
def get_dispute(dispute_id):
    """Get dispute details"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    dispute = DepositDispute.query.get(dispute_id)
    if not dispute:
        return jsonify({'success': False, 'error': 'Dispute not found'}), 404
    
    # Check authorization
    if dispute.tenant_id != user_id and dispute.landlord_id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    return jsonify({
        'success': True,
        'dispute': dispute.to_dict()
    })

@deposit_bp.route('/disputes/<int:dispute_id>/resolve', methods=['POST'])
def resolve_dispute(dispute_id):
    """Resolve a dispute (admin or mutual agreement)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    dispute = DepositDispute.query.get(dispute_id)
    if not dispute:
        return jsonify({'success': False, 'error': 'Dispute not found'}), 404
    
    try:
        data = request.get_json()
        resolution_amount = float(data.get('resolution_amount', 0))
        resolution_method = data.get('resolution_method', 'admin_decision')
        resolution_notes = data.get('resolution_notes', '')
        
        # Validate resolution amount
        if resolution_amount < 0 or resolution_amount > dispute.deposit_claim.claimed_amount:
            return jsonify({'success': False, 'error': 'Invalid resolution amount'}), 400
        
        # Resolve the dispute
        dispute.resolve_dispute(
            final_amount=resolution_amount,
            resolution_method=resolution_method,
            resolution_notes=resolution_notes,
            resolved_by_id=user_id
        )
        
        # Send resolution notifications
        DepositNotificationService.notify_deposit_dispute_resolved(dispute)
        
        logger.info(f"Resolved dispute {dispute_id} with amount {resolution_amount}")
        
        return jsonify({
            'success': True,
            'dispute': dispute.to_dict(),
            'message': 'Dispute resolved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error resolving dispute: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to resolve dispute'}), 500



# ============================================================================
# FRONTEND INTEGRATION ROUTES
# ============================================================================

@deposit_bp.route('/agreement/<int:agreement_id>', methods=['GET'])
def get_deposit_by_agreement(agreement_id):
    """Get deposit information for a specific tenancy agreement"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get the deposit transaction
        deposit = DepositTransaction.query.filter_by(
            tenancy_agreement_id=agreement_id
        ).first()
        
        if not deposit:
            return jsonify({'success': False, 'error': 'Deposit not found'}), 404
        
        # Check if user has access to this deposit
        if deposit.tenant_id != user_id and deposit.landlord_id != user_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Get tenancy agreement details
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if tenancy is ending soon (within 7 days)
        from datetime import datetime, timedelta
        tenancy_ending_soon = False
        if agreement.lease_end_date:
            days_until_end = (agreement.lease_end_date - datetime.now().date()).days
            tenancy_ending_soon = days_until_end <= 7 and days_until_end >= 0
        
        # Get claims for this deposit
        claims = DepositClaim.query.filter_by(
            deposit_transaction_id=deposit.id
        ).all()
        
        deposit_data = deposit.to_dict()
        deposit_data.update({
            'property_address': agreement.property_address,
            'tenant_name': agreement.tenant_full_name,
            'landlord_name': agreement.landlord_full_name,
            'tenancy_ending_soon': tenancy_ending_soon,
            'claims': [claim.to_dict() for claim in claims]
        })
        
        return jsonify({
            'success': True,
            'deposit': deposit_data
        })
        
    except Exception as e:
        logger.error(f"Error getting deposit by agreement: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get deposit'}), 500

@deposit_bp.route('/<int:deposit_id>/release', methods=['POST'])
def release_deposit(deposit_id):
    """Release full deposit to tenant"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        deposit = DepositTransaction.query.get(deposit_id)
        if not deposit:
            return jsonify({'success': False, 'error': 'Deposit not found'}), 404
        
        # Check if user is the landlord
        if deposit.landlord_id != user_id:
            return jsonify({'success': False, 'error': 'Only landlord can release deposit'}), 403
        
        # Check if deposit can be released
        if deposit.status != DepositTransactionStatus.HELD_IN_ESCROW:
            return jsonify({'success': False, 'error': 'Deposit cannot be released in current status'}), 400
        
        data = request.get_json()
        release_type = data.get('release_type', 'full')
        amount = float(data.get('amount', deposit.amount))
        
        if release_type == 'full' and amount != deposit.amount:
            return jsonify({'success': False, 'error': 'Amount must equal full deposit for full release'}), 400
        
        # Update deposit status
        deposit.status = DepositTransactionStatus.RELEASED
        deposit.released_amount = amount
        deposit.released_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send notification to tenant and landlord
        DepositNotificationService.notify_deposit_resolved(
            deposit_transaction_id=deposit.id,
            tenant_id=deposit.tenant_id,
            landlord_id=deposit.landlord_id,
            tenant_refund=amount,
            landlord_payout=0,
            property_address=deposit.tenancy_agreement.property_address,
            tenancy_agreement_id=deposit.tenancy_agreement_id,
            property_id=deposit.property_id
        )
        
        logger.info(f"Released deposit {deposit_id} amount {amount}")
        
        return jsonify({
            'success': True,
            'deposit': deposit.to_dict(),
            'message': 'Deposit released successfully'
        })
        
    except Exception as e:
        logger.error(f"Error releasing deposit: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to release deposit'}), 500


@deposit_bp.route('/claims/<int:claim_id>', methods=['GET'])
def get_claim_details(claim_id):
    """
    Get all claim details associated with a deposit, starting from one claim ID.
    This is for displaying the full dispute page.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    user_id = session['user_id']

    try:
        # Find the initial claim to identify the parent deposit transaction
        initial_claim = DepositClaim.query.get(claim_id)
        if not initial_claim:
            return jsonify({'success': False, 'error': 'Claim not found'}), 404

        # Check if user has access to this claim
        if initial_claim.tenant_id != user_id and initial_claim.landlord_id != user_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

        # Now, find all claims associated with the same deposit transaction
        all_claims = DepositClaim.query.filter_by(
            deposit_transaction_id=initial_claim.deposit_transaction_id
        ).order_by(DepositClaim.created_at.asc()).all()

        # Get parent objects once
        deposit = DepositTransaction.query.get(initial_claim.deposit_transaction_id)
        agreement = TenancyAgreement.query.get(initial_claim.tenancy_agreement_id)

        # Prepare the response
        claims_data = [claim.to_dict() for claim in all_claims]

        return jsonify({
            'success': True,
            'claims': claims_data,  # Return a list of claims
            'property_address': agreement.property_address if agreement else 'Unknown',
            'tenant_name': agreement.tenant_full_name if agreement else 'Unknown',
            'landlord_name': agreement.landlord_full_name if agreement else 'Unknown',
            'deposit_amount': float(deposit.amount) if deposit else 0
        })

    except Exception as e:
        logger.error(f"Error getting claim details: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get claim details'}), 500

@deposit_bp.route('/claims/<int:claim_id>/respond', methods=['POST'])
def respond_to_claim_items(claim_id):
    """Tenant response to individual claim items"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        print(f"DEBUG: Starting respond_to_claim_items for claim_id={claim_id}, user_id={user_id}")
        
        # Find the initial claim to get the deposit transaction
        initial_claim = DepositClaim.query.get(claim_id)
        if not initial_claim:
            print(f"DEBUG: Claim {claim_id} not found")
            return jsonify({'success': False, 'error': 'Claim not found'}), 404
        
        print(f"DEBUG: Found initial claim {claim_id}, tenant_id={initial_claim.tenant_id}")
        
        # Check if user is the tenant
        if initial_claim.tenant_id != user_id:
            print(f"DEBUG: User {user_id} is not the tenant {initial_claim.tenant_id}")
            return jsonify({'success': False, 'error': 'Only tenant can respond to claims'}), 403
        
        # Get all claims for this deposit transaction
        all_claims = DepositClaim.query.filter_by(
            deposit_transaction_id=initial_claim.deposit_transaction_id
        ).all()
        
        print(f"DEBUG: Found {len(all_claims)} claims for deposit transaction {initial_claim.deposit_transaction_id}")
        
        # Check if claims are still open for responses
        for claim in all_claims:
            if claim.status not in [DepositClaimStatus.SUBMITTED, DepositClaimStatus.TENANT_NOTIFIED]:
                print(f"DEBUG: Claim {claim.id} status {claim.status} not accepting responses")
                return jsonify({'success': False, 'error': 'Claims no longer accepting responses'}), 400
        
        data = request.get_json()
        print(f"DEBUG: Received data: {data}")
        
        responses = data.get('responses', [])
        print(f"DEBUG: Extracted responses: {responses}")
        
        if not responses:
            print("DEBUG: No responses provided")
            return jsonify({'success': False, 'error': 'No responses provided'}), 400
        
        # Create a mapping of item_id to response
        response_dict = {resp['item_id']: resp for resp in responses}
        print(f"DEBUG: Response dict: {response_dict}")
        
        # Process responses and calculate amounts
        total_accepted = 0
        total_disputed = 0
        has_disputes = False
        
        # Update each claim with the corresponding response
        for i, claim in enumerate(all_claims):
            # Use the claim ID as the item_id (since each claim is an individual item)
            item_id = claim.id
            print(f"DEBUG: Processing claim {claim.id} (item_id={item_id})")
            
            if item_id in response_dict:
                response = response_dict[item_id]
                print(f"DEBUG: Found response for claim {claim.id}: {response}")
                
                # Store response data in the claim
                if response['response'] == 'accept':
                    total_accepted += float(claim.claimed_amount)
                    claim.status = DepositClaimStatus.ACCEPTED
                    claim.tenant_response = 'accept'
                elif response['response'] == 'partial_accept':
                    counter_amount = float(response.get('counter_amount', 0))
                    total_accepted += counter_amount
                    total_disputed += float(claim.claimed_amount) - counter_amount
                    has_disputes = True
                    claim.status = DepositClaimStatus.DISPUTED
                    claim.tenant_response = 'partial_accept'
                    claim.tenant_counter_amount = counter_amount
                else:  # reject
                    total_disputed += float(claim.claimed_amount)
                    has_disputes = True
                    claim.status = DepositClaimStatus.DISPUTED
                    claim.tenant_response = 'reject'
                
                # Store common response data
                claim.tenant_explanation = response.get('explanation', '')
                claim.tenant_responded_at = datetime.utcnow()
                claim.updated_at = datetime.utcnow()
                
            else:
                print(f"DEBUG: No response found for claim {claim.id}")
        
        print(f"DEBUG: Processing complete. total_accepted={total_accepted}, total_disputed={total_disputed}, has_disputes={has_disputes}")
        
        # Commit all changes
        db.session.commit()
        
        # Send notifications (simplified for now)
        if has_disputes:
            logger.info(f"Disputes created for deposit transaction {initial_claim.deposit_transaction_id}")
        else:
            logger.info(f"All claims accepted for deposit transaction {initial_claim.deposit_transaction_id}")
        
        return jsonify({
            'success': True,
            'message': 'Response submitted successfully',
            'total_accepted': total_accepted,
            'total_disputed': total_disputed,
            'has_disputes': has_disputes
        })
        
    except Exception as e:
        logger.error(f"Error responding to claim: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to submit response'}), 500


# ============================================================================
# END OF DEPOSIT ROUTES
# ============================================================================

