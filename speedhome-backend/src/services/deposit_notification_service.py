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
    def notify_landlord_verification_required(
        landlord_id,
        agreement_id, 
        tenant_name,
        property_address,
        deposit_amount,
        deadline_days=3
    ):
        """Notify landlord that they need to complete account verification to receive deposit"""
        
        deadline = datetime.utcnow() + timedelta(days=deadline_days)
        
        message = (
            f"Action Required: Complete Payment Account Setup\n\n"
            f"A tenant ({tenant_name}) has paid a deposit of RM{deposit_amount:.2f} "
            f"for your property at {property_address}. To receive these funds, you must "
            f"complete your Stripe Connect account verification.\n\n"
            f"Please complete verification by {deadline.strftime('%B %d, %Y')} (3 days) or "
            f"the deposit will be automatically refunded to the tenant.\n\n"
            f"Click 'Complete Setup' to verify your account now."
        )
        
        return DepositNotificationService.create_notification(
            recipient_id=landlord_id,
            message=message,
            notification_type=NotificationType.DEPOSIT_PAYMENT,
            priority=NotificationPriority.HIGH,
            action_required=True,
            action_deadline=deadline,
            action_url="/landlord/stripe/complete-setup",
            entity_type="tenancy_agreement",
            entity_id=agreement_id,
            tenancy_agreement_id=agreement_id
        )
    
    @staticmethod
    def notify_landlord_verification_reminder(
        landlord_id,
        agreement_id,
        tenant_name,
        property_address,
        deposit_amount,
        days_remaining
    ):
        """Send reminder notification to landlord about pending verification"""
        
        urgency = "urgent - only" if days_remaining <= 2 else ""
        
        message = (
            f"Reminder: Payment Account Setup Required\n\n"
            f"This is an {urgency} reminder that you have {days_remaining} day(s) "
            f"remaining to complete your payment account verification.\n\n"
            f"Tenant: {tenant_name}\n"
            f"Property: {property_address}\n"
            f"Deposit Amount: RM{deposit_amount:.2f}\n\n"
            f"If not completed, the deposit will be refunded to the tenant.\n\n"
            f"Complete your setup now to receive the funds."
        )
        
        return DepositNotificationService.create_notification(
            recipient_id=landlord_id,
            message=message,
            notification_type=NotificationType.DEPOSIT_PAYMENT,
            priority=NotificationPriority.HIGH if days_remaining <= 2 else NotificationPriority.NORMAL,
            action_required=True,
            action_url="/landlord/stripe/complete-setup",
            entity_type="tenancy_agreement",
            entity_id=agreement_id,
            tenancy_agreement_id=agreement_id
        )
    
    @staticmethod
    def notify_deposit_verified_and_transferred(
        landlord_id,
        tenant_id,
        agreement_id,
        property_address,
        deposit_amount
    ):
        """Notify both parties when deposit verification is complete and funds transferred"""
        
        landlord_message = (
            f"Deposit Funds Transferred\n\n"
            f"Your payment account has been verified and the deposit of RM{deposit_amount:.2f} "
            f"for your property at {property_address} has been transferred to your account.\n\n"
            f"The tenancy agreement is now fully active."
        )
        
        tenant_message = (
            f"Deposit Processed - Tenancy Activated\n\n"
            f"Your deposit of RM{deposit_amount:.2f} for the property at {property_address} "
            f"has been successfully processed. Your tenancy agreement is now fully active.\n\n"
            f"The landlord's payment account has been verified and funds are being held in escrow."
        )
        
        # Notify landlord
        landlord_notification = DepositNotificationService.create_notification(
            recipient_id=landlord_id,
            message=landlord_message,
            notification_type=NotificationType.DEPOSIT_PAYMENT,
            priority=NotificationPriority.NORMAL,
            entity_type="tenancy_agreement",
            entity_id=agreement_id,
            tenancy_agreement_id=agreement_id
        )
        
        # Notify tenant
        tenant_notification = DepositNotificationService.create_notification(
            recipient_id=tenant_id,
            message=tenant_message,
            notification_type=NotificationType.DEPOSIT_PAYMENT,
            priority=NotificationPriority.NORMAL,
            entity_type="tenancy_agreement",
            entity_id=agreement_id,
            tenancy_agreement_id=agreement_id
        )
        
        return {
            'landlord_notification': landlord_notification,
            'tenant_notification': tenant_notification
        }
    
    @staticmethod
    def notify_tenant_deposit_protection(
        tenant_id,
        agreement_id,
        landlord_name,
        property_address,
        deposit_amount
    ):
        """Notify tenant about 3-day auto-refund protection guarantee"""
        
        message = (
            f"Deposit Protected - 3-Day Guarantee\n\n"
            f"Your deposit of RM{deposit_amount:.2f} for {property_address} has been paid successfully.\n\n"
            f"🛡️ PROTECTION GUARANTEE:\n"
            f"If the landlord ({landlord_name}) doesn't complete their payment account "
            f"verification within 3 days, your deposit will be AUTOMATICALLY REFUNDED.\n\n"
            f"You don't need to do anything - our system will protect you automatically.\n\n"
            f"We've notified the landlord to complete their setup immediately."
        )
        
        return DepositNotificationService.create_notification(
            recipient_id=tenant_id,
            message=message,
            notification_type=NotificationType.DEPOSIT_PAYMENT,
            priority=NotificationPriority.HIGH,
            action_required=False,
            entity_type="tenancy_agreement", 
            entity_id=agreement_id,
            tenancy_agreement_id=agreement_id
        )
    
    @staticmethod
    def notify_tenant_deposit_refund_processed(
        tenant_id,
        agreement_id,
        landlord_name,
        property_address,
        deposit_amount
    ):
        """Notify tenant when their deposit has been auto-refunded due to landlord timeout"""
        
        message = (
            f"Deposit Auto-Refunded - Landlord Failed to Verify\n\n"
            f"Your deposit of RM{deposit_amount:.2f} for {property_address} has been "
            f"automatically refunded because the landlord ({landlord_name}) failed to "
            f"complete their payment account verification within 3 days.\n\n"
            f"💸 Refund Status: Processed\n"
            f"⏰ Processing Time: 3-5 business days\n"
            f"💳 Refund Method: Original payment method\n\n"
            f"The tenancy agreement has been cancelled. You can continue searching "
            f"for other properties on our platform."
        )
        
        return DepositNotificationService.create_notification(
            recipient_id=tenant_id,
            message=message,
            notification_type=NotificationType.DEPOSIT_PAYMENT,
            priority=NotificationPriority.HIGH,
            action_required=False,
            entity_type="tenancy_agreement",
            entity_id=agreement_id,
            tenancy_agreement_id=agreement_id
        )

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
            notification_type=NotificationType.DEPOSIT_RELEASED,
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
            notification_type=NotificationType.DEPOSIT_RELEASED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/deposit/status/{deposit_transaction_id}",
            entity_type="deposit_transaction",
            entity_id=deposit_transaction_id,
            tenancy_agreement_id=tenancy_agreement_id,
            property_id=property_id
        )
        
        return [tenant_notification, landlord_notification]

