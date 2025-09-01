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
from datetime import datetime
from .deposit_deadline_service import DepositDeadlineService
from ..models.user import db

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

