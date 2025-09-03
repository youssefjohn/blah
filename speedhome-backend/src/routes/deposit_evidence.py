from flask import Blueprint, request, jsonify, send_file, current_app, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from functools import wraps
import os
import uuid
from datetime import datetime

deposit_evidence_bp = Blueprint('deposit_evidence', __name__)

def require_auth(f):
    """Custom authentication decorator that uses session-based auth"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

from ..models.deposit_claim import db, DepositClaim, DepositClaimStatus, DepositClaimType
from ..models.deposit_transaction import DepositTransaction


class DepositEvidenceService:
    """Service for handling deposit evidence file uploads and management."""
    
    ALLOWED_EXTENSIONS = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    EVIDENCE_TYPES = ['photo', 'document']
    
    def __init__(self):
        self.upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'deposits')
        self.ensure_upload_directory()
    
    def ensure_upload_directory(self):
        """Ensure the upload directory exists."""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder, exist_ok=True)
    
    def validate_file(self, file, evidence_type):
        """
        Validate uploaded file for type, size, and evidence type.
        
        Args:
            file: Werkzeug FileStorage object
            evidence_type: Type of evidence being uploaded
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"
        
        if not file.filename:
            return False, "No filename provided"
        
        if evidence_type not in self.EVIDENCE_TYPES:
            return False, f"Invalid evidence type: {evidence_type}"
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum limit of {self.MAX_FILE_SIZE // (1024*1024)}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check file extension
        filename = secure_filename(file.filename.lower())
        if '.' not in filename:
            return False, "File must have an extension"
        
        extension = filename.rsplit('.', 1)[1]
        if extension not in self.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS.keys())}"
        
        # For photo evidence, only allow image types
        if evidence_type == 'photo' and extension not in ['jpg', 'jpeg', 'png']:
            return False, "Photo evidence must be JPG or PNG format"
        
        return True, None
    
    def generate_filename(self, original_filename, evidence_type, deposit_id, claim_item_id):
        """
        Generate a secure, unique filename for the uploaded evidence.
        
        Args:
            original_filename: Original filename from upload
            evidence_type: Type of evidence
            deposit_id: ID of the deposit
            claim_item_id: ID of the claim item
            
        Returns:
            str: Generated filename
        """
        # Get file extension
        secure_name = secure_filename(original_filename)
        extension = secure_name.rsplit('.', 1)[1].lower() if '.' in secure_name else 'bin'
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        filename = f"{evidence_type}_{deposit_id}_{claim_item_id}_{timestamp}_{unique_id}.{extension}"
        return filename
    
    def get_deposit_folder(self, deposit_id):
        """Get the folder path for a specific deposit."""
        deposit_folder = os.path.join(self.upload_folder, str(deposit_id), 'evidence')
        if not os.path.exists(deposit_folder):
            os.makedirs(deposit_folder, exist_ok=True)
        return deposit_folder
    
    def save_file(self, file, evidence_type, deposit_id, claim_item_id):
        """
        Save uploaded file to the file system.
        
        Args:
            file: Werkzeug FileStorage object
            evidence_type: Type of evidence
            deposit_id: ID of the deposit
            claim_item_id: ID of the claim item
            
        Returns:
            tuple: (success, file_path_or_error)
        """
        try:
            # Validate file
            is_valid, error_message = self.validate_file(file, evidence_type)
            if not is_valid:
                return False, error_message
            
            # Generate filename and path
            filename = self.generate_filename(file.filename, evidence_type, deposit_id, claim_item_id)
            deposit_folder = self.get_deposit_folder(deposit_id)
            file_path = os.path.join(deposit_folder, filename)
            
            # Save file
            file.save(file_path)
            
            # Return relative path for database storage
            relative_path = os.path.join('uploads', 'deposits', str(deposit_id), 'evidence', filename)
            
            current_app.logger.info(f"Evidence file saved successfully: {relative_path}")
            return True, relative_path
            
        except Exception as e:
            current_app.logger.error(f"Error saving evidence file: {str(e)}")
            return False, f"Failed to save file: {str(e)}"
    
    def delete_file(self, file_path):
        """
        Delete a file from the file system.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            if not file_path:
                return True, None  # Nothing to delete
            
            # Convert relative path to absolute path
            abs_path = os.path.join(current_app.root_path, '..', file_path)
            
            if os.path.exists(abs_path):
                os.remove(abs_path)
                current_app.logger.info(f"Evidence file deleted successfully: {file_path}")
            
            return True, None
            
        except Exception as e:
            current_app.logger.error(f"Error deleting evidence file: {str(e)}")
            return False, f"Failed to delete file: {str(e)}"
    
    def get_file_info(self, file_path):
        """
        Get information about a file.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            dict: File information or None if file doesn't exist
        """
        try:
            if not file_path:
                return None
            
            abs_path = os.path.join(current_app.root_path, '..', file_path)
            
            if not os.path.exists(abs_path):
                return None
            
            stat = os.stat(abs_path)
            
            return {
                'path': file_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'exists': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting evidence file info: {str(e)}")
            return None


def get_evidence_service():
    """Get DepositEvidenceService instance within application context."""
    return DepositEvidenceService()


@deposit_evidence_bp.route('/api/deposits/<int:deposit_id>/evidence/temp', methods=['POST'])
@require_auth
def upload_temporary_evidence_file(deposit_id):
    """
    Upload an evidence file temporarily for a deposit claim item.
    Files are stored temporarily and will be moved to permanent location when claim is submitted.
    
    Expected form data:
    - file: The file to upload
    - evidence_type: Type of evidence (photo, document)
    - claim_item_id: Frontend claim item ID (for organization)
    """
    try:
        evidence_service = get_evidence_service()
        
        # Get the deposit transaction to verify access
        deposit = DepositTransaction.query.get_or_404(deposit_id)
        
        # Check if user has permission to upload evidence for this deposit
        # Allow both landlord and tenant to upload evidence
        if session['user_id'] not in [deposit.landlord_id, deposit.tenant_id]:
            return jsonify({'error': 'Unauthorized to upload evidence for this deposit'}), 403
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        evidence_type = request.form.get('evidence_type')
        claim_item_id = request.form.get('claim_item_id', 'temp')
        
        if not evidence_type:
            return jsonify({'error': 'Evidence type is required'}), 400
        
        # Validate evidence type
        if evidence_type not in evidence_service.EVIDENCE_TYPES:
            return jsonify({'error': f'Invalid evidence type. Allowed types: {", ".join(evidence_service.EVIDENCE_TYPES)}'}), 400
        
        # Save the file to temporary location
        success, result = evidence_service.save_file(file, evidence_type, deposit_id, f"temp_{claim_item_id}")
        
        if not success:
            return jsonify({'error': result}), 400
        
        # Get file info for response
        file_info = evidence_service.get_file_info(result)
        
        # Generate a unique evidence ID for frontend reference
        evidence_id = f"temp_{claim_item_id}_{evidence_type}_{datetime.now().timestamp()}"
        
        return jsonify({
            'message': 'Evidence file uploaded successfully',
            'evidence_type': evidence_type,
            'evidence_id': evidence_id,
            'file_path': result,
            'file_info': file_info,
            'original_name': file.filename
        }), 200
        
    except RequestEntityTooLarge:
        return jsonify({'error': f'File too large. Maximum size is {evidence_service.MAX_FILE_SIZE // (1024*1024)}MB'}), 413
    
    except Exception as e:
        current_app.logger.error(f"Error uploading temporary evidence file: {str(e)}")
        return jsonify({'error': 'Internal server error during file upload'}), 500


@deposit_evidence_bp.route('/api/deposits/<int:deposit_id>/evidence/<evidence_id>', methods=['GET'])
@require_auth
def get_evidence_file(deposit_id, evidence_id):
    """
    Download or view an evidence file for a specific deposit.
    """
    try:
        evidence_service = get_evidence_service()
        
        # Get the deposit transaction to verify access
        deposit = DepositTransaction.query.get_or_404(deposit_id)
        
        # Check if user has permission to view evidence for this deposit
        # Allow landlord, tenant, and admin to view evidence
        if session['user_id'] not in [deposit.landlord_id, deposit.tenant_id]:
            # TODO: Add admin check here if needed
            return jsonify({'error': 'Unauthorized to view evidence for this deposit'}), 403
        
        # Parse evidence_id to get claim_item_id and evidence_type
        # Format: {claim_item_id}_{evidence_type}_{index}
        try:
            parts = evidence_id.split('_')
            if len(parts) < 3:
                return jsonify({'error': 'Invalid evidence ID format'}), 400
            
            claim_item_id = parts[0]
            evidence_type = parts[1]
            evidence_index = int(parts[2])
        except (ValueError, IndexError):
            return jsonify({'error': 'Invalid evidence ID format'}), 400
        
        # Get the claim item
        claim_item = DepositClaimItem.query.get(claim_item_id)
        if not claim_item:
            return jsonify({'error': 'Claim item not found'}), 404
        
        # Get the file path from the claim item
        if evidence_type == 'photo':
            evidence_files = claim_item.evidence_photos or []
        elif evidence_type == 'document':
            evidence_files = claim_item.evidence_documents or []
        else:
            return jsonify({'error': 'Invalid evidence type'}), 400
        
        if evidence_index >= len(evidence_files):
            return jsonify({'error': 'Evidence file not found'}), 404
        
        file_path = evidence_files[evidence_index]
        
        if not file_path:
            return jsonify({'error': f'No {evidence_type} found for this claim item'}), 404
        
        # Convert relative path to absolute path
        abs_path = os.path.join(current_app.root_path, '..', file_path)
        
        if not os.path.exists(abs_path):
            current_app.logger.error(f"Evidence file not found on disk: {abs_path}")
            return jsonify({'error': 'File not found on server'}), 404
        
        # Determine if this should be downloaded or displayed inline
        download = request.args.get('download', 'false').lower() == 'true'
        
        # Get original filename for download
        original_filename = os.path.basename(file_path)
        
        return send_file(
            abs_path,
            as_attachment=download,
            download_name=original_filename if download else None,
            mimetype=None  # Let Flask auto-detect
        )
        
    except Exception as e:
        current_app.logger.error(f"Error serving evidence file: {str(e)}")
        return jsonify({'error': 'Internal server error while serving file'}), 500


@deposit_evidence_bp.route('/api/deposits/<int:deposit_id>/evidence/<evidence_id>', methods=['DELETE'])
@require_auth
def delete_evidence_file(deposit_id, evidence_id):
    """
    Delete an evidence file for a specific deposit claim.
    """
    try:
        evidence_service = get_evidence_service()
        
        # Get the deposit transaction to verify access
        deposit = DepositTransaction.query.get_or_404(deposit_id)
        
        # Check if user has permission to delete evidence for this deposit
        # Only allow the user who uploaded it (landlord or tenant)
        if session['user_id'] not in [deposit.landlord_id, deposit.tenant_id]:
            return jsonify({'error': 'Unauthorized to delete evidence for this deposit'}), 403
        
        # Parse evidence_id to get claim_item_id and evidence_type
        try:
            parts = evidence_id.split('_')
            if len(parts) < 3:
                return jsonify({'error': 'Invalid evidence ID format'}), 400
            
            claim_item_id = parts[0]
            evidence_type = parts[1]
            evidence_index = int(parts[2])
        except (ValueError, IndexError):
            return jsonify({'error': 'Invalid evidence ID format'}), 400
        
        # Get the claim item
        claim_item = DepositClaimItem.query.get(claim_item_id)
        if not claim_item:
            return jsonify({'error': 'Claim item not found'}), 404
        
        # Get the file path from the claim item
        if evidence_type == 'photo':
            evidence_files = claim_item.evidence_photos or []
        elif evidence_type == 'document':
            evidence_files = claim_item.evidence_documents or []
        else:
            return jsonify({'error': 'Invalid evidence type'}), 400
        
        if evidence_index >= len(evidence_files):
            return jsonify({'error': 'Evidence file not found'}), 404
        
        file_path = evidence_files[evidence_index]
        
        # Delete the file from the file system
        success, error = evidence_service.delete_file(file_path)
        
        if not success:
            current_app.logger.error(f"Failed to delete evidence file: {error}")
            # Continue with database update even if file deletion fails
        
        # Remove the file path from the list
        evidence_files.pop(evidence_index)
        
        # Update the claim item record
        if evidence_type == 'photo':
            claim_item.evidence_photos = evidence_files
        else:
            claim_item.evidence_documents = evidence_files
        
        try:
            db.session.commit()
            current_app.logger.info(f"Evidence file deleted successfully: {evidence_type} for deposit {deposit_id}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during evidence deletion: {str(e)}")
            return jsonify({'error': 'Failed to update claim record'}), 500
        
        return jsonify({
            'message': f'{evidence_type} evidence deleted successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting evidence file: {str(e)}")
        return jsonify({'error': 'Internal server error during file deletion'}), 500


@deposit_evidence_bp.route('/api/deposits/<int:deposit_id>/evidence', methods=['GET'])
@require_auth
def list_evidence_files(deposit_id):
    """
    List all evidence files for a specific deposit with their status.
    """
    try:
        evidence_service = get_evidence_service()
        
        # Get the deposit transaction to verify access
        deposit = DepositTransaction.query.get_or_404(deposit_id)
        
        # Check if user has permission to view evidence for this deposit
        if session['user_id'] not in [deposit.landlord_id, deposit.tenant_id]:
            return jsonify({'error': 'Unauthorized to view evidence for this deposit'}), 403
        
        # Get all claims for this deposit
        claims = DepositClaim.query.filter_by(deposit_id=deposit_id).all()
        
        evidence_files = {}
        
        for claim in claims:
            claim_items = DepositClaimItem.query.filter_by(claim_id=claim.id).all()
            
            for item in claim_items:
                item_evidence = {
                    'photos': [],
                    'documents': []
                }
                
                # Process photos
                if item.evidence_photos:
                    for index, photo_path in enumerate(item.evidence_photos):
                        file_info = evidence_service.get_file_info(photo_path)
                        evidence_id = f"{item.id}_photo_{index}"
                        
                        item_evidence['photos'].append({
                            'evidence_id': evidence_id,
                            'file_path': photo_path,
                            'file_info': file_info,
                            'download_url': f'/api/deposits/{deposit_id}/evidence/{evidence_id}?download=true',
                            'view_url': f'/api/deposits/{deposit_id}/evidence/{evidence_id}?download=false'
                        })
                
                # Process documents
                if item.evidence_documents:
                    for index, doc_path in enumerate(item.evidence_documents):
                        file_info = evidence_service.get_file_info(doc_path)
                        evidence_id = f"{item.id}_document_{index}"
                        
                        item_evidence['documents'].append({
                            'evidence_id': evidence_id,
                            'file_path': doc_path,
                            'file_info': file_info,
                            'download_url': f'/api/deposits/{deposit_id}/evidence/{evidence_id}?download=true',
                            'view_url': f'/api/deposits/{deposit_id}/evidence/{evidence_id}?download=false'
                        })
                
                evidence_files[f'claim_item_{item.id}'] = item_evidence
        
        return jsonify({
            'deposit_id': deposit_id,
            'evidence_files': evidence_files
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error listing evidence files: {str(e)}")
        return jsonify({'error': 'Internal server error while listing evidence files'}), 500


@deposit_evidence_bp.errorhandler(413)
def handle_file_too_large(e):
    """Handle file too large errors."""
    evidence_service = get_evidence_service()
    return jsonify({
        'error': f'File too large. Maximum size is {evidence_service.MAX_FILE_SIZE // (1024*1024)}MB'
    }), 413


@deposit_evidence_bp.errorhandler(404)
def handle_not_found(e):
    """Handle not found errors."""
    return jsonify({'error': 'Resource not found'}), 404

