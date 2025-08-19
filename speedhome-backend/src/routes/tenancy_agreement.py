from flask import Blueprint, request, jsonify, send_file, session
from flask_login import login_required, current_user

from ..services.stripe_service import stripe_service
from ..models.tenancy_agreement import TenancyAgreement
from src.services.pdf_service import pdf_service
from ..models.application import Application
from ..models.property import Property, PropertyStatus
from ..models.user import User
from ..models import db
from ..services.pdf_service import pdf_service
from ..services.workflow_coordinator import workflow_coordinator
from ..services.deposit_service import DepositService
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

# Create blueprint
tenancy_agreement_bp = Blueprint('tenancy_agreement', __name__, url_prefix='/api/tenancy-agreements')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tenancy_agreement_bp.route('/', methods=['GET'])
def get_agreements():
    """Get tenancy agreements for the current user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    # Get agreements where user is either tenant or landlord
    agreements = TenancyAgreement.query.filter(
        (TenancyAgreement.tenant_id == user_id) | 
        (TenancyAgreement.landlord_id == user_id)
    ).order_by(TenancyAgreement.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'agreements': [agreement.to_dict() for agreement in agreements]
    })


@tenancy_agreement_bp.route('/<int:agreement_id>', methods=['GET'])
def get_agreement(agreement_id):
    """Get a specific tenancy agreement"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    agreement = TenancyAgreement.query.get(agreement_id)
    if not agreement:
        return jsonify({'success': False, 'error': 'Agreement not found'}), 404
    
    # Check if user has access to this agreement
    if agreement.tenant_id != user_id and agreement.landlord_id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
    
    return jsonify({
        'success': True,
        'agreement': agreement.to_dict()
    })


@tenancy_agreement_bp.route('/tenant', methods=['GET'])
def get_tenant_agreements():
    """Get tenancy agreements for the current tenant"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    # Get agreements where user is the tenant
    agreements = TenancyAgreement.query.filter(
        TenancyAgreement.tenant_id == user_id
    ).order_by(TenancyAgreement.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'agreements': [agreement.to_dict() for agreement in agreements]
    })


@tenancy_agreement_bp.route('/create-from-application', methods=['POST'])
def create_agreement_from_application():
    """Create a tenancy agreement from an approved application"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        application_id = data.get('application_id')
        
        if not application_id:
            return jsonify({'success': False, 'error': 'Application ID is required'}), 400
        
        # Get the application
        application = Application.query.get(application_id)
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Check if user is the landlord for this application
        if application.landlord_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Only the landlord can create agreements'}), 403
        
        # Check if application is approved
        if application.status != 'approved':
            return jsonify({'success': False, 'error': 'Application must be approved first'}), 400
        
        # Check if agreement already exists
        existing_agreement = TenancyAgreement.query.filter_by(application_id=application_id).first()
        if existing_agreement:
            return jsonify({'success': False, 'error': 'Agreement already exists for this application'}), 409
        
        # Get property and user details
        property_obj = application.property
        tenant = application.tenant
        landlord = User.query.get(application.landlord_id)
        
        if not property_obj or not tenant or not landlord:
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Calculate lease dates (default to 12 months from move-in date or today)
        lease_start_date = application.move_in_date or datetime.utcnow().date()
        lease_duration_months = 12  # Default to 12 months
        lease_end_date = lease_start_date + timedelta(days=lease_duration_months * 30)  # Approximate
        
        # Calculate expiry time (48 hours from now)
        expires_at_time = datetime.utcnow() + timedelta(hours=48)
        logger.info(f"Creating agreement with expires_at: {expires_at_time}")
        
        # Create the tenancy agreement
        agreement = TenancyAgreement(
            application_id=application.id,
            property_id=application.property_id,
            tenant_id=application.tenant_id,
            landlord_id=application.landlord_id,
            
            # Agreement terms
            monthly_rent=property_obj.price,
            security_deposit=property_obj.price * 2,  # Default to 2 months rent
            lease_start_date=lease_start_date,
            lease_end_date=lease_end_date,
            lease_duration_months=lease_duration_months,
            
            # Property snapshot
            property_address=f"{property_obj.title}, {property_obj.location}",
            property_type=property_obj.property_type,
            property_bedrooms=property_obj.bedrooms,
            property_bathrooms=property_obj.bathrooms,
            property_sqft=property_obj.sqft,
            
            # Tenant snapshot
            tenant_full_name=application.full_name or tenant.username,
            tenant_phone=application.phone_number or '',
            tenant_email=application.email or tenant.email,
            
            # Landlord snapshot
            landlord_full_name=landlord.username,
            landlord_phone='',  # TODO: Add phone to User model
            landlord_email=landlord.email,
            
            # Additional terms
            furnished_status=getattr(property_obj, 'furnished', 'unfurnished'),
            utilities_included=False,  # Default
            parking_included=getattr(property_obj, 'parking', 0) > 0,
            
            # Set expiry to 48 hours from creation if not completed
            expires_at=expires_at_time
        )
        
        db.session.add(agreement)
        db.session.commit()
        
        # Debug: Verify expires_at was set correctly
        logger.info(f"Agreement created with ID: {agreement.id}, expires_at: {agreement.expires_at}")
        
        # Generate draft PDF
        try:
            pdf_paths = pdf_service.update_agreement_pdfs(agreement)
            agreement.draft_pdf_path = pdf_paths['draft_pdf_path']
            if pdf_paths['final_pdf_path']:
                agreement.final_pdf_path = pdf_paths['final_pdf_path']
            db.session.commit()
            logger.info(f"Generated PDFs for agreement {agreement.id}")
        except Exception as pdf_error:
            logger.warning(f"Failed to generate PDFs for agreement {agreement.id}: {str(pdf_error)}")
            # Don't fail the entire operation if PDF generation fails
        
        logger.info(f"Created tenancy agreement {agreement.id} for application {application_id}")
        
        return jsonify({
            'success': True,
            'agreement': agreement.to_dict(),
            'message': 'Tenancy agreement created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating tenancy agreement: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/<int:agreement_id>/sign', methods=['POST'])
def sign_agreement(agreement_id):
    """Record a signature for the agreement"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        user_id = session['user_id']
        data = request.get_json()
        signature_id = data.get('signature_id')  # From SignWell API
        
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if user has access to this agreement
        if agreement.tenant_id != user_id and agreement.landlord_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Check if agreement is in correct status
        if agreement.status != 'pending_signatures':
            return jsonify({'success': False, 'error': 'Agreement is not in signing phase'}), 400
        
        # Record the signature
        now = datetime.utcnow()
        if user_id == agreement.landlord_id:
            if agreement.landlord_signed_at:
                return jsonify({'success': False, 'error': 'Landlord has already signed'}), 400
            agreement.landlord_signed_at = now
            agreement.landlord_signature_id = signature_id
        elif user_id == agreement.tenant_id:
            if agreement.tenant_signed_at:
                return jsonify({'success': False, 'error': 'Tenant has already signed'}), 400
            agreement.tenant_signed_at = now
            agreement.tenant_signature_id = signature_id
        
        # Check if both parties have signed
        if agreement.is_fully_signed:
            agreement.status = 'pending_payment'
            logger.info(f"Agreement {agreement_id} fully signed, moving to payment phase")
        
        agreement.updated_at = now
        db.session.commit()
        
        return jsonify({
            'success': True,
            'agreement': agreement.to_dict(),
            'message': 'Signature recorded successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording signature: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/<int:agreement_id>/payment', methods=['POST'])
def record_payment(agreement_id):
    """Record payment completion for the agreement"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        user_id = session['user_id']
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')  # From Stripe
        payment_method = data.get('payment_method', 'credit_card')
        
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Only tenant can make payment
        if agreement.tenant_id != user_id:
            return jsonify({'success': False, 'error': 'Only tenant can make payment'}), 403
        
        # Check if agreement is in correct status
        if agreement.status != 'pending_payment':
            return jsonify({'success': False, 'error': 'Agreement is not in payment phase'}), 400
        
        # Check if payment already completed
        if agreement.payment_completed_at:
            return jsonify({'success': False, 'error': 'Payment already completed'}), 400
        
        # Record payment
        now = datetime.utcnow()
        agreement.payment_completed_at = now
        agreement.payment_intent_id = payment_intent_id
        agreement.payment_method = payment_method
        
        # Update agreement status to website_fee_paid (not active yet - deposit payment will activate it)
        agreement.status = 'website_fee_paid'
        agreement.payment_completed_at = datetime.utcnow()
        agreement.updated_at = now
        
        # Note: Property will transition to rented when deposit is paid and agreement becomes active
        
        # 🏠 CREATE DEPOSIT TRANSACTION AUTOMATICALLY (but don't activate agreement yet)
        try:
            deposit_service = DepositService()
            deposit_result = deposit_service.create_deposit_for_agreement(agreement.id)
            
            if deposit_result['success']:
                logger.info(f"Deposit transaction created for agreement {agreement_id}: {deposit_result['deposit']['id']}")
                deposit_info = {
                    'deposit_id': deposit_result['deposit']['id'],
                    'deposit_amount': deposit_result['deposit']['total_amount'],
                    'deposit_status': deposit_result['deposit']['status']
                }
            else:
                logger.warning(f"Failed to create deposit for agreement {agreement_id}: {deposit_result['error']}")
                deposit_info = None
        except Exception as e:
            logger.error(f"Error creating deposit for agreement {agreement_id}: {str(e)}")
            deposit_info = None
        
        db.session.commit()
        
        logger.info(f"Payment completed for agreement {agreement_id}, agreement activated")
        
        # Include deposit information in response
        response_data = {
            'success': True,
            'agreement': agreement.to_dict(),
            'message': 'Payment recorded and agreement activated'
        }
        
        if deposit_info:
            response_data['deposit'] = deposit_info
            response_data['message'] += ' - Deposit system initialized'
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording payment: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/<int:agreement_id>/status', methods=['GET'])
def get_agreement_status(agreement_id):
    """Get the current status of an agreement"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    agreement = TenancyAgreement.query.get(agreement_id)
    if not agreement:
        return jsonify({'success': False, 'error': 'Agreement not found'}), 404
    
    # Check if user has access to this agreement
    if agreement.tenant_id != user_id and agreement.landlord_id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
    
    return jsonify({
        'success': True,
        'status': agreement.status,
        'is_fully_signed': agreement.is_fully_signed,
        'is_payment_completed': agreement.is_payment_completed,
        'can_be_activated': agreement.can_be_activated,
        'days_until_expiry': agreement.days_until_expiry
    })



@tenancy_agreement_bp.route('/<int:agreement_id>/download/<pdf_type>', methods=['GET'])
def download_agreement_pdf(agreement_id, pdf_type):
    """Download agreement PDF (draft or final)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        user_id = session['user_id']
        
        # Get the agreement
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if user has access to this agreement
        if agreement.tenant_id != user_id and agreement.landlord_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Get the appropriate PDF path
        if pdf_type == 'draft':
            pdf_path = agreement.draft_pdf_path
        elif pdf_type == 'final':
            pdf_path = agreement.final_pdf_path
        else:
            return jsonify({'success': False, 'error': 'Invalid PDF type'}), 400
        
        # If PDF doesn't exist, try to generate it
        if not pdf_path or not os.path.exists(pdf_path):
            logger.info(f"PDF not found for agreement {agreement_id}, attempting to generate...")
            
            try:
                # Generate PDFs using PDF service
                pdf_paths = pdf_service.update_agreement_pdfs(agreement)
                
                if pdf_type == 'draft' and pdf_paths.get('draft_pdf_path'):
                    agreement.draft_pdf_path = pdf_paths['draft_pdf_path']
                    pdf_path = agreement.draft_pdf_path
                elif pdf_type == 'final' and pdf_paths.get('final_pdf_path'):
                    agreement.final_pdf_path = pdf_paths['final_pdf_path']
                    pdf_path = agreement.final_pdf_path
                
                db.session.commit()
                logger.info(f"Generated {pdf_type} PDF for agreement {agreement_id}: {pdf_path}")
                
            except Exception as gen_error:
                logger.error(f"Error generating {pdf_type} PDF for agreement {agreement_id}: {str(gen_error)}")
                return jsonify({'success': False, 'error': f'Could not generate {pdf_type} PDF'}), 500
        
        # Final check if PDF exists
        if not pdf_path or not os.path.exists(pdf_path):
            logger.error(f"{pdf_type.title()} PDF still not found for agreement {agreement_id}")
            return jsonify({'success': False, 'error': 'PDF not found'}), 404
        
        # Generate filename for download
        filename = f"tenancy_agreement_{agreement.id}_{pdf_type}.pdf"
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error downloading PDF for agreement {agreement_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/<int:agreement_id>/regenerate-pdf', methods=['POST'])
def regenerate_agreement_pdf(agreement_id):
    """Regenerate PDFs for an agreement"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        user_id = session['user_id']
        
        # Get the agreement
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if user is the landlord (only landlords can regenerate PDFs)
        if agreement.landlord_id != user_id:
            return jsonify({'success': False, 'error': 'Only landlords can regenerate PDFs'}), 403
        
        # Clean up old PDFs
        pdf_service.cleanup_old_pdfs(agreement)
        
        # Generate new PDFs
        pdf_paths = pdf_service.update_agreement_pdfs(agreement)
        agreement.draft_pdf_path = pdf_paths['draft_pdf_path']
        if pdf_paths['final_pdf_path']:
            agreement.final_pdf_path = pdf_paths['final_pdf_path']
        
        db.session.commit()
        
        logger.info(f"Regenerated PDFs for agreement {agreement.id}")
        
        return jsonify({
            'success': True,
            'message': 'PDFs regenerated successfully',
            'agreement': agreement.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error regenerating PDFs for agreement {agreement_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/<int:agreement_id>/preview', methods=['GET'])
def preview_agreement(agreement_id):
    """Preview agreement in browser (HTML version)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        user_id = session['user_id']
        
        # Get the agreement
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if user has access to this agreement
        if agreement.tenant_id != user_id and agreement.landlord_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        agreement_property = Property.query.get(agreement.property_id)
        if not property:
            return jsonify({'success': False, 'error': 'Associated property not found'}), 404
        
        # Render the HTML template for preview
        from flask import render_template
        return render_template(
            'tenancy_agreement.html',
            agreement=agreement,
            property=agreement_property,
            is_draft=agreement.status != 'active'
        )
        
    except Exception as e:
        logger.error(f"Error previewing agreement {agreement_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500



@tenancy_agreement_bp.route('/<int:agreement_id>/initiate-signing', methods=['POST'])
@login_required
def initiate_signing(agreement_id):
    """Initiate the SignWell signing process for an agreement"""
    try:
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if user has access to this agreement
        if agreement.tenant_id != current_user.id and agreement.landlord_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Check if agreement is ready for signing
        if agreement.status != 'pending_signatures':
            return jsonify({'success': False, 'error': 'Agreement is not ready for signing'}), 400
        
        # Initiate signing process through workflow coordinator
        result = workflow_coordinator.initiate_signing_process(agreement_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'signing_url': result['signing_url'],
                'signature_request_id': result['signature_request_id'],
                'message': 'Signing process initiated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error initiating signing process: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/<int:agreement_id>/initiate-payment', methods=['POST'])
# @login_required  <-- This line is removed
def initiate_payment(agreement_id):
    """Initiate the Stripe payment process for an agreement"""
    # This function requires a valid session to get the current_user,
    # so we'll check for it manually instead of using the decorator.
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    current_user_id = session['user_id']

    try:
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404

        # Security check: ensure the current user is the tenant
        if agreement.tenant_id != current_user_id:
            return jsonify({'success': False, 'error': 'Only the tenant can initiate payment'}), 403

        # Check if agreement is ready for payment
        if agreement.status != 'pending_payment':
            return jsonify({'success': False, 'error': 'Agreement is not ready for payment'}), 400

        # Use the stripe_service to create the payment intent
        result = stripe_service.create_payment_intent(agreement)

        if result['success']:
            # Save the payment intent ID to the agreement
            agreement.payment_intent_id = result['payment_intent_id']
            db.session.commit()

            return jsonify({
                'success': True,
                'client_secret': result['client_secret'],
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to create payment intent')
            }), 500

    except Exception as e:
        logger.error(f"Error initiating payment process: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@tenancy_agreement_bp.route('/<int:agreement_id>/cancel', methods=['POST'])
@login_required
def cancel_agreement(agreement_id):
    """Cancel an agreement and clean up external services"""
    try:
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if user has access to this agreement
        if agreement.tenant_id != current_user.id and agreement.landlord_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Check if agreement can be cancelled
        if agreement.status in ['active', 'cancelled']:
            return jsonify({'success': False, 'error': 'Agreement cannot be cancelled'}), 400
        
        data = request.get_json()
        reason = data.get('reason', 'User cancellation')
        
        # Cancel agreement through workflow coordinator
        result = workflow_coordinator.cancel_agreement(agreement_id, reason)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Agreement cancelled successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error cancelling agreement: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@tenancy_agreement_bp.route('/service-status', methods=['GET'])
@login_required
def get_service_status():
    """Get status of external services"""
    try:
        status = workflow_coordinator.get_service_status()
        
        return jsonify({
            'success': True,
            'services': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/<int:agreement_id>/withdraw-offer', methods=['POST'])
def withdraw_landlord_offer(agreement_id):
    """Allow landlord to withdraw their offer before tenant signs"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if user is the landlord
        if agreement.landlord_id != user_id:
            return jsonify({'success': False, 'error': 'Only the landlord can withdraw the offer'}), 403
        
        # Check if landlord can withdraw
        if not agreement.can_landlord_withdraw:
            return jsonify({'success': False, 'error': 'Cannot withdraw offer at this stage'}), 400
        
        data = request.get_json()
        reason = data.get('reason', 'Landlord changed mind')
        
        # Update agreement with withdrawal info
        agreement.landlord_withdrawn_at = datetime.utcnow()
        agreement.withdrawn_by = user_id
        agreement.withdrawal_reason = reason
        agreement.status = 'withdrawn'
        
        # Revert property from Pending back to Active when landlord withdraws offer
        property_obj = Property.query.get(agreement.property_id)
        if property_obj and property_obj.status == PropertyStatus.PENDING:
            if property_obj.transition_to_active():
                logger.info(f"Property {property_obj.id} reverted to Active status after landlord withdrawal")
            else:
                logger.warning(f"Failed to revert property {property_obj.id} to Active status")
        
        db.session.commit()
        
        logger.info(f"Landlord {user_id} withdrew offer for agreement {agreement_id}")
        
        return jsonify({
            'success': True,
            'message': 'Offer withdrawn successfully',
            'agreement': agreement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error withdrawing landlord offer: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/<int:agreement_id>/withdraw-signature', methods=['POST'])
def withdraw_tenant_signature(agreement_id):
    """Allow tenant to withdraw their signature before landlord counter-signs"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if user is the tenant
        if agreement.tenant_id != user_id:
            return jsonify({'success': False, 'error': 'Only the tenant can withdraw their signature'}), 403
        
        # Check if tenant can withdraw
        if not agreement.can_tenant_withdraw:
            return jsonify({'success': False, 'error': 'Cannot withdraw signature at this stage'}), 400
        
        data = request.get_json()
        reason = data.get('reason', 'Tenant changed mind')
        
        # Update agreement with withdrawal info
        agreement.tenant_withdrawn_at = datetime.utcnow()
        agreement.tenant_signed_at = None  # Remove the signature
        agreement.tenant_signature_id = None
        agreement.withdrawn_by = user_id
        agreement.withdrawal_reason = reason
        agreement.status = 'pending_signatures'  # Back to pending signatures
        
        db.session.commit()
        
        logger.info(f"Tenant {user_id} withdrew signature for agreement {agreement_id}")
        
        return jsonify({
            'success': True,
            'message': 'Signature withdrawn successfully',
            'agreement': agreement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error withdrawing tenant signature: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/<int:agreement_id>/check-expiry', methods=['GET'])
def check_agreement_expiry(agreement_id):
    """Check if agreement has expired and update status if needed"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        agreement = TenancyAgreement.query.get(agreement_id)
        if not agreement:
            return jsonify({'success': False, 'error': 'Agreement not found'}), 404
        
        # Check if user has access to this agreement
        if agreement.tenant_id != user_id and agreement.landlord_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Check if agreement has expired
        if agreement.is_expired and agreement.status not in ['active', 'cancelled', 'withdrawn', 'expired']:
            agreement.status = 'expired'
            agreement.cancelled_at = datetime.utcnow()
            agreement.cancellation_reason = 'Agreement expired - not completed within time limit'
            
            # Revert property from Pending back to Active when agreement expires
            property_obj = Property.query.get(agreement.property_id)
            if property_obj and property_obj.status == PropertyStatus.PENDING:
                if property_obj.transition_to_active():
                    logger.info(f"Property {property_obj.id} reverted to Active status after agreement expiration")
                else:
                    logger.warning(f"Failed to revert property {property_obj.id} to Active status")
            
            db.session.commit()
            
            logger.info(f"Agreement {agreement_id} marked as expired")
        
        return jsonify({
            'success': True,
            'agreement': agreement.to_dict(),
            'is_expired': agreement.is_expired,
            'hours_until_expiry': agreement.hours_until_expiry
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking agreement expiry: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/admin/expire-check', methods=['POST'])
def admin_expire_check():
    """Admin endpoint to manually trigger expiry check for all agreements"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        from ..services.expiry_service import expiry_service
        
        # Run the expiry check
        expired_count = expiry_service.check_and_expire_agreements()
        
        # Get statistics
        stats = expiry_service.get_expiry_statistics()
        
        return jsonify({
            'success': True,
            'expired_count': expired_count,
            'statistics': stats,
            'message': f'Expiry check completed. {expired_count} agreements expired.'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in admin expiry check: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@tenancy_agreement_bp.route('/admin/expiry-stats', methods=['GET'])
def admin_expiry_stats():
    """Admin endpoint to get expiry statistics"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        from ..services.expiry_service import expiry_service
        
        # Get statistics
        stats = expiry_service.get_expiry_statistics()
        
        # Get agreements expiring soon
        expiring_soon = expiry_service.get_expiring_soon_agreements(hours_ahead=24)
        expiring_soon_data = [agreement.to_dict() for agreement in expiring_soon]
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'expiring_soon': expiring_soon_data,
            'expiring_soon_count': len(expiring_soon_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting expiry statistics: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

