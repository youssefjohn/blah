"""
Deposit Deadline Service

Handles the 7-day inspection period logic:
- Tracks when tenancy ends and 7-day window begins
- Auto-finalizes claims after 7 days
- Releases undisputed balance after deadline
- Sends final notifications to tenant
"""

from datetime import datetime, timedelta
from ..models.user import db
from ..models.deposit_transaction import DepositTransaction, DepositTransactionStatus
from ..models.deposit_claim import DepositClaim, DepositClaimStatus
from ..models.tenancy_agreement import TenancyAgreement
from ..services.fund_release_service import fund_release_service
from ..services.deposit_notification_service import DepositNotificationService
import logging

logger = logging.getLogger(__name__)

class DepositDeadlineService:
    
    @staticmethod
    def get_inspection_period_status(deposit_transaction):
        """
        Get the current status of the 7-day inspection period.
        
        Returns:
        - days_remaining: int (0 if expired)
        - is_active: bool (True if within 7-day window)
        - deadline_date: datetime
        - can_add_claims: bool
        """
        try:
            # Get the tenancy agreement to find lease end date
            agreement = TenancyAgreement.query.get(deposit_transaction.tenancy_agreement_id)
            if not agreement or not agreement.lease_end_date:
                return {
                    'days_remaining': 0,
                    'is_active': False,
                    'deadline_date': None,
                    'can_add_claims': False,
                    'error': 'No lease end date found'
                }
            
            # Calculate 7-day deadline from lease end date
            lease_end = datetime.combine(agreement.lease_end_date, datetime.min.time())
            deadline_date = lease_end + timedelta(days=7)
            
            # Calculate days remaining
            now = datetime.utcnow()
            time_remaining = deadline_date - now
            days_remaining = max(0, time_remaining.days)
            
            # Check if still within inspection period
            is_active = now <= deadline_date
            can_add_claims = is_active and deposit_transaction.status == DepositTransactionStatus.HELD_IN_ESCROW
            
            return {
                'days_remaining': days_remaining,
                'is_active': is_active,
                'deadline_date': deadline_date,
                'can_add_claims': can_add_claims,
                'lease_end_date': agreement.lease_end_date
            }
            
        except Exception as e:
            logger.error(f"Error getting inspection period status: {e}")
            return {
                'days_remaining': 0,
                'is_active': False,
                'deadline_date': None,
                'can_add_claims': False,
                'error': str(e)
            }
    
    @staticmethod
    def finalize_claims_and_release_funds(deposit_transaction):
        """
        Finalize all claims for a deposit and release undisputed balance.
        This happens either:
        1. When landlord manually finalizes
        2. Automatically after 7-day deadline
        """
        try:
            logger.info(f"Finalizing claims for deposit {deposit_transaction.id}")
            
            # Get all claims for this deposit
            claims = DepositClaim.query.filter_by(
                deposit_transaction_id=deposit_transaction.id
            ).all()
            
            # Update all claims to SUBMITTED status (ready for tenant response)
            for claim in claims:
                if claim.status == DepositClaimStatus.DRAFT:
                    claim.status = DepositClaimStatus.SUBMITTED
                    claim.tenant_response_deadline = datetime.utcnow() + timedelta(days=7)
                    claim.updated_at = datetime.utcnow()
            
            # Release undisputed balance to tenant
            release_result = fund_release_service.release_undisputed_balance(deposit_transaction)
            
            # Send final notification to tenant with ALL claims
            if claims:
                # Send notification about all finalized claims
                for claim in claims:
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
            else:
                # No claims - full deposit refund
                deposit_transaction.status = DepositTransactionStatus.REFUNDED
                deposit_transaction.refunded_amount = deposit_transaction.amount
                deposit_transaction.refunded_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Successfully finalized {len(claims)} claims for deposit {deposit_transaction.id}")
            
            return {
                'success': True,
                'claims_count': len(claims),
                'undisputed_release': release_result,
                'message': 'Claims finalized and undisputed balance released'
            }
            
        except Exception as e:
            logger.error(f"Error finalizing claims: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def check_and_process_expired_deposits():
        """
        Background task to check for deposits where 7-day period has expired
        and auto-finalize them.
        """
        try:
            # Find all deposits that are still in escrow
            active_deposits = DepositTransaction.query.filter_by(
                status=DepositTransactionStatus.HELD_IN_ESCROW
            ).all()
            
            processed_count = 0
            
            for deposit in active_deposits:
                status = DepositDeadlineService.get_inspection_period_status(deposit)
                
                # If deadline has passed, auto-finalize
                if not status['is_active'] and not status.get('error'):
                    logger.info(f"Auto-finalizing expired deposit {deposit.id}")
                    result = DepositDeadlineService.finalize_claims_and_release_funds(deposit)
                    
                    if result['success']:
                        processed_count += 1
                    else:
                        logger.error(f"Failed to auto-finalize deposit {deposit.id}: {result.get('error')}")
            
            logger.info(f"Processed {processed_count} expired deposits")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error checking expired deposits: {e}")
            return 0

# Create service instance
deposit_deadline_service = DepositDeadlineService()

