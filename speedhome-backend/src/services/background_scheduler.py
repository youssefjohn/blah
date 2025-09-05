"""
Background Job Scheduler

Handles scheduling and execution of background jobs for the property lifecycle system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import schedule
import time
import threading
from datetime import datetime, timedelta
# Use full property lifecycle service now that deposit models are working
from src.services.property_lifecycle_service import PropertyLifecycleService
from src.models.user import db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundScheduler:
    """Background job scheduler for property lifecycle tasks"""
    
    def __init__(self, app=None):
        self.app = app
        self.running = False
        self.scheduler_thread = None
        
    def init_app(self, app):
        """Initialize the scheduler with Flask app context"""
        self.app = app
        
    def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("⚠️ Scheduler is already running")
            return
            
        logger.info("🚀 Starting background job scheduler...")
        

        
        # Schedule hourly checks for immediate needs (optional)
        schedule.every(10).minutes.do(self._run_hourly_checks)
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("✅ Background scheduler started successfully")
        
    def stop(self):
        """Stop the background scheduler"""
        if not self.running:
            logger.warning("⚠️ Scheduler is not running")
            return
            
        logger.info("🛑 Stopping background job scheduler...")
        self.running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        schedule.clear()
        logger.info("✅ Background scheduler stopped")
        
    def _run_scheduler(self):
        """Main scheduler loop"""
        logger.info("🔄 Scheduler loop started")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {str(e)}")
                time.sleep(60)  # Continue running even if there's an error
                
        logger.info("🔄 Scheduler loop stopped")
        
    def _run_daily_maintenance(self):
        """Run daily maintenance tasks with Flask app context"""
        if not self.app:
            logger.error("❌ No Flask app context available for daily maintenance")
            return
            
        with self.app.app_context():
            logger.info("🌅 Running daily property lifecycle maintenance...")
            
            try:
                results = PropertyLifecycleService.run_daily_maintenance()
                
                if results["success"]:
                    logger.info("✅ Daily maintenance completed successfully")
                    logger.info(f"   - Properties updated: {results['total_properties_updated']}")
                    logger.info(f"   - Notifications created: {results['total_notifications_created']}")
                else:
                    logger.error(f"❌ Daily maintenance failed: {results.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ Exception during daily maintenance: {str(e)}")
                
    def _run_hourly_checks(self):
        """Run hourly checks for time-sensitive tasks including deposit deadlines"""
        if not self.app:
            logger.error("❌ No Flask app context available for hourly checks")
            return
            
        with self.app.app_context():
            logger.info("⏰ Running hourly property lifecycle and deposit checks...")
            
            try:
                # Check for expired agreements (moved from daily to hourly)
                expiry_result = PropertyLifecycleService.check_expired_agreements()

                # Check future availability (existing functionality)
                availability_result = PropertyLifecycleService.check_future_availability()
                
                if availability_result["success"] and availability_result["properties_activated"] > 0:
                    logger.info(f"✅ Hourly check: {availability_result['properties_activated']} properties activated")
                
                # Check deposit claim deadlines (new functionality)
                claim_result = PropertyLifecycleService.check_deposit_claim_deadlines()
                
                if claim_result["success"]:
                    if claim_result.get("claims_auto_approved", 0) > 0:
                        logger.info(f"✅ Hourly check: {claim_result['claims_auto_approved']} claims auto-approved")
                    if claim_result.get("deadline_reminders_sent", 0) > 0:
                        logger.info(f"✅ Hourly check: {claim_result['deadline_reminders_sent']} deadline reminders sent")
                
                # Check deposit dispute deadlines (new functionality)
                dispute_result = PropertyLifecycleService.check_deposit_dispute_deadlines()
                
                if dispute_result["success"]:
                    if dispute_result.get("disputes_escalated", 0) > 0:
                        logger.info(f"✅ Hourly check: {dispute_result['disputes_escalated']} disputes escalated")
                    if dispute_result.get("mediation_reminders_sent", 0) > 0:
                        logger.info(f"✅ Hourly check: {dispute_result['mediation_reminders_sent']} mediation reminders sent")
                    
            except Exception as e:
                logger.error(f"❌ Exception during hourly checks: {str(e)}")
                
    def run_maintenance_now(self):
        """Run maintenance tasks immediately (for testing/manual execution)"""
        if not self.app:
            logger.error("❌ No Flask app context available")
            return None
            
        with self.app.app_context():
            logger.info("🔧 Running maintenance tasks manually...")
            return PropertyLifecycleService.run_daily_maintenance()

# Global scheduler instance
scheduler = BackgroundScheduler()

def init_scheduler(app):
    """Initialize the background scheduler with the Flask app"""
    scheduler.init_app(app)
    return scheduler

def start_scheduler():
    """Start the background scheduler"""
    scheduler.start()

def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.stop()

# Standalone script execution
if __name__ == "__main__":
    """
    Run the scheduler as a standalone script
    Usage: python background_scheduler.py
    """
    
    # Create a minimal Flask app for database context
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Initialize and start scheduler
    scheduler = BackgroundScheduler(app)
    
    try:
        logger.info("🚀 Starting standalone background scheduler...")
        scheduler.start()
        
        # Keep the script running
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("⌨️ Keyboard interrupt received")
        scheduler.stop()
        logger.info("👋 Scheduler stopped gracefully")
        
    except Exception as e:
        logger.error(f"❌ Fatal error in standalone scheduler: {str(e)}")
        scheduler.stop()

