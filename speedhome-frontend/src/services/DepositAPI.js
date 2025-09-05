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
}

export default DepositAPI;

