const API_BASE_URL = 'http://localhost:5001/api/tenancy-agreements/';

class TenancyAgreementAPI {
  /**
   * Get all tenancy agreements for the current user
   */
  static async getAll() {
    try {
      const response = await fetch(API_BASE_URL, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching agreements:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Get a specific tenancy agreement by ID
   */
  static async getById(agreementId, options = {}) {
    try {
      // Add cache-busting parameter if provided
      const url = new URL(`${API_BASE_URL}${agreementId}`);
      if (options._t) {
        url.searchParams.append('_t', options._t);
      }
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching agreement:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Create a tenancy agreement from an application
   */
  static async createFromApplication(applicationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/create-from-application`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ application_id: applicationId }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error creating agreement:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Sign a tenancy agreement
   */
  static async signAgreement(agreementId) {
    try {
      const response = await fetch(`${API_BASE_URL}${agreementId}/sign`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error signing agreement:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Record payment for a tenancy agreement
   */
  static async recordPayment(agreementId, paymentData) {
    try {
      const response = await fetch(`${API_BASE_URL}/${agreementId}/payment`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(paymentData),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error recording payment:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Get agreement status
   */
  static async getStatus(agreementId) {
    try {
      const response = await fetch(`${API_BASE_URL}/${agreementId}/status`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting status:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Download draft PDF
   */
  static async downloadDraftPDF(agreementId) {
    try {
      const response = await fetch(`${API_BASE_URL}/${agreementId}/download-draft`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        return { success: true, download_url: url };
      } else {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.error('Error downloading draft PDF:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Download final PDF
   */
  static async downloadFinalPDF(agreementId) {
    try {
      const response = await fetch(`${API_BASE_URL}/${agreementId}/download-final`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        return { success: true, download_url: url };
      } else {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.error('Error downloading final PDF:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Preview agreement as HTML
   */
  static async previewHTML(agreementId) {
    try {
      const response = await fetch(`${API_BASE_URL}/${agreementId}/preview`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const html = await response.text();
        return { success: true, html };
      } else {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.error('Error previewing agreement:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Regenerate PDF
   */
  static async regeneratePDF(agreementId) {
    try {
      const response = await fetch(`${API_BASE_URL}/${agreementId}/regenerate-pdf`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error regenerating PDF:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Helper method to get status color
   */
  static getStatusColor(status) {
    switch (status) {
      case 'pending_signatures':
        return 'text-yellow-600 bg-yellow-100';
      case 'pending_payment':
        return 'text-blue-600 bg-blue-100';
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'cancelled':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }

  /**
   * Helper method to format status text
   */
  static formatStatus(status) {
    switch (status) {
      case 'pending_signatures':
        return 'Pending Signatures';
      case 'pending_payment':
        return 'Pending Payment';
      case 'active':
        return 'Active';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  /**
   * Helper method to check if agreement is fully signed
   */
  static isFullySigned(agreement) {
    return agreement.landlord_signed_at && agreement.tenant_signed_at;
  }

  /**
   * Initiate signing process for an agreement
   */
  static async initiateSigning(agreementId) {
    try {
      const response = await fetch(`${API_BASE_URL}/${agreementId}/initiate-signing`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error initiating signing:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Initiate payment process for an agreement
   */
  static async initiatePayment(agreementId) {
    try {
      const response = await fetch(`${API_BASE_URL}/${agreementId}/initiate-payment`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error initiating payment:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Cancel an agreement
   */
  static async cancelAgreement(agreementId, reason) {
    try {
      const response = await fetch(`${API_BASE_URL}/${agreementId}/cancel`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error cancelling agreement:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

   /**
   * Get service status
   */
  static async getServiceStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/service-status`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting service status:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }

  /**
   * Get tenant agreements (for tenant dashboard)
   */
  static async getTenantAgreements() {
    try {
      const response = await fetch(`${API_BASE_URL}tenant`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching tenant agreements:', error);
      return { success: false, error: 'Network error occurred' };
    }
  }
}

export default TenancyAgreementAPI;

