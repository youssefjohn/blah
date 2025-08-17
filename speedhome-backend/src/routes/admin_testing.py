from flask import Blueprint, jsonify, request, session
from src.models.user import db, User
from src.models.property import Property, PropertyStatus
from src.models.tenancy_agreement import TenancyAgreement
from src.models.application import Application
from src.services.property_lifecycle_service import PropertyLifecycleService
from datetime import datetime, date, timedelta
import logging

admin_testing_bp = Blueprint('admin_testing_bp', __name__, url_prefix='/api/admin')

logger = logging.getLogger(__name__)

@admin_testing_bp.route('/trigger-expired-check', methods=['POST'])
def trigger_expired_check():
    """
    Manual trigger for expired agreements check
    Useful for testing the property lifecycle system
    """
    try:
        logger.info("🧪 Manual trigger: Starting expired agreements check...")
        result = PropertyLifecycleService.check_expired_agreements()
        
        logger.info(f"🧪 Manual trigger completed: {result}")
        return jsonify({
            "success": True,
            "message": "Expired agreements check completed",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@admin_testing_bp.route('/trigger-pending-timeout', methods=['POST'])
def trigger_pending_timeout():
    """
    Manual trigger for pending agreements timeout check
    """
    try:
        logger.info("🧪 Manual trigger: Starting pending timeout check...")
        result = PropertyLifecycleService.check_pending_agreements_timeout()
        
        logger.info(f"🧪 Manual trigger completed: {result}")
        return jsonify({
            "success": True,
            "message": "Pending timeout check completed",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@admin_testing_bp.route('/trigger-future-availability', methods=['POST'])
def trigger_future_availability():
    """
    Manual trigger for future availability check
    """
    try:
        logger.info("🧪 Manual trigger: Starting future availability check...")
        result = PropertyLifecycleService.check_future_availability()
        
        logger.info(f"🧪 Manual trigger completed: {result}")
        return jsonify({
            "success": True,
            "message": "Future availability check completed",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@admin_testing_bp.route('/trigger-daily-maintenance', methods=['POST'])
def trigger_daily_maintenance():
    """
    Manual trigger for complete daily maintenance
    """
    try:
        logger.info("🧪 Manual trigger: Starting daily maintenance...")
        result = PropertyLifecycleService.run_daily_maintenance()
        
        logger.info(f"🧪 Manual trigger completed: {result}")
        return jsonify({
            "success": True,
            "message": "Daily maintenance completed",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@admin_testing_bp.route('/create-test-expired-tenancy', methods=['POST'])
def create_test_expired_tenancy():
    """
    Helper endpoint to create a test tenancy that's already expired
    Useful for testing the lifecycle system
    """
    try:
        data = request.get_json() or {}
        property_id = data.get('property_id')
        
        if not property_id:
            return jsonify({
                "success": False,
                "error": "property_id is required"
            }), 400
            
        # Get the property
        property_obj = Property.query.get(property_id)
        if not property_obj:
            return jsonify({
                "success": False,
                "error": "Property not found"
            }), 404
            
        # Get a tenant user (first tenant in the system)
        tenant = User.query.filter_by(role='tenant').first()
        if not tenant:
            return jsonify({
                "success": False,
                "error": "No tenant found in system"
            }), 404
            
        # Create an application first
        application = Application(
            tenant_id=tenant.id,
            property_id=property_id,
            status='approved',
            full_name=tenant.first_name + ' ' + tenant.last_name,
            email=tenant.email,
            phone='0123456789',
            nationality='Malaysian',
            occupation='Test Occupation',
            gross_monthly_income=5000,
            number_of_occupants=1,
            preferred_move_in_date=date.today() - timedelta(days=30),
            lease_duration_preference='1-year',
            pets=False,
            smoking=False,
            message='Test application for expired tenancy'
        )
        
        db.session.add(application)
        db.session.flush()  # Get the application ID
        
        # Create an expired tenancy agreement
        expired_date = date.today() - timedelta(days=1)  # Yesterday
        
        tenancy_agreement = TenancyAgreement(
            application_id=application.id,
            landlord_id=property_obj.owner_id,
            tenant_id=tenant.id,
            property_id=property_id,
            lease_start_date=date.today() - timedelta(days=365),  # Started 1 year ago
            lease_end_date=expired_date,  # Ended yesterday
            lease_duration_months=12,
            monthly_rent=property_obj.price,
            security_deposit=property_obj.price * 2,
            agreement_fee=399,
            status='active',  # Still active but expired
            landlord_signed=True,
            tenant_signed=True,
            landlord_signed_at=datetime.now() - timedelta(days=365),
            tenant_signed_at=datetime.now() - timedelta(days=365),
            payment_completed=True,
            payment_completed_at=datetime.now() - timedelta(days=365)
        )
        
        db.session.add(tenancy_agreement)
        
        # Set property to Rented status
        property_obj.status = PropertyStatus.RENTED
        
        db.session.commit()
        
        logger.info(f"🧪 Created test expired tenancy for property {property_id}")
        
        return jsonify({
            "success": True,
            "message": "Test expired tenancy created successfully",
            "data": {
                "property_id": property_id,
                "property_status": property_obj.status.value,
                "tenancy_agreement_id": tenancy_agreement.id,
                "lease_end_date": expired_date.isoformat(),
                "tenant_name": tenant.first_name + ' ' + tenant.last_name
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Failed to create test expired tenancy: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@admin_testing_bp.route('/property-status/<int:property_id>', methods=['GET'])
def get_property_status_info(property_id):
    """
    Get detailed property status information for testing
    """
    try:
        property_obj = Property.query.get(property_id)
        if not property_obj:
            return jsonify({
                "success": False,
                "error": "Property not found"
            }), 404
            
        # Get related tenancy agreements
        agreements = TenancyAgreement.query.filter_by(property_id=property_id).all()
        
        return jsonify({
            "success": True,
            "data": {
                "property_id": property_id,
                "title": property_obj.title,
                "status": property_obj.status.value,
                "available_from_date": property_obj.available_from_date.isoformat() if property_obj.available_from_date else None,
                "owner_id": property_obj.owner_id,
                "tenancy_agreements": [
                    {
                        "id": agreement.id,
                        "status": agreement.status,
                        "lease_start_date": agreement.lease_start_date.isoformat() if agreement.lease_start_date else None,
                        "lease_end_date": agreement.lease_end_date.isoformat() if agreement.lease_end_date else None,
                        "tenant_id": agreement.tenant_id
                    }
                    for agreement in agreements
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get property status info: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

