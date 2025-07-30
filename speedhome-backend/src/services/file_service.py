import os
import uuid
import magic
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app


class FileService:
    """Service for handling file uploads and management."""
    
    ALLOWED_EXTENSIONS = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    DOCUMENT_TYPES = [
        'id_document',
        'income_proof',
        'employment_letter',
        'bank_statement',
        'reference_letter',
        'credit_check'
    ]
    
    def __init__(self):
        self.upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'applications')
        self.ensure_upload_directory()
    
    def ensure_upload_directory(self):
        """Ensure the upload directory exists."""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder, exist_ok=True)
    
    def validate_file(self, file, document_type):
        """
        Validate uploaded file for type, size, and document type.
        
        Args:
            file: Werkzeug FileStorage object
            document_type: Type of document being uploaded
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"
        
        if not file.filename:
            return False, "No filename provided"
        
        if document_type not in self.DOCUMENT_TYPES:
            return False, f"Invalid document type: {document_type}"
        
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
        
        # Validate MIME type using python-magic
        try:
            file_content = file.read(1024)  # Read first 1KB for MIME detection
            file.seek(0)  # Reset file pointer
            
            detected_mime = magic.from_buffer(file_content, mime=True)
            expected_mime = self.ALLOWED_EXTENSIONS[extension]
            
            if detected_mime != expected_mime:
                return False, f"File content doesn't match extension. Expected {expected_mime}, got {detected_mime}"
        
        except Exception as e:
            current_app.logger.warning(f"MIME type validation failed: {str(e)}")
            # Continue without MIME validation if magic fails
        
        return True, None
    
    def generate_filename(self, original_filename, document_type, application_id):
        """
        Generate a secure, unique filename for the uploaded document.
        
        Args:
            original_filename: Original filename from upload
            document_type: Type of document
            application_id: ID of the application
            
        Returns:
            str: Generated filename
        """
        # Get file extension
        secure_name = secure_filename(original_filename)
        extension = secure_name.rsplit('.', 1)[1].lower() if '.' in secure_name else 'bin'
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        filename = f"{document_type}_{application_id}_{timestamp}_{unique_id}.{extension}"
        return filename
    
    def get_application_folder(self, application_id):
        """Get the folder path for a specific application."""
        app_folder = os.path.join(self.upload_folder, str(application_id))
        if not os.path.exists(app_folder):
            os.makedirs(app_folder, exist_ok=True)
        return app_folder
    
    def save_file(self, file, document_type, application_id):
        """
        Save uploaded file to the file system.
        
        Args:
            file: Werkzeug FileStorage object
            document_type: Type of document
            application_id: ID of the application
            
        Returns:
            tuple: (success, file_path_or_error)
        """
        try:
            # Validate file
            is_valid, error_message = self.validate_file(file, document_type)
            if not is_valid:
                return False, error_message
            
            # Generate filename and path
            filename = self.generate_filename(file.filename, document_type, application_id)
            app_folder = self.get_application_folder(application_id)
            file_path = os.path.join(app_folder, filename)
            
            # Save file
            file.save(file_path)
            
            # Return relative path for database storage
            relative_path = os.path.join('uploads', 'applications', str(application_id), filename)
            
            current_app.logger.info(f"File saved successfully: {relative_path}")
            return True, relative_path
            
        except Exception as e:
            current_app.logger.error(f"Error saving file: {str(e)}")
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
                current_app.logger.info(f"File deleted successfully: {file_path}")
            
            return True, None
            
        except Exception as e:
            current_app.logger.error(f"Error deleting file: {str(e)}")
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
            current_app.logger.error(f"Error getting file info: {str(e)}")
            return None
    
    def cleanup_application_files(self, application_id):
        """
        Clean up all files for a specific application.
        
        Args:
            application_id: ID of the application
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            app_folder = os.path.join(self.upload_folder, str(application_id))
            
            if os.path.exists(app_folder):
                import shutil
                shutil.rmtree(app_folder)
                current_app.logger.info(f"Application files cleaned up: {application_id}")
            
            return True, None
            
        except Exception as e:
            current_app.logger.error(f"Error cleaning up application files: {str(e)}")
            return False, f"Failed to cleanup files: {str(e)}"

