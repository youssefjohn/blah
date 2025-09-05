"""
Tenant Deposit Routes - Integration with main SpeedHome application
Provides deposit management endpoints for tenants in the main app
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from ..models.user import db
from ..models.deposit_transaction import DepositTransaction
from ..models.tenancy_agreement import TenancyAgreement
from ..services.deposit_service import DepositService
import logging

logger = logging.getLogger(__name__)

# Create blueprint for tenant deposit management
tenant_deposit_bp = Blueprint('tenant_deposit', __name__, url_prefix='/api/tenant/deposits')

@tenant_deposit_bp.route('/', methods=['GET'])
@login_required
def get_tenant_deposits():
    """Get all deposits for the current tenant"""
    try:
        tenant_id = current_user.id
        
        # Get all deposits where user is the tenant
        deposits = DepositTransaction.query.filter_by(tenant_id=tenant_id).all()
        
        return jsonify({
            'success': True,
            'deposits': [deposit.to_dict() for deposit in deposits],
            'count': len(deposits)
        })
        
    except Exception as e:
        logger.error(f"Error getting tenant deposits: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@tenant_deposit_bp.route('/agreement/<int:agreement_id>', methods=['GET'])
@login_required
def get_deposit_for_agreement(agreement_id):
    """Get deposit information for a specific tenancy agreement"""
    try:
        tenant_id = current_user.id
        
        # Verify the agreement belongs to this tenant
        agreement = TenancyAgreement.query.filter_by(
            id=agreement_id,
            tenant_id=tenant_id
        ).first()
        
        if not agreement:
            return jsonify({'success': False, 'error': 'Tenancy agreement not found'}), 404
        
        # Get the deposit for this agreement
        deposit_service = DepositService()
        result = deposit_service.get_deposit_for_agreement(agreement_id)
        
        if result['success']:
            # Add agreement information to the response
            deposit_data = result['deposit']
            deposit_data['agreement'] = {
                'id': agreement.id,
                'property_address': agreement.property.title + ", " + agreement.property.location if agreement.property else 'N/A',
                'monthly_rent': float(agreement.monthly_rent) if agreement.monthly_rent else 0,
                'lease_start_date': agreement.lease_start_date.isoformat() if agreement.lease_start_date else None,
                'lease_end_date': agreement.lease_end_date.isoformat() if agreement.lease_end_date else None,
                'status': agreement.status
            }
            
            return jsonify({
                'success': True,
                'deposit': deposit_data,
                'has_deposit': True
            })
        else:
            return jsonify({
                'success': True,
                'has_deposit': False,
                'message': 'No deposit found for this agreement',
                'agreement': {
                    'id': agreement.id,
                    'property_address': agreement.property.title + ", " + agreement.property.location if agreement.property else 'N/A',
                    'monthly_rent': float(agreement.monthly_rent) if agreement.monthly_rent else 0,
                    'status': agreement.status
                }
            })
        
    except Exception as e:
        logger.error(f"Error getting deposit for agreement {agreement_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@tenant_deposit_bp.route('/dashboard', methods=['GET'])
@login_required
def get_tenant_deposit_dashboard():
    """Get deposit dashboard data for tenant"""
    try:
        tenant_id = current_user.id
        
        # Get all active tenancy agreements for this tenant
        active_agreements = TenancyAgreement.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).all()
        
        dashboard_data = {
            'active_agreements': [],
            'total_deposits_held': 0.0,
            'upcoming_lease_expiries': [],
            'recent_activity': []
        }
        
        for agreement in active_agreements:
            # Get deposit for each agreement
            deposit = DepositTransaction.query.filter_by(
                tenancy_agreement_id=agreement.id
            ).first()
            
            agreement_data = {
                'agreement_id': agreement.id,
                'property_address': agreement.property.title + ", " + agreement.property.location if agreement.property else 'N/A',
                'monthly_rent': float(agreement.monthly_rent) if agreement.monthly_rent else 0,
                'lease_end_date': agreement.lease_end_date.isoformat() if agreement.lease_end_date else None,
                'has_deposit': deposit is not None
            }
            
            if deposit:
                agreement_data['deposit'] = {
                    'id': deposit.id,
                    'total_amount': float(deposit.total_amount),
                    'status': deposit.status.value if deposit.status else 'unknown',
                    'remaining_amount': float(deposit.get_remaining_amount()) if hasattr(deposit, 'get_remaining_amount') else float(deposit.total_amount)
                }
                dashboard_data['total_deposits_held'] += float(deposit.total_amount)
            
            dashboard_data['active_agreements'].append(agreement_data)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Error getting tenant deposit dashboard: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@tenant_deposit_bp.route('/<int:deposit_id>/status', methods=['GET'])
@login_required
def get_deposit_status(deposit_id):
    """Get detailed status of a specific deposit"""
    try:
        tenant_id = current_user.id
        
        # Get deposit and verify ownership
        deposit = DepositTransaction.query.filter_by(
            id=deposit_id,
            tenant_id=tenant_id
        ).first()
        
        if not deposit:
            return jsonify({'success': False, 'error': 'Deposit not found'}), 404
        
        # Get related claims and disputes
        from ..models.deposit_claim import DepositClaim
        from ..models.deposit_dispute import DepositDispute
        
        claims = DepositClaim.query.filter_by(deposit_transaction_id=deposit_id).all()
        disputes = DepositDispute.query.filter_by(deposit_transaction_id=deposit_id).all()
        
        status_data = {
            'deposit': deposit.to_dict(),
            'claims': [claim.to_dict() for claim in claims],
            'disputes': [dispute.to_dict() for dispute in disputes],
            'timeline': self._build_deposit_timeline(deposit, claims, disputes)
        }
        
        return jsonify({
            'success': True,
            'status': status_data
        })
        
    except Exception as e:
        logger.error(f"Error getting deposit status {deposit_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def _build_deposit_timeline(deposit, claims, disputes):
    """Build a timeline of deposit events"""
    timeline = []
    
    # Deposit creation
    timeline.append({
        'date': deposit.created_at.isoformat() if deposit.created_at else None,
        'event': 'Deposit Created',
        'description': f'Security deposit of RM {deposit.total_amount} held in escrow',
        'type': 'deposit'
    })
    
    # Claims
    for claim in claims:
        timeline.append({
            'date': claim.created_at.isoformat() if claim.created_at else None,
            'event': 'Claim Submitted',
            'description': f'Landlord claimed RM {claim.claimed_amount} for {claim.title}',
            'type': 'claim'
        })
    
    # Disputes
    for dispute in disputes:
        timeline.append({
            'date': dispute.created_at.isoformat() if dispute.created_at else None,
            'event': 'Dispute Created',
            'description': f'Tenant disputed claim - {dispute.tenant_response.value if dispute.tenant_response else "Response pending"}',
            'type': 'dispute'
        })
    
    # Sort by date
    timeline.sort(key=lambda x: x['date'] or '1970-01-01')
    
    return timeline

