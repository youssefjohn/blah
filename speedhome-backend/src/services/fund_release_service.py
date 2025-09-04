"""
Fund Release Service

Handles automatic release of deposit funds based on claim statuses.
Implements fair release logic where only disputed amounts are held in escrow.
"""
from datetime import datetime
from decimal import Decimal
from ..models.user import db
from ..models.deposit_transaction import DepositTransaction, DepositTransactionStatus
from ..models.deposit_claim import DepositClaim, DepositClaimStatus
from ..services.stripe_service import stripe_service
import logging

logger = logging.getLogger(__name__)

class FundReleaseService:
    
    @staticmethod
    def calculate_undisputed_balance(deposit_transaction):
        """
        Calculate the undisputed balance that should be immediately released to tenant
        when landlord submits claims.
        
        Formula: Total Deposit - Total Claims = Undisputed Balance
        """
        try:
            total_deposit = deposit_transaction.amount
            
            # Get all claims for this deposit
            claims = DepositClaim.query.filter_by(
                deposit_transaction_id=deposit_transaction.id
            ).all()
            
            total_claimed = sum(claim.claimed_amount for claim in claims)
            undisputed_balance = total_deposit - total_claimed
            
            logger.info(f"Deposit {deposit_transaction.id}: Total={total_deposit}, Claimed={total_claimed}, Undisputed={undisputed_balance}")
            
            return max(undisputed_balance, 0)  # Never negative
            
        except Exception as e:
            logger.error(f"Error calculating undisputed balance: {e}")
            return Decimal('0.00')
    
    @staticmethod
    def release_undisputed_balance(deposit_transaction):
        """
        Release the undisputed balance to tenant immediately when claims are submitted.
        This is the fair approach - only hold disputed amounts in escrow.
        """
        try:
            undisputed_amount = FundReleaseService.calculate_undisputed_balance(deposit_transaction)
            
            if undisputed_amount <= 0:
                logger.info(f"No undisputed balance to release for deposit {deposit_transaction.id}")
                return {'success': True, 'amount': 0, 'message': 'No undisputed balance'}
            
            # Check if already released
            if deposit_transaction.refunded_amount >= undisputed_amount:
                logger.info(f"Undisputed balance already released for deposit {deposit_transaction.id}")
                return {'success': True, 'amount': 0, 'message': 'Already released'}
            
            # Process the refund to tenant
            refund_result = FundReleaseService._process_tenant_refund(
                deposit_transaction, 
                undisputed_amount,
                "Automatic release of undisputed deposit balance"
            )
            
            if refund_result['success']:
                # Update deposit transaction
                deposit_transaction.refunded_amount = undisputed_amount
                deposit_transaction.refunded_at = datetime.utcnow()
                deposit_transaction.updated_at = datetime.utcnow()
                
                # Update status if partially released
                if undisputed_amount < deposit_transaction.amount:
                    deposit_transaction.status = DepositTransactionStatus.PARTIALLY_RELEASED
                else:
                    deposit_transaction.status = DepositTransactionStatus.REFUNDED
                
                db.session.commit()
                
                logger.info(f"Released £{undisputed_amount} undisputed balance to tenant for deposit {deposit_transaction.id}")
                
                return {
                    'success': True, 
                    'amount': float(undisputed_amount),
                    'message': f'Released £{undisputed_amount} to tenant'
                }
            else:
                return refund_result
                
        except Exception as e:
            logger.error(f"Error releasing undisputed balance: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def release_accepted_claim(deposit_transaction, claim):
        """
        Release funds to landlord immediately when tenant accepts a claim.
        """
        try:
            # Determine the amount to release
            if claim.status == DepositClaimStatus.ACCEPTED:
                release_amount = claim.claimed_amount
            elif claim.status == DepositClaimStatus.RESOLVED and hasattr(claim, 'approved_amount'):
                release_amount = claim.approved_amount or claim.claimed_amount
            else:
                logger.warning(f"Claim {claim.id} not in releasable state: {claim.status}")
                return {'success': False, 'error': 'Claim not in releasable state'}
            
            # Process payment to landlord
            payment_result = FundReleaseService._process_landlord_payment(
                deposit_transaction,
                release_amount,
                f"Deposit claim payment: {claim.title}"
            )
            
            if payment_result['success']:
                # Update deposit transaction
                deposit_transaction.released_amount = (deposit_transaction.released_amount or 0) + release_amount
                deposit_transaction.released_at = datetime.utcnow()
                deposit_transaction.updated_at = datetime.utcnow()
                
                # Update status
                total_processed = (deposit_transaction.released_amount or 0) + (deposit_transaction.refunded_amount or 0)
                if total_processed >= deposit_transaction.amount:
                    deposit_transaction.status = DepositTransactionStatus.RELEASED
                else:
                    deposit_transaction.status = DepositTransactionStatus.PARTIALLY_RELEASED
                
                db.session.commit()
                
                logger.info(f"Released £{release_amount} to landlord for accepted claim {claim.id}")
                
                return {
                    'success': True,
                    'amount': float(release_amount),
                    'message': f'Released £{release_amount} to landlord'
                }
            else:
                return payment_result
                
        except Exception as e:
            logger.error(f"Error releasing accepted claim: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _process_tenant_refund(deposit_transaction, amount, description):
        """
        Process refund to tenant using Stripe or payment system.
        """
        try:
            # For now, simulate the refund process
            # In production, this would integrate with Stripe refunds
            logger.info(f"Processing £{amount} refund to tenant {deposit_transaction.tenant_id}: {description}")
            
            # TODO: Integrate with actual payment processing
            # stripe_result = stripe_service.create_refund(
            #     payment_intent_id=deposit_transaction.payment_intent_id,
            #     amount=int(amount * 100),  # Convert to cents
            #     reason='requested_by_customer'
            # )
            
            # For now, return success (in production, check stripe_result)
            return {
                'success': True,
                'transaction_id': f"refund_{deposit_transaction.id}_{int(datetime.utcnow().timestamp())}",
                'amount': float(amount)
            }
            
        except Exception as e:
            logger.error(f"Error processing tenant refund: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _process_landlord_payment(deposit_transaction, amount, description):
        """
        Process payment to landlord using Stripe or payment system.
        """
        try:
            # For now, simulate the payment process
            # In production, this would integrate with Stripe transfers
            logger.info(f"Processing £{amount} payment to landlord {deposit_transaction.landlord_id}: {description}")
            
            # TODO: Integrate with actual payment processing
            # stripe_result = stripe_service.create_transfer(
            #     destination_account=landlord_stripe_account,
            #     amount=int(amount * 100),  # Convert to cents
            #     currency='gbp'
            # )
            
            # For now, return success (in production, check stripe_result)
            return {
                'success': True,
                'transaction_id': f"payment_{deposit_transaction.id}_{int(datetime.utcnow().timestamp())}",
                'amount': float(amount)
            }
            
        except Exception as e:
            logger.error(f"Error processing landlord payment: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_deposit_breakdown(deposit_transaction):
        """
        Get a complete breakdown of deposit amounts for display.
        """
        try:
            claims = DepositClaim.query.filter_by(
                deposit_transaction_id=deposit_transaction.id
            ).all()
            
            total_deposit = float(deposit_transaction.amount)
            total_claimed = sum(float(claim.claimed_amount) for claim in claims)
            
            # If no claims have been submitted yet, entire deposit should be held in escrow
            if not claims:
                return {
                    'total_deposit': total_deposit,
                    'total_claimed': 0,
                    'undisputed_balance': 0,
                    'accepted_amount': 0,
                    'resolved_amount': 0,
                    'disputed_amount': 0,
                    'mediation_amount': 0,
                    'released_to_landlord': 0,
                    'refunded_to_tenant': 0,
                    'remaining_in_escrow': total_deposit,  # All held in escrow until claims are submitted
                    'claims': [],
                    'status': 'awaiting_claims'  # Indicate we're waiting for landlord to submit claims
                }
            
            # Calculate amounts by status
            accepted_amount = sum(
                float(claim.claimed_amount) for claim in claims 
                if claim.status == DepositClaimStatus.ACCEPTED
            )
            
            resolved_amount = sum(
                float(claim.approved_amount or claim.claimed_amount) for claim in claims 
                if claim.status == DepositClaimStatus.RESOLVED
            )
            
            disputed_amount = sum(
                float(claim.claimed_amount) for claim in claims 
                if claim.status == DepositClaimStatus.DISPUTED
            )
            
            mediation_amount = sum(
                float(claim.claimed_amount) for claim in claims 
                if claim.status == DepositClaimStatus.UNDER_REVIEW
            )
            
            # IMPORTANT: Pending claims should also be held in escrow until tenant responds
            pending_amount = sum(
                float(claim.claimed_amount) for claim in claims 
                if claim.status in [DepositClaimStatus.SUBMITTED, DepositClaimStatus.TENANT_NOTIFIED]
            )
            
            # Calculate claim reductions (difference between claimed and approved amounts)
            claim_reductions = sum(
                float(claim.claimed_amount) - float(claim.approved_amount or claim.claimed_amount)
                for claim in claims 
                if claim.status == DepositClaimStatus.RESOLVED and claim.approved_amount is not None
            )
            
            # Calculate released amounts based on actual claim statuses
            # Released to landlord = accepted claims + resolved claims (using approved amounts)
            released_to_landlord = accepted_amount + resolved_amount
            
            # Calculate what should be held in escrow = disputed + mediation + pending claims
            total_in_escrow = disputed_amount + mediation_amount + pending_amount
            
            # Refunded to tenant = only the truly undisputed amount (after all claims are resolved)
            # If there are pending claims, don't refund anything yet - wait for tenant response
            if pending_amount > 0:
                # If there are pending claims, don't refund undisputed balance yet
                refunded_to_tenant = 0
                remaining_in_escrow = total_in_escrow + (total_deposit - total_claimed)  # Include undisputed balance in escrow
            else:
                # Only refund undisputed balance if no pending claims
                refunded_to_tenant = (total_deposit - total_claimed) + claim_reductions
                remaining_in_escrow = total_in_escrow
            
            return {
                'total_deposit': total_deposit,
                'total_claimed': total_claimed,
                'undisputed_balance': total_deposit - total_claimed,
                'accepted_amount': accepted_amount,
                'resolved_amount': resolved_amount,
                'disputed_amount': disputed_amount,
                'mediation_amount': mediation_amount,
                'pending_amount': pending_amount,  # Add pending amount to breakdown
                'released_to_landlord': released_to_landlord,
                'refunded_to_tenant': refunded_to_tenant,
                'remaining_in_escrow': max(remaining_in_escrow, 0),
                'claims': [claim.to_dict() for claim in claims],
                'status': 'claims_submitted'
            }
            
        except Exception as e:
            logger.error(f"Error getting deposit breakdown: {e}")
            return None

# Create service instance
fund_release_service = FundReleaseService()

