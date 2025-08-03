"""
Automated Expiry Service for Tenancy Agreements

This service handles the automatic expiration of tenancy agreements
that have not been completed within the specified time limit.
"""

from datetime import datetime, timedelta
from ..models.tenancy_agreement import TenancyAgreement
from ..models import db
import logging

logger = logging.getLogger(__name__)


class ExpiryService:
    """Service for handling automatic expiry of tenancy agreements"""
    
    @staticmethod
    def check_and_expire_agreements():
        """
        Check all agreements and expire those that have passed their expiry time
        Returns the number of agreements that were expired
        """
        try:
            now = datetime.utcnow()
            
            # Find agreements that should be expired
            expired_agreements = TenancyAgreement.query.filter(
                TenancyAgreement.expires_at <= now,
                TenancyAgreement.status.in_(['pending_signatures', 'pending_payment']),
                TenancyAgreement.cancelled_at.is_(None),
                TenancyAgreement.landlord_withdrawn_at.is_(None),
                TenancyAgreement.tenant_withdrawn_at.is_(None)
            ).all()
            
            expired_count = 0
            
            for agreement in expired_agreements:
                try:
                    # Update agreement status to expired
                    agreement.status = 'expired'
                    agreement.cancelled_at = now
                    agreement.cancellation_reason = 'Agreement expired - not completed within time limit'
                    
                    db.session.add(agreement)
                    expired_count += 1
                    
                    logger.info(f"Expired agreement {agreement.id} - was in status '{agreement.status}' and expired at {agreement.expires_at}")
                    
                except Exception as e:
                    logger.error(f"Error expiring agreement {agreement.id}: {str(e)}")
                    continue
            
            if expired_count > 0:
                db.session.commit()
                logger.info(f"Successfully expired {expired_count} agreements")
            else:
                logger.debug("No agreements to expire")
            
            return expired_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in check_and_expire_agreements: {str(e)}")
            return 0
    
    @staticmethod
    def get_expiring_soon_agreements(hours_ahead=24):
        """
        Get agreements that will expire within the specified number of hours
        
        Args:
            hours_ahead (int): Number of hours to look ahead (default: 24)
            
        Returns:
            List of agreements that will expire soon
        """
        try:
            now = datetime.utcnow()
            future_time = now + timedelta(hours=hours_ahead)
            
            expiring_agreements = TenancyAgreement.query.filter(
                TenancyAgreement.expires_at.between(now, future_time),
                TenancyAgreement.status.in_(['pending_signatures', 'pending_payment']),
                TenancyAgreement.cancelled_at.is_(None),
                TenancyAgreement.landlord_withdrawn_at.is_(None),
                TenancyAgreement.tenant_withdrawn_at.is_(None)
            ).all()
            
            return expiring_agreements
            
        except Exception as e:
            logger.error(f"Error getting expiring agreements: {str(e)}")
            return []
    
    @staticmethod
    def get_expiry_statistics():
        """
        Get statistics about agreement expiry
        
        Returns:
            Dictionary with expiry statistics
        """
        try:
            now = datetime.utcnow()
            
            # Count agreements by status
            total_agreements = TenancyAgreement.query.count()
            
            expired_agreements = TenancyAgreement.query.filter(
                TenancyAgreement.status == 'expired'
            ).count()
            
            expiring_today = TenancyAgreement.query.filter(
                TenancyAgreement.expires_at <= now + timedelta(hours=24),
                TenancyAgreement.expires_at > now,
                TenancyAgreement.status.in_(['pending_signatures', 'pending_payment'])
            ).count()
            
            pending_agreements = TenancyAgreement.query.filter(
                TenancyAgreement.status.in_(['pending_signatures', 'pending_payment']),
                TenancyAgreement.expires_at > now
            ).count()
            
            return {
                'total_agreements': total_agreements,
                'expired_agreements': expired_agreements,
                'expiring_today': expiring_today,
                'pending_agreements': pending_agreements,
                'last_check': now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting expiry statistics: {str(e)}")
            return {
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def cleanup_old_expired_agreements(days_old=30):
        """
        Clean up expired agreements that are older than specified days
        This is for maintenance purposes to keep the database clean
        
        Args:
            days_old (int): Number of days after which to clean up expired agreements
            
        Returns:
            Number of agreements cleaned up
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            old_expired_agreements = TenancyAgreement.query.filter(
                TenancyAgreement.status == 'expired',
                TenancyAgreement.cancelled_at <= cutoff_date
            ).all()
            
            cleanup_count = 0
            
            for agreement in old_expired_agreements:
                try:
                    # Instead of deleting, we could archive or mark for cleanup
                    # For now, we'll just log them
                    logger.info(f"Old expired agreement found: {agreement.id} (expired on {agreement.cancelled_at})")
                    cleanup_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing old expired agreement {agreement.id}: {str(e)}")
                    continue
            
            logger.info(f"Found {cleanup_count} old expired agreements (older than {days_old} days)")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error in cleanup_old_expired_agreements: {str(e)}")
            return 0


# Create a global instance
expiry_service = ExpiryService()

