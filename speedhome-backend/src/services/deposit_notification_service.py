"""
Deposit Notification Service
Handles all deposit-related notifications with multi-channel delivery
"""

from datetime import datetime, timedelta
from ..models.user import db
from ..models.notification import Notification, NotificationType, NotificationPriority
from ..models.deposit_transaction import DepositTransaction
from ..models.deposit_claim import DepositClaim
from ..models.deposit_dispute import DepositDispute

class DepositNotificationService:
    """Service for managing deposit-related notifications"""
    
    @staticmethod
    def create_notification(
        recipient_id,
        message,
        notification_type,
        priority=NotificationPriority.NORMAL,
        action_required=False,
        action_deadline=None,
        action_url=None,
        **entity_refs
    ):
        """Create a new deposit notification"""
        
        notification = Notification(
            recipient_id=recipient_id,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_required=action_required,
            action_deadline=action_deadline,
            action_url=action_url,
            **entity_refs
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    # Deposit Payment Notifications
    @staticmethod
    def notify_deposit_payment_required(deposit_transaction):
        """Notify tenant that deposit payment is required"""
        
        message = (f"Deposit payment required: MYR {deposit_transaction.amount:,.2f} "
                  f"({deposit_transaction.calculation_multiplier} months rent) for "
                  f"{deposit_transaction.property.address}")
        
        return DepositNotificationService.create_notification(
            recipient_id=deposit_transaction.tenant_id,
            message=message,
            notification_type=NotificationType.DEPOSIT_PAYMENT_REQUIRED,
            priority=NotificationPriority.HIGH,
            action_required=True,
            action_deadline=datetime.utcnow() + timedelta(days=7),  # 7 days to pay
            action_url=f"/deposit/payment/{deposit_transaction.id}",
            deposit_transaction_id=deposit_transaction.id,
            tenancy_agreement_id=deposit_transaction.tenancy_agreement_id,
            property_id=deposit_transaction.property_id
        )
    
    @staticmethod
    def notify_deposit_payment_confirmed(deposit_transaction):
        """Notify tenant and landlord that deposit payment is confirmed"""
        
        # Notify tenant
        tenant_message = (f"Deposit payment confirmed: MYR {deposit_transaction.amount:,.2f} "
                         f"for {deposit_transaction.property.address}. "
                         f"Your deposit is now held securely in escrow.")
        
        tenant_notification = DepositNotificationService.create_notification(
            recipient_id=deposit_transaction.tenant_id,
            message=tenant_message,
            notification_type=NotificationType.DEPOSIT_PAYMENT_CONFIRMED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/deposit/status/{deposit_transaction.id}",
            deposit_transaction_id=deposit_transaction.id,
            tenancy_agreement_id=deposit_transaction.tenancy_agreement_id,
            property_id=deposit_transaction.property_id
        )
        
        # Notify landlord
        landlord_message = (f"Tenant deposit received: MYR {deposit_transaction.amount:,.2f} "
                           f"for {deposit_transaction.property.address}. "
                           f"Deposit is held securely in escrow.")
        
        landlord_notification = DepositNotificationService.create_notification(
            recipient_id=deposit_transaction.landlord_id,
            message=landlord_message,
            notification_type=NotificationType.DEPOSIT_PAYMENT_CONFIRMED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/deposit/status/{deposit_transaction.id}",
            deposit_transaction_id=deposit_transaction.id,
            tenancy_agreement_id=deposit_transaction.tenancy_agreement_id,
            property_id=deposit_transaction.property_id
        )
        
        return [tenant_notification, landlord_notification]
    
    # Lease Expiry Notifications
    @staticmethod
    def notify_lease_expiry_advance(tenancy_agreement):
        """Notify landlord and tenant 7 days before lease expiry"""
        
        # Notify tenant
        tenant_message = (f"Your lease for {tenancy_agreement.property.address} "
                         f"expires in 7 days ({tenancy_agreement.lease_end_date.strftime('%d %b %Y')}). "
                         f"Deposit resolution process will begin after lease end.")
        
        tenant_notification = DepositNotificationService.create_notification(
            recipient_id=tenancy_agreement.tenant_id,
            message=tenant_message,
            notification_type=NotificationType.LEASE_EXPIRY_ADVANCE,
            priority=NotificationPriority.HIGH,
            action_url=f"/tenancy/{tenancy_agreement.id}",
            tenancy_agreement_id=tenancy_agreement.id,
            property_id=tenancy_agreement.property_id
        )
        
        # Notify landlord
        landlord_message = (f"Tenant lease expires in 7 days ({tenancy_agreement.lease_end_date.strftime('%d %b %Y')}) "
                           f"for {tenancy_agreement.property.address}. "
                           f"You can submit deposit claims after lease end.")
        
        landlord_notification = DepositNotificationService.create_notification(
            recipient_id=tenancy_agreement.landlord_id,
            message=landlord_message,
            notification_type=NotificationType.LEASE_EXPIRY_ADVANCE,
            priority=NotificationPriority.HIGH,
            action_url=f"/tenancy/{tenancy_agreement.id}",
            tenancy_agreement_id=tenancy_agreement.id,
            property_id=tenancy_agreement.property_id
        )
        
        return [tenant_notification, landlord_notification]
    
    # Deposit Claim Notifications
    @staticmethod
    def notify_deposit_claim_submitted(deposit_claim):
        """Notify tenant that landlord has submitted a deposit claim"""
        
        message = (f"Deposit claim submitted: {deposit_claim.title} - "
                  f"MYR {deposit_claim.claimed_amount:,.2f} for "
                  f"{deposit_claim.property.address}. "
                  f"You have 7 days to respond.")
        
        return DepositNotificationService.create_notification(
            recipient_id=deposit_claim.tenant_id,
            message=message,
            notification_type=NotificationType.DEPOSIT_CLAIM_SUBMITTED,
            priority=NotificationPriority.URGENT,
            action_required=True,
            action_deadline=deposit_claim.tenant_response_deadline,
            action_url=f"/deposit/claim/{deposit_claim.id}",
            deposit_claim_id=deposit_claim.id,
            deposit_transaction_id=deposit_claim.deposit_transaction_id,
            tenancy_agreement_id=deposit_claim.tenancy_agreement_id,
            property_id=deposit_claim.property_id
        )

