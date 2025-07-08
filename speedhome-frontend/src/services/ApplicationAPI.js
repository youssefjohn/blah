// src/services/ApplicationAPI.js

const API_BASE_URL = 'http://localhost:5001/api';

class ApplicationAPI {
  // Method for landlords to get their applications
  static async getApplicationsByLandlord() {
    try {
      const response = await fetch(`${API_BASE_URL}/applications/landlord`, {
        credentials: 'include',
      });
      return await response.json();
    } catch (error) {
      console.error('Error fetching landlord applications:', error);
      return { success: false, error: error.message };
    }
  }

  // Method for tenants to get their own applications
  static async getApplicationsByTenant() {
    try {
      const response = await fetch(`${API_BASE_URL}/applications/tenant`, {
        credentials: 'include',
      });
      return await response.json();
    } catch (error) {
      console.error('Error fetching tenant applications:', error);
      return { success: false, error: error.message };
    }
  }

  // Method for landlords to update an application status
  static async updateApplicationStatus(applicationId, status) {
    try {
      const response = await fetch(`${API_BASE_URL}/applications/${applicationId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ status }),
      });
      return await response.json();
    } catch (error) {
      console.error('Error updating application status:', error);
      return { success: false, error: error.message };
    }
  }

  // Method for tenants to create an application
  static async createApplication(applicationData) {
    try {
      const response = await fetch(`${API_BASE_URL}/applications/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(applicationData),
      });
      return await response.json();
    } catch (error) {
      console.error('Error creating application:', error);
      return { success: false, error: error.message };
    }
  }

  // Method to check if a user has already applied for a specific property
  static async hasApplied(propertyId) {
    try {
      const response = await fetch(`${API_BASE_URL}/applications/status?property_id=${propertyId}`, {
        credentials: 'include',
      });
      return await response.json();
    } catch (error) {
      console.error('Error checking application status:', error);
      return { success: false, error: error.message };
    }
  }

  // --- NEW: Method for tenants to withdraw an application ---
  static async withdrawApplication(applicationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/applications/${applicationId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      return await response.json();
    } catch (error) {
      console.error('Error withdrawing application:', error);
      return { success: false, error: error.message };
    }
  }
}

export default ApplicationAPI;
