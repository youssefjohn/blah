"""
Workflow Coordinator for Tenancy Agreement Process
Orchestrates SignWell, Stripe, and S3 services for complete agreement workflow
"""

import os
import logging
from datetime import datetime
from flask import current_app

from .signwell_service import signwell_service
from .stripe_service import stripe_service
from .s3_service import s3_service
from .pdf_service import pdf_service
from ..models.tenancy_agreement import TenancyAgreement
from ..models.property import Property, PropertyStatus
from ..models import db

logger = logging.getLogger(__name__)

class WorkflowCoordinator:
    """Coordinates the complete tenancy agreement workflow"""
    
    def __init__(self):
        self.signwell = signwell_service
        self.stripe = stripe_service
        self.s3 = s3_service
        self.pdf = pdf_service
    
    def initiate_signing_process(self, agreement_id):
        """
        Initiate the complete signing process for an agreement
        
        Args:
            agreement_id: TenancyAgreement ID
            
        Returns:
            dict: Process initiation result
        """
        try:
            # Get agreement
            agreement = TenancyAgreement.query.get(agreement_id)
            if not agreement:
                return {'success': False, 'error': 'Agreement not found'}
            
            if agreement.status != 'pending_signatures':
                return {'success': False, 'error': 'Agreement not ready for signing'}
            
            # Step 1: Generate fresh PDF
            pdf_result = self._generate_and_store_pdf(agreement)
            if not pdf_result['success']:
                return pdf_result
            
            # Step 2: Upload to S3 (if configured)
            s3_key = None
            if self.s3.is_configured():
                s3_result = self._upload_to_s3(agreement, pdf_result['pdf_path'])
                if s3_result['success']:
                    s3_key = s3_result['key']
                    agreement.s3_draft_key = s3_key
            
            # Step 3: Create SignWell signature request
            signwell_result = self.signwell.create_signature_request(
                agreement, pdf_result['pdf_path']
            )
            
            if not signwell_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to create signature request: {signwell_result['error']}"
                }
            
            # Step 4: Update agreement with SignWell details
            agreement.signwell_request_id = signwell_result['signature_request_id']
            agreement.signing_url = signwell_result['signing_url']
            agreement.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Initiated signing process for agreement {agreement_id}")
            
            return {
                'success': True,
                'signing_url': signwell_result['signing_url'],
                'signature_request_id': signwell_result['signature_request_id'],
                's3_key': s3_key
            }
            
        except Exception as e:
            logger.error(f"Error initiating signing process: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def initiate_payment_process(self, agreement_id):
        """
        Initiate payment process for a fully signed agreement
        
        Args:
            agreement_id: TenancyAgreement ID
            
        Returns:
            dict: Payment initiation result
        """
        try:
            # Get agreement
            agreement = TenancyAgreement.query.get(agreement_id)
            if not agreement:
                return {'success': False, 'error': 'Agreement not found'}
            
            if agreement.status != 'pending_payment':
                return {'success': False, 'error': 'Agreement not ready for payment'}
            
            # Create Stripe payment intent
            payment_result = self.stripe.create_payment_intent(agreement)
            
            if not payment_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to create payment intent: {payment_result['error']}"
                }
            
            # Update agreement with payment details
            agreement.stripe_payment_intent_id = payment_result['payment_intent_id']
            agreement.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Initiated payment process for agreement {agreement_id}")
            
            return {
                'success': True,
                'payment_intent_id': payment_result['payment_intent_id'],
                'client_secret': payment_result['client_secret'],
                'amount': payment_result['amount'],
                'currency': payment_result['currency']
            }
            
        except Exception as e:
            logger.error(f"Error initiating payment process: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def handle_signature_completion(self, signature_request_id):
        """
        Handle completion of signature process
        
        Args:
            signature_request_id: SignWell signature request ID
            
        Returns:
            dict: Handling result
        """
        try:
            # Find agreement by SignWell request ID
            agreement = TenancyAgreement.query.filter_by(
                signwell_request_id=signature_request_id
            ).first()
            
            if not agreement:
                return {'success': False, 'error': 'Agreement not found'}
            
            # Download signed document from SignWell
            signed_pdf_path = f"documents/agreements/{agreement.id}_signed.pdf"
            os.makedirs(os.path.dirname(signed_pdf_path), exist_ok=True)
            
            download_success = self.signwell.download_signed_document(
                signature_request_id, signed_pdf_path
            )
            
            if download_success:
                agreement.final_pdf_path = signed_pdf_path
                
                # Upload signed document to S3 (if configured)
                if self.s3.is_configured():
                    s3_result = self._upload_signed_to_s3(agreement, signed_pdf_path)
                    if s3_result['success']:
                        agreement.s3_final_key = s3_result['key']
            
            # Update agreement status and timestamps
            agreement.status = 'pending_payment'
            agreement.landlord_signed_at = datetime.utcnow()
            agreement.tenant_signed_at = datetime.utcnow()
            agreement.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Processed signature completion for agreement {agreement.id}")
            
            # Automatically initiate payment process
            payment_result = self.initiate_payment_process(agreement.id)
            
            return {
                'success': True,
                'agreement_id': agreement.id,
                'status': agreement.status,
                'payment_initiated': payment_result['success'],
                'payment_details': payment_result if payment_result['success'] else None
            }
            
        except Exception as e:
            logger.error(f"Error handling signature completion: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def handle_payment_completion(self, payment_intent_id):
        """
        Handle completion of payment process
        
        Args:
            payment_intent_id: Stripe payment intent ID
            
        Returns:
            dict: Handling result
        """
        try:
            # Find agreement by Stripe payment intent ID
            agreement = TenancyAgreement.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if not agreement:
                return {'success': False, 'error': 'Agreement not found'}
            
            # Ensure final PDF is available for download
            if not agreement.final_pdf_path or not os.path.exists(agreement.final_pdf_path):
                logger.info(f"Final PDF missing for agreement {agreement.id}, generating...")
                
                # Generate final PDF using PDF service
                try:
                    pdf_result = self.pdf.update_agreement_pdfs(agreement)
                    if pdf_result.get('final_pdf_path'):
                        agreement.final_pdf_path = pdf_result['final_pdf_path']
                        logger.info(f"Generated final PDF for agreement {agreement.id}: {agreement.final_pdf_path}")
                    else:
                        logger.warning(f"Could not generate final PDF for agreement {agreement.id}")
                except Exception as pdf_error:
                    logger.error(f"Error generating final PDF for agreement {agreement.id}: {str(pdf_error)}")
            
            # Update agreement status
            agreement.status = 'active'
            agreement.payment_completed_at = datetime.utcnow()
            agreement.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Processed payment completion for agreement {agreement.id}")
            
            return {
                'success': True,
                'agreement_id': agreement.id,
                'status': agreement.status
            }
            
        except Exception as e:
            logger.error(f"Error handling payment completion: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def cancel_agreement(self, agreement_id, reason='User cancellation'):
        """
        Cancel an agreement and clean up external services
        
        Args:
            agreement_id: TenancyAgreement ID
            reason: Cancellation reason
            
        Returns:
            dict: Cancellation result
        """
        try:
            agreement = TenancyAgreement.query.get(agreement_id)
            if not agreement:
                return {'success': False, 'error': 'Agreement not found'}
            
            # Cancel SignWell signature request if exists
            if agreement.signwell_request_id:
                self.signwell.cancel_signature_request(agreement.signwell_request_id)
            
            # Cancel Stripe payment intent if exists and not completed
            if agreement.stripe_payment_intent_id and not agreement.payment_completed_at:
                # Note: Stripe payment intents auto-cancel after 24 hours
                pass
            
            # Update agreement status
            agreement.status = 'cancelled'
            agreement.cancellation_reason = reason
            agreement.cancelled_at = datetime.utcnow()
            agreement.updated_at = datetime.utcnow()
            
            # Revert property from Pending back to Active when agreement is cancelled
            property_obj = Property.query.get(agreement.property_id)
            if property_obj and property_obj.status == PropertyStatus.PENDING:
                if property_obj.transition_to_active():
                    logger.info(f"Property {property_obj.id} reverted to Active status after agreement cancellation")
                else:
                    logger.warning(f"Failed to revert property {property_obj.id} to Active status")
            
            db.session.commit()
            
            logger.info(f"Cancelled agreement {agreement_id}: {reason}")
            
            return {
                'success': True,
                'agreement_id': agreement.id,
                'status': agreement.status
            }
            
        except Exception as e:
            logger.error(f"Error cancelling agreement: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def _generate_and_store_pdf(self, agreement):
        """Generate and store PDF for agreement"""
        try:
            pdf_path = f"documents/agreements/{agreement.id}_draft.pdf"
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            success = self.pdf.generate_agreement_pdf(agreement, pdf_path, watermark=True)
            
            if success:
                agreement.draft_pdf_path = pdf_path
                return {'success': True, 'pdf_path': pdf_path}
            else:
                return {'success': False, 'error': 'Failed to generate PDF'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _upload_to_s3(self, agreement, pdf_path):
        """Upload draft PDF to S3"""
        try:
            key = self.s3.generate_agreement_key(agreement.id, 'draft')
            result = self.s3.upload_document(pdf_path, key)
            return result
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _upload_signed_to_s3(self, agreement, pdf_path):
        """Upload signed PDF to S3"""
        try:
            key = self.s3.generate_agreement_key(agreement.id, 'signed')
            result = self.s3.upload_document(pdf_path, key)
            return result
        except Exception as e:
            logger.error(f"Error uploading signed PDF to S3: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_service_status(self):
        """Get status of all external services"""
        return {
            'signwell': {
                'configured': bool(self.signwell.api_key),
                'status': 'ready' if self.signwell.api_key else 'not_configured'
            },
            'stripe': {
                'configured': bool(self.stripe.api_key),
                'status': 'ready' if self.stripe.api_key else 'not_configured'
            },
            's3': {
                'configured': self.s3.is_configured(),
                'status': 'ready' if self.s3.is_configured() else 'not_configured'
            }
        }

# Global instance
workflow_coordinator = WorkflowCoordinator()

