"""
Property Lifecycle Service

Handles automated property status transitions and background jobs for the property lifecycle system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_
from flask import current_app
from src.models.user import db, User
from src.models.property import Property, PropertyStatus
from src.models.tenancy_agreement import TenancyAgreement
from src.models.notification import Notification
# Now that deposit models are working, restore these imports
from src.models.deposit_transaction import DepositTransaction
from src.models.deposit_claim import DepositClaim
from src.models.deposit_dispute import DepositDispute
from src.services.deposit_notification_service import DepositNotificationService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyLifecycleService:
    """Service for managing automated property lifecycle transitions"""
    
    @staticmethod
    def check_expired_agreements():
        """
        Check for expired tenancy agreements and start deposit resolution process
        This should be run daily as a background job
        """
        logger.info("🔄 Starting expired agreements check with deposit resolution...")
        
        try:
            # Find all agreements that have expired (lease_end_date < today)
            today = date.today()
            expired_agreements = TenancyAgreement.query.filter(
                and_(
                    TenancyAgreement.lease_end_date < today,
                    TenancyAgreement.status.in_(['active', 'signed'])  # Only active agreements
                )
            ).all()
            
            properties_updated = 0
            notifications_created = 0
            deposit_resolutions_started = 0
            
            for agreement in expired_agreements:
                try:
                    # Get the associated property
                    property_obj = Property.query.get(agreement.property_id)
                    
                    if property_obj and property_obj.status == PropertyStatus.RENTED:
                        # Check if there's a deposit transaction for this agreement
                        deposit_transaction = DepositTransaction.query.filter_by(
                            tenancy_agreement_id=agreement.id
                        ).first()
                        
                        if deposit_transaction:
                            # Start deposit resolution process
                            property_obj.status = PropertyStatus.INACTIVE  # Will be reactivated after deposit resolution
                            agreement.status = 'expired'
                            
                            # Create notification for landlord about deposit claim window
                            landlord_notification = Notification(
                                recipient_id=property_obj.owner_id,
                                message=f"Your tenancy for '{property_obj.title}' has ended. You have 7 days to submit any deposit claims, or the full deposit will be refunded to the tenant.",
                                notification_type='LEASE_EXPIRY_ADVANCE',
                                priority='HIGH',
                                action_required=True,
                                action_deadline=datetime.utcnow() + timedelta(days=7),
                                action_url=f"/deposit/claim/create/{deposit_transaction.id}",
                                deposit_transaction_id=deposit_transaction.id,
                                tenancy_agreement_id=agreement.id,
                                property_id=property_obj.id
                            )
                            
                            # Create notification for tenant about deposit resolution
                            tenant_notification = Notification(
                                recipient_id=agreement.tenant_id,
                                message=f"Your lease for '{property_obj.title}' has ended. Deposit resolution process has begun. You will be notified of any claims or refund within 7 days.",
                                notification_type='LEASE_EXPIRY_ADVANCE',
                                priority='NORMAL',
                                action_url=f"/deposit/status/{deposit_transaction.id}",
                                deposit_transaction_id=deposit_transaction.id,
                                tenancy_agreement_id=agreement.id,
                                property_id=property_obj.id
                            )
                            
                            db.session.add(landlord_notification)
                            db.session.add(tenant_notification)
                            deposit_resolutions_started += 1
                            notifications_created += 2
                            
                            logger.info(f"✅ Started deposit resolution for property {property_obj.id} ({property_obj.title})")
                        else:
                            # No deposit - proceed with normal expiry process
                            property_obj.status = PropertyStatus.INACTIVE
                            agreement.status = 'expired'
                            
                            # Create standard notification for landlord
                            notification = Notification(
                                recipient_id=property_obj.owner_id,
                                message=f"Your tenancy for '{property_obj.title}' has ended. Please review and re-activate your listing when you're ready to find new tenants."
                            )
                            
                            db.session.add(notification)
                            notifications_created += 1
                            
                            logger.info(f"✅ Set property {property_obj.id} ({property_obj.title}) to Inactive status - no deposit to resolve")
                        
                        properties_updated += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing expired agreement {agreement.id}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"🎉 Expired agreements check completed:")
            logger.info(f"   - Properties updated: {properties_updated}")
            logger.info(f"   - Deposit resolutions started: {deposit_resolutions_started}")
            logger.info(f"   - Notifications created: {notifications_created}")
            
            return {
                "success": True,
                "properties_updated": properties_updated,
                "deposit_resolutions_started": deposit_resolutions_started,
                "notifications_created": notifications_created
            }
            
        except Exception as e:
            logger.error(f"❌ Error in expired agreements check: {str(e)}")
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def check_lease_expiry_advance_notifications():
        """
        Send 7-day advance notifications for upcoming lease expiries
        """
        logger.info("🔄 Checking for upcoming lease expiries (7-day advance)...")
        
        try:
            # Find agreements expiring in exactly 7 days
            target_date = date.today() + timedelta(days=7)
            
            upcoming_expiries = TenancyAgreement.query.filter(
                and_(
                    TenancyAgreement.lease_end_date == target_date,
                    TenancyAgreement.status.in_(['active', 'signed'])
                )
            ).all()
            
            notifications_sent = 0
            
            for agreement in upcoming_expiries:
                try:
                    # Check if we've already sent the 7-day notice
                    existing_notification = Notification.query.filter(
                        and_(
                            Notification.tenancy_agreement_id == agreement.id,
                            Notification.notification_type == 'LEASE_EXPIRY_ADVANCE',
                            Notification.created_at >= datetime.utcnow() - timedelta(days=1)  # Sent within last day
                        )
                    ).first()
                    
                    if not existing_notification:
                        # Send 7-day advance notifications
                        DepositNotificationService.notify_lease_expiry_advance(agreement)
                        notifications_sent += 2  # Tenant + landlord
                        
                        logger.info(f"✅ Sent 7-day advance notifications for agreement {agreement.id}")
                    
                except Exception as e:
                    logger.error(f"❌ Error sending advance notification for agreement {agreement.id}: {str(e)}")
                    continue
            
            logger.info(f"🎉 Lease expiry advance notifications completed:")
            logger.info(f"   - Notifications sent: {notifications_sent}")
            
            return {
                "success": True,
                "notifications_sent": notifications_sent
            }
            
        except Exception as e:
            logger.error(f"❌ Error in lease expiry advance notifications: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def check_deposit_claim_deadlines():
        """
        Check for deposit claims approaching deadline and auto-approve expired ones
        """
        logger.info("🔄 Checking deposit claim deadlines...")
        
        try:
            # Find claims that can be auto-approved (deadline passed)
            auto_approved = 0
            deadline_reminders = 0
            
            # Auto-approve overdue claims
            overdue_claims = DepositClaim.query.filter(
                and_(
                    DepositClaim.status.in_(['submitted', 'tenant_notified']),
                    DepositClaim.auto_approve_at < datetime.utcnow()
                )
            ).all()
            
            for claim in overdue_claims:
                try:
                    if claim.auto_approve_claim():
                        # Notify both parties about auto-approval
                        DepositNotificationService.notify_deposit_claim_submitted(claim)  # Will show as resolved
                        auto_approved += 1
                        
                        logger.info(f"✅ Auto-approved deposit claim {claim.id} due to no tenant response")
                    
                except Exception as e:
                    logger.error(f"❌ Error auto-approving claim {claim.id}: {str(e)}")
                    continue
            
            # Send deadline reminders for claims expiring within 24 hours
            upcoming_deadline = datetime.utcnow() + timedelta(hours=24)
            
            approaching_claims = DepositClaim.query.filter(
                and_(
                    DepositClaim.status.in_(['submitted', 'tenant_notified']),
                    DepositClaim.tenant_response_deadline <= upcoming_deadline,
                    DepositClaim.tenant_response_deadline > datetime.utcnow()
                )
            ).all()
            
            for claim in approaching_claims:
                try:
                    # Check if we've sent a reminder in the last 6 hours
                    recent_reminder = Notification.query.filter(
                        and_(
                            Notification.deposit_claim_id == claim.id,
                            Notification.notification_type == 'DEPOSIT_CLAIM_RESPONSE_DEADLINE',
                            Notification.created_at >= datetime.utcnow() - timedelta(hours=6)
                        )
                    ).first()
                    
                    if not recent_reminder:
                        DepositNotificationService.notify_deposit_claim_response_deadline(claim)
                        deadline_reminders += 1
                        
                        logger.info(f"✅ Sent deadline reminder for claim {claim.id}")
                    
                except Exception as e:
                    logger.error(f"❌ Error sending deadline reminder for claim {claim.id}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"🎉 Deposit claim deadlines check completed:")
            logger.info(f"   - Claims auto-approved: {auto_approved}")
            logger.info(f"   - Deadline reminders sent: {deadline_reminders}")
            
            return {
                "success": True,
                "claims_auto_approved": auto_approved,
                "deadline_reminders_sent": deadline_reminders
            }
            
        except Exception as e:
            logger.error(f"❌ Error in deposit claim deadlines check: {str(e)}")
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def check_deposit_dispute_deadlines():
        """
        Check for deposit disputes approaching mediation deadline and auto-escalate expired ones
        """
        logger.info("🔄 Checking deposit dispute deadlines...")
        
        try:
            escalated_disputes = 0
            mediation_reminders = 0
            
            # Auto-escalate disputes past mediation deadline
            overdue_disputes = DepositDispute.query.filter(
                and_(
                    DepositDispute.status == 'under_mediation',
                    DepositDispute.escalation_deadline < datetime.utcnow()
                )
            ).all()
            
            for dispute in overdue_disputes:
                try:
                    dispute.escalate_dispute("Mediation deadline exceeded - escalated to admin review")
                    escalated_disputes += 1
                    
                    logger.info(f"✅ Auto-escalated dispute {dispute.id} due to mediation timeout")
                    
                except Exception as e:
                    logger.error(f"❌ Error auto-escalating dispute {dispute.id}: {str(e)}")
                    continue
            
            # Send mediation deadline reminders
            upcoming_deadline = datetime.utcnow() + timedelta(hours=48)  # 48 hours before deadline
            
            approaching_disputes = DepositDispute.query.filter(
                and_(
                    DepositDispute.status == 'under_mediation',
                    DepositDispute.mediation_deadline <= upcoming_deadline,
                    DepositDispute.mediation_deadline > datetime.utcnow()
                )
            ).all()
            
            for dispute in approaching_disputes:
                try:
                    # Check if we've sent a reminder in the last 12 hours
                    recent_reminder = Notification.query.filter(
                        and_(
                            Notification.deposit_dispute_id == dispute.id,
                            Notification.notification_type == 'DEPOSIT_MEDIATION_DEADLINE',
                            Notification.created_at >= datetime.utcnow() - timedelta(hours=12)
                        )
                    ).first()
                    
                    if not recent_reminder:
                        # Send mediation deadline reminders to both parties
                        hours_remaining = dispute.hours_until_mediation_deadline
                        
                        message = (f"Mediation deadline approaching: {hours_remaining:.0f} hours remaining "
                                  f"to resolve dispute for {dispute.deposit_claim.title}")
                        
                        # Notify tenant
                        tenant_notification = Notification(
                            recipient_id=dispute.tenant_id,
                            message=message,
                            notification_type='DEPOSIT_MEDIATION_DEADLINE',
                            priority='URGENT',
                            action_required=True,
                            action_deadline=dispute.mediation_deadline,
                            action_url=f"/deposit/dispute/{dispute.id}",
                            deposit_dispute_id=dispute.id,
                            deposit_claim_id=dispute.deposit_claim_id,
                            deposit_transaction_id=dispute.deposit_transaction_id,
                            property_id=dispute.property_id
                        )
                        
                        # Notify landlord
                        landlord_notification = Notification(
                            recipient_id=dispute.landlord_id,
                            message=message,
                            notification_type='DEPOSIT_MEDIATION_DEADLINE',
                            priority='URGENT',
                            action_required=True,
                            action_deadline=dispute.mediation_deadline,
                            action_url=f"/deposit/dispute/{dispute.id}",
                            deposit_dispute_id=dispute.id,
                            deposit_claim_id=dispute.deposit_claim_id,
                            deposit_transaction_id=dispute.deposit_transaction_id,
                            property_id=dispute.property_id
                        )
                        
                        db.session.add(tenant_notification)
                        db.session.add(landlord_notification)
                        mediation_reminders += 2
                        
                        logger.info(f"✅ Sent mediation deadline reminders for dispute {dispute.id}")
                    
                except Exception as e:
                    logger.error(f"❌ Error sending mediation reminder for dispute {dispute.id}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"🎉 Deposit dispute deadlines check completed:")
            logger.info(f"   - Disputes auto-escalated: {escalated_disputes}")
            logger.info(f"   - Mediation reminders sent: {mediation_reminders}")
            
            return {
                "success": True,
                "disputes_escalated": escalated_disputes,
                "mediation_reminders_sent": mediation_reminders
            }
            
        except Exception as e:
            logger.error(f"❌ Error in deposit dispute deadlines check: {str(e)}")
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def check_deposit_resolution_completion():
        """
        Check for completed deposit resolutions and reactivate properties
        """
        logger.info("🔄 Checking for completed deposit resolutions...")
        
        try:
            properties_reactivated = 0
            
            # Find deposit transactions that are fully resolved but properties are still inactive
            resolved_transactions = db.session.query(DepositTransaction).join(
                Property, DepositTransaction.property_id == Property.id
            ).filter(
                and_(
                    DepositTransaction.is_fully_resolved == True,
                    Property.status == PropertyStatus.INACTIVE,
                    DepositTransaction.resolved_at.isnot(None)
                )
            ).all()
            
            for transaction in resolved_transactions:
                try:
                    property_obj = transaction.property
                    
                    # Check if there are any pending claims or disputes
                    pending_claims = DepositClaim.query.filter(
                        and_(
                            DepositClaim.deposit_transaction_id == transaction.id,
                            DepositClaim.is_resolved == False
                        )
                    ).count()
                    
                    pending_disputes = DepositDispute.query.filter(
                        and_(
                            DepositDispute.deposit_transaction_id == transaction.id,
                            DepositDispute.is_resolved == False
                        )
                    ).count()
                    
                    if pending_claims == 0 and pending_disputes == 0:
                        # All deposit matters resolved - reactivate property
                        property_obj.status = PropertyStatus.ACTIVE
                        property_obj.available_from_date = None  # Available immediately
                        
                        # Create notification for landlord
                        notification = Notification(
                            recipient_id=property_obj.owner_id,
                            message=f"Deposit resolution completed for '{property_obj.title}'. Your property is now active and ready for new tenants.",
                            notification_type='PROPERTY',
                            priority='NORMAL',
                            action_url=f"/property/{property_obj.id}",
                            property_id=property_obj.id,
                            deposit_transaction_id=transaction.id
                        )
                        
                        db.session.add(notification)
                        properties_reactivated += 1
                        
                        logger.info(f"✅ Reactivated property {property_obj.id} ({property_obj.title}) - deposit resolution completed")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing resolved transaction {transaction.id}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"🎉 Deposit resolution completion check completed:")
            logger.info(f"   - Properties reactivated: {properties_reactivated}")
            
            return {
                "success": True,
                "properties_reactivated": properties_reactivated
            }
            
        except Exception as e:
            logger.error(f"❌ Error in deposit resolution completion check: {str(e)}")
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def check_pending_agreements_timeout():
        """
        Check for pending agreements that have been inactive for too long
        and revert properties to Active status
        """
        logger.info("🔄 Starting pending agreements timeout check...")
        
        try:
            # Find agreements that have been pending for more than 30 days
            timeout_date = datetime.utcnow() - timedelta(days=30)
            
            stale_agreements = TenancyAgreement.query.filter(
                and_(
                    TenancyAgreement.status == 'pending_signatures',
                    TenancyAgreement.created_at < timeout_date
                )
            ).all()
            
            properties_reverted = 0
            notifications_created = 0
            
            for agreement in stale_agreements:
                try:
                    # Get the associated property
                    property_obj = Property.query.get(agreement.property_id)
                    
                    if property_obj and property_obj.status == PropertyStatus.PENDING:
                        # Revert property status to Active
                        property_obj.status = PropertyStatus.ACTIVE
                        
                        # Mark agreement as expired
                        agreement.status = 'expired'
                        agreement.cancellation_reason = 'Timeout - No signatures received within 30 days'
                        
                        # Create notification for landlord
                        notification = Notification(
                            recipient_id=property_obj.owner_id,
                            message=f"Your property '{property_obj.title}' has been re-listed as the tenancy agreement was not signed within 30 days."
                        )
                        
                        db.session.add(notification)
                        properties_reverted += 1
                        notifications_created += 1
                        
                        logger.info(f"✅ Reverted property {property_obj.id} ({property_obj.title}) from Pending to Active due to timeout")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing stale agreement {agreement.id}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"🎉 Pending agreements timeout check completed:")
            logger.info(f"   - Properties reverted to Active: {properties_reverted}")
            logger.info(f"   - Notifications created: {notifications_created}")
            
            return {
                "success": True,
                "properties_set_to_inactive": properties_reverted,
                "notifications_created": notifications_created
            }
            
        except Exception as e:
            logger.error(f"❌ Error in pending agreements timeout check: {str(e)}")
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def check_future_availability():
        """
        Check for properties with future availability dates that have arrived
        and make them publicly visible
        """
        logger.info("🔄 Starting future availability check...")
        
        try:
            today = date.today()
            
            # Find properties that are Active but have a future availability date that has arrived
            properties_to_activate = Property.query.filter(
                and_(
                    Property.status == PropertyStatus.ACTIVE,
                    Property.available_from_date <= today,
                    Property.available_from_date.isnot(None)
                )
            ).all()
            
            properties_activated = 0
            notifications_created = 0
            
            for property_obj in properties_to_activate:
                try:
                    # Clear the future availability date (property is now immediately available)
                    property_obj.available_from_date = None
                    
                    # Create notification for landlord
                    notification = Notification(
                        recipient_id=property_obj.owner_id,
                        message=f"Your property '{property_obj.title}' is now publicly visible and accepting applications."
                    )
                    
                    db.session.add(notification)
                    properties_activated += 1
                    notifications_created += 1
                    
                    logger.info(f"✅ Activated property {property_obj.id} ({property_obj.title}) - future availability date reached")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing future availability for property {property_obj.id}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"🎉 Future availability check completed:")
            logger.info(f"   - Properties activated: {properties_activated}")
            logger.info(f"   - Notifications created: {notifications_created}")
            
            return {
                "success": True,
                "properties_activated": properties_activated,
                "notifications_created": notifications_created
            }
            
        except Exception as e:
            logger.error(f"❌ Error in future availability check: {str(e)}")
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def run_daily_maintenance():
        """
        Run all daily maintenance tasks for the property lifecycle system including deposit workflows
        This is the main entry point for the daily background job
        """
        logger.info("🚀 Starting daily property lifecycle maintenance with deposit workflows...")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "lease_expiry_advance": None,
            "expired_agreements": None,
            "pending_timeouts": None,
            "future_availability": None,
            "deposit_claim_deadlines": None,
            "deposit_dispute_deadlines": None,
            "deposit_resolution_completion": None,
            "total_properties_updated": 0,
            "total_notifications_created": 0
        }
        
        try:
            # 1. Send 7-day advance lease expiry notifications
            advance_result = PropertyLifecycleService.check_lease_expiry_advance_notifications()
            results["lease_expiry_advance"] = advance_result
            
            if advance_result["success"]:
                results["total_notifications_created"] += advance_result.get("notifications_sent", 0)
            
            # 2. Check expired agreements and start deposit resolution
            expired_result = PropertyLifecycleService.check_expired_agreements()
            results["expired_agreements"] = expired_result
            
            if expired_result["success"]:
                results["total_properties_updated"] += expired_result.get("properties_updated", 0)
                results["total_notifications_created"] += expired_result["notifications_created"]
            
            # 3. Check pending agreement timeouts
            timeout_result = PropertyLifecycleService.check_pending_agreements_timeout()
            results["pending_timeouts"] = timeout_result
            
            if timeout_result["success"]:
                results["total_properties_updated"] += timeout_result.get("properties_reverted", 0)
                results["total_notifications_created"] += timeout_result["notifications_created"]
            
            # 4. Check future availability
            availability_result = PropertyLifecycleService.check_future_availability()
            results["future_availability"] = availability_result
            
            if availability_result["success"]:
                results["total_properties_updated"] += availability_result.get("properties_activated", 0)
                results["total_notifications_created"] += availability_result["notifications_created"]
            
            # 5. Check deposit claim deadlines
            claim_deadlines_result = PropertyLifecycleService.check_deposit_claim_deadlines()
            results["deposit_claim_deadlines"] = claim_deadlines_result
            
            if claim_deadlines_result["success"]:
                results["total_notifications_created"] += claim_deadlines_result.get("deadline_reminders_sent", 0)
            
            # 6. Check deposit dispute deadlines
            dispute_deadlines_result = PropertyLifecycleService.check_deposit_dispute_deadlines()
            results["deposit_dispute_deadlines"] = dispute_deadlines_result
            
            if dispute_deadlines_result["success"]:
                results["total_notifications_created"] += dispute_deadlines_result.get("mediation_reminders_sent", 0)
            
            # 7. Check for completed deposit resolutions and reactivate properties
            resolution_result = PropertyLifecycleService.check_deposit_resolution_completion()
            results["deposit_resolution_completion"] = resolution_result
            
            if resolution_result["success"]:
                results["total_properties_updated"] += resolution_result.get("properties_reactivated", 0)
            
            logger.info("🎉 Daily property lifecycle maintenance completed successfully!")
            logger.info(f"   - Total properties updated: {results['total_properties_updated']}")
            logger.info(f"   - Total notifications created: {results['total_notifications_created']}")
            
            results["success"] = True
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in daily maintenance: {str(e)}")
            results["success"] = False
            results["error"] = str(e)
            return results

    @staticmethod
    def create_status_change_notification(property_obj, old_status, new_status, reason="Manual change"):
        """
        Create a notification when property status changes
        """
        try:
            status_messages = {
                PropertyStatus.ACTIVE: "is now active and accepting applications",
                PropertyStatus.PENDING: "has a pending tenancy agreement",
                PropertyStatus.RENTED: "is now rented and occupied",
                PropertyStatus.INACTIVE: "has been deactivated"
            }
            
            message = f"Your property '{property_obj.title}' {status_messages.get(new_status, f'status changed to {new_status.value}')}"
            
            if reason != "Manual change":
                message += f" ({reason})"
            
            notification = Notification(
                recipient_id=property_obj.owner_id,
                message=message
            )
            
            db.session.add(notification)
            db.session.commit()
            
            logger.info(f"✅ Created status change notification for property {property_obj.id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating status change notification: {str(e)}")
            return False

