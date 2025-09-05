"""
Admin Deposit Routes

Admin endpoints for deposit management and testing:
- Manual deposit processing triggers
- Deposit system status checks
- Background job controls
"""

from flask import Blueprint, jsonify, request
from ..services.background_jobs import background_jobs_service
from ..services.deposit_deadline_service import DepositDeadlineService
from ..models.deposit_transaction import DepositTransaction, DepositTransactionStatus
import logging

logger = logging.getLogger(__name__)

admin_deposit_bp = Blueprint('admin_deposit', __name__, url_prefix='/api/admin/deposits')

@admin_deposit_bp.route('/process-expired', methods=['POST'])
def process_expired_deposits():
    """Manually trigger processing of expired deposits"""
    try:
        processed_count = DepositDeadlineService.check_and_process_expired_deposits()
        
        return jsonify({
            'success': True,
            'processed_count': processed_count,
            'message': f'Successfully processed {processed_count} expired deposits'
        })
        
    except Exception as e:
        logger.error(f"Error processing expired deposits: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_deposit_bp.route('/status', methods=['GET'])
def get_deposit_system_status():
    """Get status of deposit system and background jobs"""
    try:
        # Count deposits by status
        held_count = DepositTransaction.query.filter_by(
            status=DepositTransactionStatus.HELD_IN_ESCROW
        ).count()
        
        disputed_count = DepositTransaction.query.filter_by(
            status=DepositTransactionStatus.DISPUTED
        ).count()
        
        resolved_count = DepositTransaction.query.filter_by(
            status=DepositTransactionStatus.RESOLVED
        ).count()
        
        refunded_count = DepositTransaction.query.filter_by(
            status=DepositTransactionStatus.REFUNDED
        ).count()
        
        return jsonify({
            'success': True,
            'deposit_counts': {
                'held_in_escrow': held_count,
                'disputed': disputed_count,
                'resolved': resolved_count,
                'refunded': refunded_count
            },
            'background_jobs': {
                'running': background_jobs_service.running,
                'thread_alive': background_jobs_service.thread.is_alive() if background_jobs_service.thread else False
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting deposit system status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_deposit_bp.route('/background-jobs/restart', methods=['POST'])
def restart_background_jobs():
    """Restart background job scheduler"""
    try:
        background_jobs_service.stop_scheduler()
        background_jobs_service.start_scheduler()
        
        return jsonify({
            'success': True,
            'message': 'Background jobs restarted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error restarting background jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

