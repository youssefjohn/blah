import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001';

class DocumentAPI {
  /**
   * Upload a document for an application
   * @param {number} applicationId - The application ID
   * @param {string} documentType - Type of document (id_document, income_proof, etc.)
   * @param {File} file - The file to upload
   * @param {function} onProgress - Progress callback function
   * @returns {Promise} Upload response
   */
  static async uploadDocument(applicationId, documentType, file, onProgress = null) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);

      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
      };

      // Add progress tracking if callback provided
      if (onProgress) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        };
      }

      const response = await axios.post(
        `${API_BASE_URL}/upload/documents/${applicationId}`,
        formData,
        config
      );

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Document upload error:', error);
      
      let errorMessage = 'Failed to upload document';
      
      if (error.response) {
        // Server responded with error status
        errorMessage = error.response.data?.error || errorMessage;
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'Network error - please check your connection';
      }

      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  /**
   * Delete a document for an application
   * @param {number} applicationId - The application ID
   * @param {string} documentType - Type of document to delete
   * @returns {Promise} Delete response
   */
  static async deleteDocument(applicationId, documentType) {
    try {
      const response = await axios.delete(
        `${API_BASE_URL}/upload/documents/${applicationId}/${documentType}`,
        {
          withCredentials: true,
        }
      );

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Document delete error:', error);
      
      let errorMessage = 'Failed to delete document';
      
      if (error.response) {
        errorMessage = error.response.data?.error || errorMessage;
      }

      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  /**
   * Get list of all documents for an application
   * @param {number} applicationId - The application ID
   * @returns {Promise} Documents list response
   */
  static async getDocuments(applicationId) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/upload/documents/${applicationId}`,
        {
          withCredentials: true,
        }
      );

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get documents error:', error);
      
      let errorMessage = 'Failed to fetch documents';
      
      if (error.response) {
        errorMessage = error.response.data?.error || errorMessage;
      }

      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  /**
   * Get download URL for a document
   * @param {number} applicationId - The application ID
   * @param {string} documentType - Type of document
   * @param {boolean} download - Whether to download or view inline
   * @returns {string} Document URL
   */
  static getDocumentUrl(applicationId, documentType, download = false) {
    const downloadParam = download ? '?download=true' : '?download=false';
    return `${API_BASE_URL}/upload/documents/${applicationId}/${documentType}${downloadParam}`;
  }

  /**
   * Preview a document (for viewing without downloading)
   * @param {number} applicationId - The application ID
   * @param {string} documentType - Type of document
   * @returns {string} Preview URL
   */
  static getPreviewUrl(applicationId, documentType) {
    return this.getDocumentUrl(applicationId, documentType, false);
  }

  /**
   * Download a document
   * @param {number} applicationId - The application ID
   * @param {string} documentType - Type of document
   * @returns {string} Download URL
   */
  static getDownloadUrl(applicationId, documentType) {
    return this.getDocumentUrl(applicationId, documentType, true);
  }

  /**
   * Validate file before upload
   * @param {File} file - The file to validate
   * @returns {object} Validation result
   */
  static validateFile(file) {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!file) {
      return { valid: false, error: 'No file selected' };
    }

    if (!allowedTypes.includes(file.type)) {
      return { 
        valid: false, 
        error: 'Invalid file type. Please upload PDF, JPG, or PNG files only.' 
      };
    }

    if (file.size > maxSize) {
      return { 
        valid: false, 
        error: 'File size too large. Maximum size is 5MB.' 
      };
    }

    if (file.size === 0) {
      return { 
        valid: false, 
        error: 'File is empty.' 
      };
    }

    return { valid: true };
  }

  /**
   * Format file size for display
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted file size
   */
  static formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Get document type display name
   * @param {string} documentType - Document type key
   * @returns {string} Display name
   */
  static getDocumentDisplayName(documentType) {
    const displayNames = {
      'id_document': 'ID Document',
      'income_proof': 'Income Proof',
      'employment_letter': 'Employment Letter',
      'bank_statement': 'Bank Statement',
      'reference_letter': 'Reference Letter'
    };

    return displayNames[documentType] || documentType;
  }

  /**
   * Check if document type is required
   * @param {string} documentType - Document type key
   * @returns {boolean} Whether document is required
   */
  static isDocumentRequired(documentType) {
    const requiredDocuments = ['id_document', 'income_proof'];
    return requiredDocuments.includes(documentType);
  }
}

export default DocumentAPI;

