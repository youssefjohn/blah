"""
SignWell Service for Digital Signatures
Handles document signing workflow with SignWell API
"""

import os
import requests
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)

class SignWellService:
    """Service for managing digital signatures with SignWell"""
    
    def __init__(self):
        self.api_key = os.getenv('SIGNWELL_API_KEY')
        self.base_url = 'https://www.signwell.com/api/v1'
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        if not self.api_key:
            logger.warning("SignWell API key not configured")
    
    def create_signature_request(self, agreement, pdf_path):
        """
        Create a signature request in SignWell
        
        Args:
            agreement: TenancyAgreement model instance
            pdf_path: Path to the PDF document to be signed
            
        Returns:
            dict: SignWell signature request response
        """
        try:
            # Upload document first
            document_id = self._upload_document(pdf_path, f"Agreement_{agreement.id}.pdf")
            if not document_id:
                raise Exception("Failed to upload document to SignWell")
            
            # Create signature request
            request_data = {
                "name": f"Tenancy Agreement - {agreement.property_address}",
                "subject": "Please sign your tenancy agreement",
                "message": f"Please review and sign the tenancy agreement for {agreement.property_address}",
                "document_id": document_id,
                "recipients": [
                    {
                        "name": agreement.landlord_full_name,
                        "email": agreement.landlord_email,
                        "role": "signer",
                        "order": 1,
                        "fields": [
                            {
                                "type": "signature",
                                "page": 1,
                                "x": 150,
                                "y": 700,
                                "width": 200,
                                "height": 50,
                                "required": True
                            },
                            {
                                "type": "date",
                                "page": 1,
                                "x": 150,
                                "y": 650,
                                "width": 100,
                                "height": 30,
                                "required": True
                            }
                        ]
                    },
                    {
                        "name": agreement.tenant_full_name,
                        "email": agreement.tenant_email,
                        "role": "signer",
                        "order": 2,
                        "fields": [
                            {
                                "type": "signature",
                                "page": 1,
                                "x": 400,
                                "y": 700,
                                "width": 200,
                                "height": 50,
                                "required": True
                            },
                            {
                                "type": "date",
                                "page": 1,
                                "x": 400,
                                "y": 650,
                                "width": 100,
                                "height": 30,
                                "required": True
                            }
                        ]
                    }
                ],
                "webhook_url": f"{current_app.config.get('BASE_URL', 'http://localhost:5001')}/api/webhooks/signwell",
                "redirect_url": f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/agreement/{agreement.id}?signed=true"
            }
            
            response = requests.post(
                f"{self.base_url}/signature_requests",
                json=request_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"Created SignWell signature request {result.get('id')} for agreement {agreement.id}")
                return {
                    'success': True,
                    'signature_request_id': result.get('id'),
                    'signing_url': result.get('signing_url'),
                    'data': result
                }
            else:
                logger.error(f"SignWell API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"SignWell API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error creating SignWell signature request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _upload_document(self, file_path, filename):
        """
        Upload a document to SignWell
        
        Args:
            file_path: Path to the file to upload
            filename: Name for the uploaded file
            
        Returns:
            str: Document ID if successful, None otherwise
        """
        try:
            with open(file_path, 'rb') as file:
                files = {
                    'file': (filename, file, 'application/pdf')
                }
                
                # Remove Content-Type header for file upload
                upload_headers = {
                    'X-API-Key': self.api_key
                }
                
                response = requests.post(
                    f"{self.base_url}/documents",
                    files=files,
                    headers=upload_headers,
                    timeout=60
                )
                
                if response.status_code == 201:
                    result = response.json()
                    document_id = result.get('id')
                    logger.info(f"Uploaded document to SignWell: {document_id}")
                    return document_id
                else:
                    logger.error(f"Failed to upload document to SignWell: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error uploading document to SignWell: {str(e)}")
            return None
    
    def get_signature_request_status(self, signature_request_id):
        """
        Get the status of a signature request
        
        Args:
            signature_request_id: SignWell signature request ID
            
        Returns:
            dict: Signature request status information
        """
        try:
            response = requests.get(
                f"{self.base_url}/signature_requests/{signature_request_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('status'),
                    'data': result
                }
            else:
                logger.error(f"Failed to get SignWell status: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"SignWell API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error getting SignWell status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_signed_document(self, signature_request_id, save_path):
        """
        Download the signed document from SignWell
        
        Args:
            signature_request_id: SignWell signature request ID
            save_path: Path to save the downloaded document
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/signature_requests/{signature_request_id}/download",
                headers=self.headers,
                timeout=60
            )
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Downloaded signed document from SignWell to {save_path}")
                return True
            else:
                logger.error(f"Failed to download signed document: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading signed document: {str(e)}")
            return False
    
    def cancel_signature_request(self, signature_request_id):
        """
        Cancel a signature request
        
        Args:
            signature_request_id: SignWell signature request ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/signature_requests/{signature_request_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 204:
                logger.info(f"Cancelled SignWell signature request {signature_request_id}")
                return True
            else:
                logger.error(f"Failed to cancel signature request: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling signature request: {str(e)}")
            return False
    
    def process_webhook(self, webhook_data):
        """
        Process SignWell webhook data
        
        Args:
            webhook_data: Webhook payload from SignWell
            
        Returns:
            dict: Processing result
        """
        try:
            event_type = webhook_data.get('event')
            signature_request_id = webhook_data.get('signature_request', {}).get('id')
            
            logger.info(f"Processing SignWell webhook: {event_type} for request {signature_request_id}")
            
            if event_type == 'signature_request.completed':
                return self._handle_signature_completed(webhook_data)
            elif event_type == 'signature_request.signed':
                return self._handle_signature_signed(webhook_data)
            elif event_type == 'signature_request.declined':
                return self._handle_signature_declined(webhook_data)
            else:
                logger.info(f"Unhandled SignWell webhook event: {event_type}")
                return {'success': True, 'message': 'Event acknowledged'}
                
        except Exception as e:
            logger.error(f"Error processing SignWell webhook: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _handle_signature_completed(self, webhook_data):
        """Handle signature request completion"""
        # This will be implemented in the workflow coordinator
        return {'success': True, 'message': 'Signature completed'}
    
    def _handle_signature_signed(self, webhook_data):
        """Handle individual signature"""
        # This will be implemented in the workflow coordinator
        return {'success': True, 'message': 'Signature recorded'}
    
    def _handle_signature_declined(self, webhook_data):
        """Handle signature decline"""
        # This will be implemented in the workflow coordinator
        return {'success': True, 'message': 'Signature declined'}

# Global instance
signwell_service = SignWellService()

