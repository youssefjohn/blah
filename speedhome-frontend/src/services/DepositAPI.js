/**
 * Deposit API Service for SpeedHome Frontend
 * Handles deposit-related API calls
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

class DepositAPI {
  /**
   * Get tenant's deposit dashboard data
   */
  static async getTenantDepositDashboard() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tenant/deposits/dashboard`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching tenant deposit dashboard:', error);
      throw error;
    }
  }

  /**
   * Get deposit information for a specific tenancy agreement
   */
  static async getDepositForAgreement(agreementId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tenant/deposits/agreement/${agreementId}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching deposit for agreement:', error);
      throw error;
    }
  }

  /**
   * Get detailed status of a specific deposit
   */
  static async getDepositStatus(depositId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tenant/deposits/${depositId}/status`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching deposit status:', error);
      throw error;
    }
  }

  /**
   * Format currency amount in Malaysian Ringgit
   */
  static formatMYR(amount) {
    return new Intl.NumberFormat('en-MY', {
      style: 'currency',
      currency: 'MYR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  /**
   * Get deposit status color for UI
   */
  static getDepositStatusColor(status) {
    switch (status) {
      case 'held_in_escrow':
        return 'bg-blue-100 text-blue-800';
      case 'pending_release':
        return 'bg-yellow-100 text-yellow-800';
      case 'partially_released':
        return 'bg-orange-100 text-orange-800';
      case 'fully_released':
        return 'bg-green-100 text-green-800';
      case 'disputed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }

  /**
   * Get deposit status display text
   */
  static getDepositStatusText(status) {
    switch (status) {
      case 'held_in_escrow':
        return 'Held in Escrow';
      case 'pending_release':
        return 'Pending Release';
      case 'partially_released':
        return 'Partially Released';
      case 'fully_released':
        return 'Fully Released';
      case 'disputed':
        return 'Under Dispute';
      default:
        return status || 'Unknown';
    }
  }

  /**
   * Upload evidence file for a deposit claim item (temporary storage)
   * @param {number} depositId - The deposit ID
   * @param {string} claimItemId - The frontend claim item ID
   * @param {string} evidenceType - Type of evidence (photo or document)
   * @param {File} file - The file to upload
   * @param {function} onProgress - Progress callback function
   * @returns {Promise} Upload response
   */
  static async uploadEvidenceFile(depositId, claimItemId, evidenceType, file, onProgress = null) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('evidence_type', evidenceType);
      formData.append('claim_item_id', claimItemId);

      const config = {
        method: 'POST',
        credentials: 'include',
        body: formData
      };

      // For progress tracking, we'll use XMLHttpRequest
      if (onProgress) {
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          
          xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
              const percentCompleted = Math.round((e.loaded * 100) / e.total);
              onProgress(percentCompleted);
            }
          });

          xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const response = JSON.parse(xhr.responseText);
                resolve({ success: true, data: response });
              } catch (e) {
                resolve({ success: true, data: {} });
              }
            } else {
              try {
                const error = JSON.parse(xhr.responseText);
                resolve({ success: false, error: error.error || 'Upload failed' });
              } catch (e) {
                resolve({ success: false, error: 'Upload failed' });
              }
            }
          });

          xhr.addEventListener('error', () => {
            resolve({ success: false, error: 'Network error - please check your connection' });
          });

          xhr.open('POST', `${API_BASE_URL}/api/deposits/${depositId}/evidence/temp`);
          xhr.withCredentials = true;
          xhr.send(formData);
        });
      } else {
        // Use fetch for simple uploads without progress
        const response = await fetch(`${API_BASE_URL}/api/deposits/${depositId}/evidence/temp`, config);
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          return {
            success: false,
            error: errorData.error || 'Failed to upload evidence file'
          };
        }

        const data = await response.json();
        return {
          success: true,
          data: data,
        };
      }
    } catch (error) {
      console.error('Evidence file upload error:', error);
      return {
        success: false,
        error: 'Failed to upload evidence file',
      };
    }
  }

  /**
   * Delete an evidence file for a deposit claim
   * @param {number} depositId - The deposit ID
   * @param {number} evidenceId - The evidence file ID to delete
   * @returns {Promise} Delete response
   */
  static async deleteEvidenceFile(depositId, evidenceId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/deposits/${depositId}/evidence/${evidenceId}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error: errorData.error || 'Failed to delete evidence file'
        };
      }

      const data = await response.json();
      return {
        success: true,
        data: data,
      };
    } catch (error) {
      console.error('Evidence file delete error:', error);
      return {
        success: false,
        error: 'Failed to delete evidence file',
      };
    }
  }

  /**
   * Get list of all evidence files for a deposit
   * @param {number} depositId - The deposit ID
   * @returns {Promise} Evidence files list response
   */
  static async getEvidenceFiles(depositId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/deposits/${depositId}/evidence`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error: errorData.error || 'Failed to fetch evidence files'
        };
      }

      const data = await response.json();
      return {
        success: true,
        data: data,
      };
    } catch (error) {
      console.error('Get evidence files error:', error);
      return {
        success: false,
        error: 'Failed to fetch evidence files',
      };
    }
  }

  /**
   * Get download URL for an evidence file
   * @param {number} depositId - The deposit ID
   * @param {number} evidenceId - The evidence file ID
   * @param {boolean} download - Whether to download or view inline
   * @returns {string} Evidence file URL
   */
  static getEvidenceFileUrl(depositId, evidenceId, download = false) {
    const downloadParam = download ? '?download=true' : '?download=false';
    return `${API_BASE_URL}/api/deposits/${depositId}/evidence/${evidenceId}${downloadParam}`;
  }

  /**
   * Preview an evidence file (for viewing without downloading)
   * @param {number} depositId - The deposit ID
   * @param {number} evidenceId - The evidence file ID
   * @returns {string} Preview URL
   */
  static getPreviewUrl(depositId, evidenceId) {
    return this.getEvidenceFileUrl(depositId, evidenceId, false);
  }

  /**
   * Download an evidence file
   * @param {number} depositId - The deposit ID
   * @param {number} evidenceId - The evidence file ID
   * @returns {string} Download URL
   */
  static getDownloadUrl(depositId, evidenceId) {
    return this.getEvidenceFileUrl(depositId, evidenceId, true);
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
   * Get evidence type display name
   * @param {string} evidenceType - Evidence type key
   * @returns {string} Display name
   */
  static getEvidenceTypeDisplayName(evidenceType) {
    const displayNames = {
      'photo': 'Photo Evidence',
      'document': 'Document Evidence'
    };

    return displayNames[evidenceType] || evidenceType;
  }
}

export default DepositAPI;

