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
from src.models.user import db
from src.models.property import Property, PropertyStatus
from src.models.tenancy_agreement import TenancyAgreement
from src.models.notification import Notification
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyLifecycleService:
    """Service for managing automated property lifecycle transitions"""
    
    @staticmethod
    def check_expired_agreements():
        """
        Check for expired tenancy agreements and revert properties to Active status
        This should be run daily as a background job
        """
        logger.info("🔄 Starting expired agreements check...")
        
        try:
            # Find all agreements that have expired (lease_end_date < today)
            today = date.today()
            expired_agreements = TenancyAgreement.query.filter(
                and_(
                    TenancyAgreement.lease_end_date < today,
                    TenancyAgreement.status.in_(['active', 'signed'])  # Only active agreements
                )
            ).all()
            
            properties_reverted = 0
            notifications_created = 0
            
            for agreement in expired_agreements:
                try:
                    # Get the associated property
                    property_obj = Property.query.get(agreement.property_id)
                    
                    if property_obj and property_obj.status == PropertyStatus.RENTED:
                        # Set property status to Inactive (landlord must manually re-activate)
                        property_obj.status = PropertyStatus.INACTIVE
                        property_obj.available_from_date = None  # Clear any future availability date
                        
                        # Mark agreement as expired
                        agreement.status = 'expired'
                        
                        # Create notification for landlord
                        notification = Notification(
                            recipient_id=property_obj.owner_id,
                            message=f"Your tenancy for '{property_obj.title}' has ended. Please review and re-activate your listing when you're ready to find new tenants."
                        )
                        
                        db.session.add(notification)
                        properties_reverted += 1
                        notifications_created += 1
                        
                        logger.info(f"✅ Set property {property_obj.id} ({property_obj.title}) to Inactive status - landlord must manually re-activate")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing expired agreement {agreement.id}: {str(e)}")
                    continue
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"🎉 Expired agreements check completed:")
            logger.info(f"   - Properties set to Inactive: {properties_reverted}")
            logger.info(f"   - Notifications created: {notifications_created}")
            
            return {
                "success": True,
                "properties_set_to_inactive": properties_reverted,
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
        Run all daily maintenance tasks for the property lifecycle system
        This is the main entry point for the daily background job
        """
        logger.info("🚀 Starting daily property lifecycle maintenance...")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "expired_agreements": None,
            "pending_timeouts": None,
            "future_availability": None,
            "total_properties_updated": 0,
            "total_notifications_created": 0
        }
        
        try:
            # Check expired agreements
            expired_result = PropertyLifecycleService.check_expired_agreements()
            results["expired_agreements"] = expired_result
            
            if expired_result["success"]:
                results["total_properties_updated"] += expired_result.get("properties_set_to_inactive", 0)
                results["total_notifications_created"] += expired_result["notifications_created"]
            
            # Check pending agreement timeouts
            timeout_result = PropertyLifecycleService.check_pending_agreements_timeout()
            results["pending_timeouts"] = timeout_result
            
            if timeout_result["success"]:
                results["total_properties_updated"] += timeout_result.get("properties_reverted", 0)
                results["total_notifications_created"] += timeout_result["notifications_created"]
            
            # Check future availability
            availability_result = PropertyLifecycleService.check_future_availability()
            results["future_availability"] = availability_result
            
            if availability_result["success"]:
                results["total_properties_updated"] += availability_result.get("properties_activated", 0)
                results["total_notifications_created"] += availability_result["notifications_created"]
            
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

