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

  // Enhanced method for tenants to create an application with comprehensive data
  static async createApplication(applicationData) {
    try {
      // Handle file uploads if documents are present
      let processedData = { ...applicationData };
      
      if (applicationData.documents) {
        // In a real implementation, you would upload files to a file storage service
        // For now, we'll simulate this by creating file paths
        const documentPaths = {};
        
        for (const [key, file] of Object.entries(applicationData.documents)) {
          if (file && file instanceof File) {
            // Simulate file upload and get path
            documentPaths[`${key}_path`] = `/uploads/applications/${Date.now()}_${file.name}`;
          }
        }
        
        // Remove the documents object and add the paths
        delete processedData.documents;
        processedData = { ...processedData, ...documentPaths };
      }

      const response = await fetch(`${API_BASE_URL}/applications/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(processedData),
      });
      return await response.json();
    } catch (error) {
      console.error('Error creating application:', error);
      return { success: false, error: error.message };
    }
  }

  // Method to update an existing application (for multi-step form saving)
  static async updateApplication(applicationId, applicationData) {
    try {
      let processedData = { ...applicationData };
      
      if (applicationData.documents) {
        const documentPaths = {};
        
        for (const [key, file] of Object.entries(applicationData.documents)) {
          if (file && file instanceof File) {
            documentPaths[`${key}_path`] = `/uploads/applications/${Date.now()}_${file.name}`;
          }
        }
        
        delete processedData.documents;
        processedData = { ...processedData, ...documentPaths };
      }

      const response = await fetch(`${API_BASE_URL}/applications/${applicationId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(processedData),
      });
      return await response.json();
    } catch (error) {
      console.error('Error updating application:', error);
      return { success: false, error: error.message };
    }
  }

  // Method to get a specific application by ID
  static async getApplicationById(applicationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/applications/${applicationId}`, {
        credentials: 'include',
      });
      return await response.json();
    } catch (error) {
      console.error('Error fetching application:', error);
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

  // Method for tenants to withdraw an application
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

  // Method to mark application as seen by landlord
  static async markAsSeen(applicationId) {
    try {
      const response = await fetch(`/api/applications/${applicationId}/mark-seen`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      const text = await response.text();
      const data = text ? JSON.parse(text) : {};

      if (!response.ok) {
        throw new Error(data.error || 'Failed to mark application as seen');
      }

      return { success: true, data: data };

    } catch (error) {
      console.error('API Error - Failed to mark application as seen:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Method to upload a single document
  static async uploadDocument(file, documentType, applicationId) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);
      formData.append('application_id', applicationId);

      const response = await fetch(`${API_BASE_URL}/applications/upload-document`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      return await response.json();
    } catch (error) {
      console.error('Error uploading document:', error);
      return { success: false, error: error.message };
    }
  }

  // Method to download a document
  static async downloadDocument(documentPath) {
    try {
      const response = await fetch(`${API_BASE_URL}/applications/download-document?path=${encodeURIComponent(documentPath)}`, {
        credentials: 'include',
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = documentPath.split('/').pop();
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        return { success: true };
      } else {
        throw new Error('Failed to download document');
      }
    } catch (error) {
      console.error('Error downloading document:', error);
      return { success: false, error: error.message };
    }
  }

  // Method to validate application completeness
  static validateApplicationCompleteness(applicationData) {
    const errors = {};
    
    // Required personal information
    if (!applicationData.full_name) errors.full_name = 'Full name is required';
    if (!applicationData.phone_number) errors.phone_number = 'Phone number is required';
    if (!applicationData.email) errors.email = 'Email is required';
    if (!applicationData.date_of_birth) errors.date_of_birth = 'Date of birth is required';
    
    // Required employment information
    if (!applicationData.employment_status) errors.employment_status = 'Employment status is required';
    if (!applicationData.monthly_income) errors.monthly_income = 'Monthly income is required';
    
    // Required financial information
    if (!applicationData.bank_name) errors.bank_name = 'Bank name is required';
    
    // Required documents
    if (!applicationData.id_document_path && !applicationData.documents?.id_document) {
      errors.id_document = 'ID document is required';
    }
    if (!applicationData.income_proof_path && !applicationData.documents?.income_proof) {
      errors.income_proof = 'Income proof is required';
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }

  // Method to calculate financial metrics
  static calculateFinancialMetrics(applicationData, propertyRent) {
    const monthlyIncome = parseFloat(applicationData.monthly_income || 0);
    const additionalIncome = parseFloat(applicationData.additional_income || 0);
    const totalIncome = monthlyIncome + additionalIncome;
    const rent = parseFloat(propertyRent || 0);
    
    let rentToIncomeRatio = null;
    let riskLevel = 'Unknown';
    
    if (totalIncome > 0 && rent > 0) {
      rentToIncomeRatio = ((rent / totalIncome) * 100).toFixed(2);
      
      if (rentToIncomeRatio <= 30) {
        riskLevel = 'Low Risk';
      } else if (rentToIncomeRatio <= 40) {
        riskLevel = 'Medium Risk';
      } else {
        riskLevel = 'High Risk';
      }
    }
    
    return {
      totalIncome,
      rentToIncomeRatio,
      riskLevel
    };
  }
}

export default ApplicationAPI;
