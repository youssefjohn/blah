"""
Minimal Property Lifecycle Service (without deposit functionality)

This is a temporary version to allow application startup without deposit model conflicts.
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
    """
    Minimal property lifecycle service without deposit functionality
    """
    
    @staticmethod
    def check_lease_expiry_advance_notifications():
        """
        Send 7-day advance notifications for expiring leases
        """
        try:
            logger.info("🔔 Checking for lease expiry advance notifications...")
            
            # Find agreements expiring in 7 days
            seven_days_from_now = datetime.utcnow() + timedelta(days=7)
            
            expiring_agreements = TenancyAgreement.query.filter(
                and_(
                    TenancyAgreement.end_date <= seven_days_from_now.date(),
                    TenancyAgreement.end_date > datetime.utcnow().date(),
                    TenancyAgreement.status == 'active',
                    TenancyAgreement.expiry_notification_sent == False
                )
            ).all()
            
            notifications_sent = 0
            
            for agreement in expiring_agreements:
                try:
                    # Create notifications for both tenant and landlord
                    tenant_notification = Notification(
                        recipient_id=agreement.tenant_id,
                        message=f"Your tenancy at {agreement.property.address} expires in 7 days on {agreement.end_date.strftime('%B %d, %Y')}",
                        notification_type='LEASE_EXPIRY_ADVANCE',
                        priority='HIGH'
                    )
                    
                    landlord_notification = Notification(
                        recipient_id=agreement.property.owner_id,
                        message=f"Tenancy agreement for {agreement.property.address} expires in 7 days on {agreement.end_date.strftime('%B %d, %Y')}",
                        notification_type='LEASE_EXPIRY_ADVANCE',
                        priority='HIGH'
                    )
                    
                    db.session.add(tenant_notification)
                    db.session.add(landlord_notification)
                    
                    # Mark as notified
                    agreement.expiry_notification_sent = True
                    notifications_sent += 2
                    
                except Exception as e:
                    logger.error(f"Error creating notifications for agreement {agreement.id}: {str(e)}")
                    continue
            
            db.session.commit()
            
            logger.info(f"✅ Sent {notifications_sent} lease expiry advance notifications")
            return {
                "success": True,
                "notifications_sent": notifications_sent,
                "agreements_processed": len(expiring_agreements)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in lease expiry advance notifications: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def check_expired_agreements():
        """
        Process expired tenancy agreements
        """
        try:
            logger.info("🏠 Checking for expired tenancy agreements...")
            
            # Find agreements that expired yesterday or earlier
            yesterday = datetime.utcnow().date() - timedelta(days=1)
            
            expired_agreements = TenancyAgreement.query.filter(
                and_(
                    TenancyAgreement.end_date <= yesterday,
                    TenancyAgreement.status == 'active'
                )
            ).all()
            
            properties_updated = 0
            notifications_created = 0
            
            for agreement in expired_agreements:
                try:
                    # Update agreement status
                    agreement.status = 'expired'
                    agreement.updated_at = datetime.utcnow()
                    
                    # Update property status to inactive (will be reactivated after deposit resolution)
                    property_obj = agreement.property
                    if property_obj:
                        property_obj.status = PropertyStatus.INACTIVE
                        property_obj.updated_at = datetime.utcnow()
                        properties_updated += 1
                        
                        # Create notification
                        notification = Notification(
                            recipient_id=property_obj.owner_id,
                            message=f"Tenancy agreement for {property_obj.address} has expired. Property status updated to inactive.",
                            notification_type='LEASE_EXPIRED',
                            priority='NORMAL'
                        )
                        db.session.add(notification)
                        notifications_created += 1
                    
                except Exception as e:
                    logger.error(f"Error processing expired agreement {agreement.id}: {str(e)}")
                    continue
            
            db.session.commit()
            
            logger.info(f"✅ Processed {len(expired_agreements)} expired agreements")
            return {
                "success": True,
                "properties_updated": properties_updated,
                "notifications_created": notifications_created,
                "agreements_processed": len(expired_agreements)
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing expired agreements: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def run_daily_maintenance():
        """
        Run basic daily maintenance tasks (without deposit functionality)
        """
        logger.info("🚀 Starting minimal daily property lifecycle maintenance...")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "lease_expiry_advance": None,
            "expired_agreements": None,
            "total_properties_updated": 0,
            "total_notifications_created": 0
        }
        
        try:
            # 1. Send 7-day advance lease expiry notifications
            advance_result = PropertyLifecycleService.check_lease_expiry_advance_notifications()
            results["lease_expiry_advance"] = advance_result
            
            if advance_result["success"]:
                results["total_notifications_created"] += advance_result.get("notifications_sent", 0)
            
            # 2. Check expired agreements
            expired_result = PropertyLifecycleService.check_expired_agreements()
            results["expired_agreements"] = expired_result
            
            if expired_result["success"]:
                results["total_properties_updated"] += expired_result.get("properties_updated", 0)
                results["total_notifications_created"] += expired_result.get("notifications_created", 0)
            
            logger.info("🎉 Minimal daily property lifecycle maintenance completed successfully!")
            logger.info(f"   - Total properties updated: {results['total_properties_updated']}")
            logger.info(f"   - Total notifications created: {results['total_notifications_created']}")
            
            results["success"] = True
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in daily maintenance: {str(e)}")
            results["success"] = False
            results["error"] = str(e)
            return results

