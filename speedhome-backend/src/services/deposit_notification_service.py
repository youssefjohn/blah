"""
Deposit Notification Service
Handles all deposit-related notifications with multi-channel delivery
Uses flexible entity references - no foreign key dependencies
"""

from datetime import datetime, timedelta
from src.models.user import db
from src.models.notification import Notification, NotificationType, NotificationPriority

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
        entity_type=None,
        entity_id=None,
        tenancy_agreement_id=None,
        property_id=None
    ):
        """Create a new deposit notification with flexible entity reference"""
        
        notification = Notification(
            recipient_id=recipient_id,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_required=action_required,
            action_deadline=action_deadline,
            action_url=action_url,
            entity_type=entity_type,
            entity_id=entity_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    # Deposit Payment Notifications
    @staticmethod
    def notify_deposit_payment_required(deposit_transaction_id, tenant_id, amount, property_address, tenancy_agreement_id, property_id):
        """Notify tenant that deposit payment is required"""
        
        message = f"Deposit payment required: MYR {amount:,.2f} for {property_address}"
        
        return DepositNotificationService.create_notification(
            recipient_id=tenant_id,
            message=message,
            notification_type=NotificationType.DEPOSIT_PAYMENT_REQUIRED,
            priority=NotificationPriority.HIGH,
            action_required=True,
            action_deadline=datetime.utcnow() + timedelta(days=7),
            action_url=f"/deposit/payment/{deposit_transaction_id}",
            entity_type="deposit_transaction",
            entity_id=deposit_transaction_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
    
    @staticmethod
    def notify_deposit_payment_confirmed(deposit_transaction_id, tenant_id, landlord_id, amount, property_address, tenancy_agreement_id, property_id):
        """Notify tenant and landlord that deposit payment is confirmed"""
        
        # Notify tenant
        tenant_message = f"Deposit payment confirmed: MYR {amount:,.2f} for {property_address}. Your deposit is now held securely in escrow."
        
        tenant_notification = DepositNotificationService.create_notification(
            recipient_id=tenant_id,
            message=tenant_message,
            notification_type=NotificationType.DEPOSIT_PAYMENT_CONFIRMED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/deposit/status/{deposit_transaction_id}",
            entity_type="deposit_transaction",
            entity_id=deposit_transaction_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
        
        # Notify landlord
        landlord_message = f"Tenant deposit received: MYR {amount:,.2f} for {property_address}. Deposit is held securely in escrow."
        
        landlord_notification = DepositNotificationService.create_notification(
            recipient_id=landlord_id,
            message=landlord_message,
            notification_type=NotificationType.DEPOSIT_PAYMENT_CONFIRMED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/deposit/status/{deposit_transaction_id}",
            entity_type="deposit_transaction",
            entity_id=deposit_transaction_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
        
        return [tenant_notification, landlord_notification]
    
    # Lease Expiry Notifications
    @staticmethod
    def notify_lease_expiry_advance(tenancy_agreement_id, tenant_id, landlord_id, property_address, lease_end_date, property_id):
        """Notify landlord and tenant 7 days before lease expiry"""
        
        # Notify tenant
        tenant_message = f"Your lease for {property_address} expires in 7 days ({lease_end_date.strftime('%d %b %Y')}). Deposit resolution process will begin after lease end."
        
        tenant_notification = DepositNotificationService.create_notification(
            recipient_id=tenant_id,
            message=tenant_message,
            notification_type=NotificationType.LEASE_EXPIRY_ADVANCE,
            priority=NotificationPriority.HIGH,
            action_url=f"/tenancy/{tenancy_agreement_id}",
            entity_type="tenancy_agreement",
            entity_id=tenancy_agreement_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
        
        # Notify landlord
        landlord_message = f"Tenant lease expires in 7 days ({lease_end_date.strftime('%d %b %Y')}) for {property_address}. You can submit deposit claims after lease end."
        
        landlord_notification = DepositNotificationService.create_notification(
            recipient_id=landlord_id,
            message=landlord_message,
            notification_type=NotificationType.LEASE_EXPIRY_ADVANCE,
            priority=NotificationPriority.HIGH,
            action_url=f"/tenancy/{tenancy_agreement_id}",
            entity_type="tenancy_agreement",
            entity_id=tenancy_agreement_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
        
        return [tenant_notification, landlord_notification]
    
    # Deposit Claim Notifications
    @staticmethod
    def notify_deposit_claim_submitted(deposit_claim_id, tenant_id, claim_title, claimed_amount, property_address, response_deadline, tenancy_agreement_id, property_id):
        """Notify tenant that landlord has submitted a deposit claim"""
        
        message = f"Deposit claim submitted: {claim_title} - MYR {claimed_amount:,.2f} for {property_address}. You have 7 days to respond."
        
        return DepositNotificationService.create_notification(
            recipient_id=tenant_id,
            message=message,
            notification_type=NotificationType.DEPOSIT_CLAIM_SUBMITTED,
            priority=NotificationPriority.URGENT,
            action_required=True,
            action_deadline=response_deadline,
            action_url=f"/deposit/claim/{deposit_claim_id}",
            entity_type="deposit_claim",
            entity_id=deposit_claim_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
    
    @staticmethod
    def notify_deposit_resolved(deposit_transaction_id, tenant_id, landlord_id, tenant_refund, landlord_payout, property_address, tenancy_agreement_id, property_id):
        """Notify both parties of final deposit resolution"""
        
        # Notify tenant
        if tenant_refund > 0:
            tenant_message = f"Deposit resolved: MYR {tenant_refund:,.2f} refunded to you for {property_address}. Funds will be transferred within 3-5 business days."
        else:
            tenant_message = f"Deposit resolved: No refund due for {property_address} based on final resolution."
        
        tenant_notification = DepositNotificationService.create_notification(
            recipient_id=tenant_id,
            message=tenant_message,
            notification_type=NotificationType.DEPOSIT_RESOLVED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/deposit/status/{deposit_transaction_id}",
            entity_type="deposit_transaction",
            entity_id=deposit_transaction_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
        
        # Notify landlord
        if landlord_payout > 0:
            landlord_message = f"Deposit resolved: MYR {landlord_payout:,.2f} released to you for {property_address}. Funds will be transferred within 3-5 business days."
        else:
            landlord_message = f"Deposit resolved: Full refund to tenant for {property_address} based on final resolution."
        
        landlord_notification = DepositNotificationService.create_notification(
            recipient_id=landlord_id,
            message=landlord_message,
            notification_type=NotificationType.DEPOSIT_RESOLVED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/deposit/status/{deposit_transaction_id}",
            entity_type="deposit_transaction",
            entity_id=deposit_transaction_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
        
        return [tenant_notification, landlord_notification]

