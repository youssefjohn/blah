"""
Background Jobs Service

Handles scheduled background tasks for the application:
- Automatic deposit finalization after 7-day inspection period
- Cleanup tasks
- Notification processing
"""

import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from .deposit_deadline_service import DepositDeadlineService
from .stripe_connect_service import stripe_connect_service
from ..models.user import db, User
from ..models.deposit_transaction import DepositTransaction, DepositTransactionStatus
from ..models.tenancy_agreement import TenancyAgreement

logger = logging.getLogger(__name__)

class BackgroundJobsService:
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start_scheduler(self):
        """Start the background job scheduler"""
        if self.running:
            logger.warning("Background jobs already running")
            return
        
        logger.info("Starting background job scheduler...")
        
        # Schedule deposit expiry checks every hour
        schedule.every().hour.do(self._process_expired_deposits)
        
        # Schedule pending verification checks every 30 minutes
        schedule.every(30).minutes.do(self._process_pending_verification_deposits)
        
        # Schedule daily cleanup at 2 AM
        schedule.every().day.at("02:00").do(self._daily_cleanup)
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Background job scheduler started successfully")
    
    def stop_scheduler(self):
        """Stop the background job scheduler"""
        if not self.running:
            return
        
        logger.info("Stopping background job scheduler...")
        self.running = False
        schedule.clear()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logger.info("Background job scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in background job scheduler: {e}")
                time.sleep(60)  # Continue running even if there's an error
    
    def _process_expired_deposits(self):
        """Process deposits where 7-day inspection period has expired"""
        try:
            logger.info("Starting expired deposit processing...")
            
            # Use the existing method from DepositDeadlineService
            processed_count = DepositDeadlineService.check_and_process_expired_deposits()
            
            if processed_count > 0:
                logger.info(f"Successfully processed {processed_count} expired deposits")
            else:
                logger.debug("No expired deposits found to process")
                
        except Exception as e:
            logger.error(f"Error processing expired deposits: {e}")
    
    def _process_pending_verification_deposits(self):
        """Process deposits waiting for landlord verification"""
        try:
            logger.info("Checking for deposits pending landlord verification...")
            
            # Find deposits pending verification
            pending_deposits = DepositTransaction.query.filter_by(
                status=DepositTransactionStatus.PENDING_LANDLORD_VERIFICATION
            ).all()
            
            if not pending_deposits:
                logger.debug("No pending verification deposits found")
                return 0
            
            processed_count = 0
            expired_count = 0
            
            for deposit in pending_deposits:
                try:
                    # Check if landlord account is now verified
                    landlord = User.query.get(deposit.landlord_id)
                    if not landlord or not landlord.stripe_account_id:
                        continue
                    
                    # Check account status
                    account_status = stripe_connect_service.get_account_status(landlord.stripe_account_id)
                    
                    if account_status['success'] and account_status['charges_enabled']:
                        # Account is now ready! Process the transfer
                        success = self._transfer_pending_deposit_to_landlord(deposit)
                        if success:
                            processed_count += 1
                            logger.info(f"Successfully transferred pending deposit {deposit.id} to verified landlord account")
                    else:
                        # Check if deposit has been waiting too long (7 days)
                        days_waiting = (datetime.utcnow() - deposit.paid_at).days if deposit.paid_at else 0
                        
                        if days_waiting >= 3:
                            # Refund to tenant after 3 days
                            success = self._refund_expired_pending_deposit(deposit)
                            if success:
                                expired_count += 1
                                logger.info(f"Refunded expired pending deposit {deposit.id} after {days_waiting} days")
                
                except Exception as e:
                    logger.error(f"Error processing pending deposit {deposit.id}: {e}")
                    continue
            
            if processed_count > 0 or expired_count > 0:
                logger.info(f"Processed {processed_count} pending deposits, refunded {expired_count} expired deposits")
            
            return processed_count + expired_count
            
        except Exception as e:
            logger.error(f"Error processing pending verification deposits: {e}")
            return 0
    
    def _transfer_pending_deposit_to_landlord(self, deposit):
        """Transfer pending deposit to landlord's verified Connect account"""
        try:
            # Transfer funds from platform to landlord's Connect account
            transfer_result = stripe_connect_service.transfer_deposit_to_connect_account({
                'payment_intent_id': deposit.payment_intent_id,
                'landlord_account_id': deposit.landlord_stripe_account_id,
                'amount': float(deposit.amount),
                'deposit_id': deposit.id
            })
            
            if transfer_result['success']:
                # Update deposit status
                deposit.status = DepositTransactionStatus.HELD_IN_ESCROW
                deposit.payment_method = 'stripe_connect'
                deposit.escrow_status = 'held'
                deposit.escrow_held_at = datetime.utcnow()
                
                # Activate the tenancy agreement
                agreement = TenancyAgreement.query.get(deposit.tenancy_agreement_id)
                if agreement and agreement.status == 'deposit_paid_pending_verification':
                    agreement.status = 'active'
                    agreement.activated_at = datetime.utcnow()
                    
                    # Update property status
                    from ..models.property import Property
                    property = Property.query.get(agreement.property_id)
                    if property:
                        property.transition_to_rented()
                
                db.session.commit()
                
                # Send notifications to both parties
                from .deposit_notification_service import DepositNotificationService
                property_address = f"{property.title}, {property.location}" if property else 'Property'
                
                DepositNotificationService.notify_deposit_verified_and_transferred(
                    landlord_id=deposit.landlord_id,
                    tenant_id=deposit.tenant_id,
                    agreement_id=agreement.id,
                    property_address=property_address,
                    deposit_amount=float(deposit.amount)
                )
                
                return True
            else:
                logger.error(f"Failed to transfer deposit {deposit.id}: {transfer_result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error transferring pending deposit {deposit.id}: {e}")
            db.session.rollback()
            return False
    
    def _refund_expired_pending_deposit(self, deposit):
        """Refund deposit that has been pending verification too long"""
        try:
            # Refund to tenant
            refund_result = stripe_connect_service.refund_payment_intent({
                'payment_intent_id': deposit.payment_intent_id,
                'amount': float(deposit.amount),
                'reason': 'landlord_verification_expired',
                'deposit_id': deposit.id
            })
            
            if refund_result['success']:
                # Update deposit status
                deposit.status = DepositTransactionStatus.CANCELLED
                deposit.refunded_amount = deposit.amount
                deposit.refunded_at = datetime.utcnow()
                
                # Cancel the tenancy agreement
                agreement = TenancyAgreement.query.get(deposit.tenancy_agreement_id)
                if agreement:
                    agreement.status = 'cancelled_landlord_unverified'
                
                db.session.commit()
                
                # Send notifications to both parties
                from .deposit_notification_service import DepositNotificationService
                
                # Get tenant and landlord info
                tenant = User.query.get(deposit.tenant_id) 
                landlord = User.query.get(deposit.landlord_id)
                property_obj = Property.query.get(deposit.property_id)
                property_address = f"{property_obj.title}, {property_obj.location}" if property_obj else 'Property'
                
                # Notify tenant about successful refund
                DepositNotificationService.notify_tenant_deposit_refund_processed(
                    tenant_id=deposit.tenant_id,
                    agreement_id=deposit.tenancy_agreement_id,
                    landlord_name=landlord.get_full_name() if landlord else 'Landlord',
                    property_address=property_address,
                    deposit_amount=float(deposit.amount)
                )
                
                # TODO: Also notify landlord about missed opportunity
                
                logger.info(f"Refunded expired pending deposit {deposit.id} - landlord failed to verify within 3 days")
                return True
            else:
                logger.error(f"Failed to refund expired deposit {deposit.id}: {refund_result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error refunding expired deposit {deposit.id}: {e}")
            db.session.rollback()
            return False
    
    def _daily_cleanup(self):
        """Daily cleanup tasks"""
        try:
            logger.info("Starting daily cleanup tasks...")
            
            # Add any daily cleanup tasks here
            # For example: clean up old notifications, temporary files, etc.
            
            logger.info("Daily cleanup completed")
            
        except Exception as e:
            logger.error(f"Error in daily cleanup: {e}")
    
    def process_expired_deposits_now(self):
        """Manually trigger expired deposit processing (for testing/admin)"""
        logger.info("Manually triggering expired deposit processing...")
        return self._process_expired_deposits()

# Global instance
background_jobs_service = BackgroundJobsService()

def start_background_jobs():
    """Start background jobs - call this from main app"""
    background_jobs_service.start_scheduler()

def stop_background_jobs():
    """Stop background jobs - call this on app shutdown"""
    background_jobs_service.stop_scheduler()

