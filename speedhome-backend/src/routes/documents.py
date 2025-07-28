from flask import Blueprint, request, jsonify, send_file, current_app, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from functools import wraps
import os

documents_bp = Blueprint('documents', __name__)

def require_auth(f):
    """Custom authentication decorator that uses session-based auth instead of Flask-Login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

from ..models.application import Application, db
from ..services.file_service import FileService


def get_file_service():
    """Get FileService instance within application context."""
    return FileService()


@documents_bp.route('/upload/documents/<int:application_id>', methods=['POST'])
@require_auth
def upload_document(application_id):
    """
    Upload a document for a specific application.
    
    Expected form data:
    - file: The file to upload
    - document_type: Type of document (id_document, income_proof, etc.)
    """
    try:
        file_service = get_file_service()
        
        # Get the application
        application = Application.query.get_or_404(application_id)
        
        # Check if user has permission to upload documents for this application
        if session['user_id'] != application.tenant_id:
            return jsonify({'error': 'Unauthorized to upload documents for this application'}), 403
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        document_type = request.form.get('document_type')
        
        if not document_type:
            return jsonify({'error': 'Document type is required'}), 400
        
        # Validate document type
        if document_type not in file_service.DOCUMENT_TYPES:
            return jsonify({'error': f'Invalid document type. Allowed types: {", ".join(file_service.DOCUMENT_TYPES)}'}), 400
        
        # Delete existing file if it exists
        existing_path = getattr(application, f'{document_type}_path')
        if existing_path:
            file_service.delete_file(existing_path)
        
        # Save the new file
        success, result = file_service.save_file(file, document_type, application_id)
        
        if not success:
            return jsonify({'error': result}), 400
        
        # Update the application with the new file path
        setattr(application, f'{document_type}_path', result)
        
        # Update the database
        try:
            db.session.commit()
            current_app.logger.info(f"Document uploaded successfully: {document_type} for application {application_id}")
        except Exception as e:
            db.session.rollback()
            # Clean up the uploaded file if database update fails
            file_service.delete_file(result)
            current_app.logger.error(f"Database error during document upload: {str(e)}")
            return jsonify({'error': 'Failed to update application record'}), 500
        
        # Get file info for response
        file_info = file_service.get_file_info(result)
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document_type': document_type,
            'file_path': result,
            'file_info': file_info
        }), 200
        
    except RequestEntityTooLarge:
        return jsonify({'error': f'File too large. Maximum size is {file_service.MAX_FILE_SIZE // (1024*1024)}MB'}), 413
    
    except Exception as e:
        current_app.logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': 'Internal server error during file upload'}), 500


@documents_bp.route('/upload/documents/<int:application_id>/<document_type>', methods=['GET'])
@require_auth
def get_document(application_id, document_type):
    """
    Download or view a document for a specific application.
    """
    try:
        file_service = get_file_service()
        
        # Get the application
        application = Application.query.get_or_404(application_id)
        
        # Check if user has permission to view documents for this application
        # Tenant can view their own documents, landlord can view tenant documents for their properties
        if session['user_id'] != application.tenant_id and session['user_id'] != application.landlord_id:
            return jsonify({'error': 'Unauthorized to view documents for this application'}), 403
        
        # Validate document type
        if document_type not in file_service.DOCUMENT_TYPES:
            return jsonify({'error': f'Invalid document type. Allowed types: {", ".join(file_service.DOCUMENT_TYPES)}'}), 400
        
        # Get the file path from the application
        file_path = getattr(application, f'{document_type}_path')
        
        if not file_path:
            return jsonify({'error': f'No {document_type} uploaded for this application'}), 404
        
        # Convert relative path to absolute path
        abs_path = os.path.join(current_app.root_path, '..', file_path)
        
        if not os.path.exists(abs_path):
            current_app.logger.error(f"File not found on disk: {abs_path}")
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
        current_app.logger.error(f"Error serving document: {str(e)}")
        return jsonify({'error': 'Internal server error while serving file'}), 500


@documents_bp.route('/upload/documents/<int:application_id>/<document_type>', methods=['DELETE'])
@require_auth
def delete_document(application_id, document_type):
    """
    Delete a document for a specific application.
    """
    try:
        file_service = get_file_service()
        
        # Get the application
        application = Application.query.get_or_404(application_id)
        
        # Check if user has permission to delete documents for this application
        if session['user_id'] != application.tenant_id:
            return jsonify({'error': 'Unauthorized to delete documents for this application'}), 403
        
        # Validate document type
        if document_type not in file_service.DOCUMENT_TYPES:
            return jsonify({'error': f'Invalid document type. Allowed types: {", ".join(file_service.DOCUMENT_TYPES)}'}), 400
        
        # Get the file path from the application
        file_path = getattr(application, f'{document_type}_path')
        
        if not file_path:
            return jsonify({'message': f'No {document_type} to delete'}), 200
        
        # Delete the file from the file system
        success, error = file_service.delete_file(file_path)
        
        if not success:
            current_app.logger.error(f"Failed to delete file: {error}")
            # Continue with database update even if file deletion fails
        
        # Update the application record
        setattr(application, f'{document_type}_path', None)
        
        try:
            db.session.commit()
            current_app.logger.info(f"Document deleted successfully: {document_type} for application {application_id}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during document deletion: {str(e)}")
            return jsonify({'error': 'Failed to update application record'}), 500
        
        return jsonify({
            'message': f'{document_type} deleted successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting document: {str(e)}")
        return jsonify({'error': 'Internal server error during file deletion'}), 500


@documents_bp.route('/upload/documents/<int:application_id>', methods=['GET'])
@require_auth
def list_documents(application_id):
    """
    List all documents for a specific application with their status.
    """
    try:
        file_service = get_file_service()
        
        # Get the application
        application = Application.query.get_or_404(application_id)
        
        # Check if user has permission to view documents for this application
        if session['user_id'] != application.tenant_id and session['user_id'] != application.landlord_id:
            return jsonify({'error': 'Unauthorized to view documents for this application'}), 403
        
        documents = {}
        
        for doc_type in file_service.DOCUMENT_TYPES:
            file_path = getattr(application, f'{doc_type}_path')
            
            if file_path:
                file_info = file_service.get_file_info(file_path)
                documents[doc_type] = {
                    'uploaded': True,
                    'file_path': file_path,
                    'file_info': file_info,
                    'download_url': f'/api/applications/{application_id}/documents/{doc_type}',
                    'view_url': f'/api/applications/{application_id}/documents/{doc_type}?download=false'
                }
            else:
                documents[doc_type] = {
                    'uploaded': False,
                    'file_path': None,
                    'file_info': None,
                    'download_url': None,
                    'view_url': None
                }
        
        return jsonify({
            'application_id': application_id,
            'documents': documents
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': 'Internal server error while listing documents'}), 500


@documents_bp.errorhandler(413)
def handle_file_too_large(e):
    """Handle file too large errors."""
    file_service = get_file_service()
    return jsonify({
        'error': f'File too large. Maximum size is {file_service.MAX_FILE_SIZE // (1024*1024)}MB'
    }), 413


@documents_bp.errorhandler(404)
def handle_not_found(e):
    """Handle not found errors."""
    return jsonify({'error': 'Resource not found'}), 404

