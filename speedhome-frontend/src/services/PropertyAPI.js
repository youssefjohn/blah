// API service for property operations
const API_BASE_URL = 'http://localhost:5001/api';

class PropertyAPI {
  // Get all properties with optional filters
  static async getProperties(filters = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      // Add filters to query parameters
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          queryParams.append(key, filters[key]);
        }
      });
      
      const url = `${API_BASE_URL}/properties${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching properties:', error);
      throw error;
    }
  }

  // Get a specific property by ID
  static async getProperty(id) {
    try {
      const response = await fetch(`${API_BASE_URL}/properties/${id}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching property:', error);
      throw error;
    }
  }

  // Create a new property
  static async createProperty(propertyData) {
    try {
      const response = await fetch(`${API_BASE_URL}/properties`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session authentication
        body: JSON.stringify(propertyData)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error creating property:', error);
      throw error;
    }
  }

  // Update an existing property
  static async updateProperty(id, propertyData) {
    try {
      const response = await fetch(`${API_BASE_URL}/properties/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session authentication
        body: JSON.stringify(propertyData)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error updating property:', error);
      throw error;
    }
  }

  // Delete a property
  static async deleteProperty(id) {
    try {
      const response = await fetch(`${API_BASE_URL}/properties/${id}`, {
        method: 'DELETE',
        credentials: 'include' // Include cookies for session authentication
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error deleting property:', error);
      throw error;
    }
  }

  // Record an inquiry for a property
  static async inquireProperty(id) {
    try {
      const response = await fetch(`${API_BASE_URL}/properties/${id}/inquire`, {
        method: 'POST',
        credentials: 'include' // Include cookies for session authentication
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error recording inquiry:', error);
      throw error;
    }
  }

  // Get properties by owner (for landlord dashboard)
  static async getPropertiesByOwner(ownerId) {
    try {
      const response = await fetch(`${API_BASE_URL}/properties/owner/${ownerId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching properties by owner:', error);
      return { success: false, error: 'Failed to fetch properties' };
    }
  }

  // Search properties with advanced filters
  static async searchProperties(searchParams = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      // Add search parameters
      Object.keys(searchParams).forEach(key => {
        if (searchParams[key] !== undefined && searchParams[key] !== null && searchParams[key] !== '') {
          queryParams.append(key, searchParams[key]);
        }
      });
      
      const url = `${API_BASE_URL}/properties/search${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error searching properties:', error);
      throw error;
    }
  }

  // Get property statistics
  static async getPropertyStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/properties/stats`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching property stats:', error);
      throw error;
    }
  }

  // Migrate localStorage data to API (one-time migration)
  static async migrateLocalStorageData() {
    try {
      const localProperties = JSON.parse(localStorage.getItem('speedhome_properties') || '[]');
      
      if (localProperties.length === 0) {
        console.log('No local properties to migrate');
        return { success: true, migrated: 0 };
      }

      console.log(`Migrating ${localProperties.length} properties from localStorage to API...`);
      
      const migrationResults = [];
      
      for (const property of localProperties) {
        try {
          // Remove the id field as it will be auto-generated by the database
          const { id, ...propertyData } = property;
          
          const result = await this.createProperty(propertyData);
          migrationResults.push({ success: true, property: result.property });
          console.log(`Migrated property: ${property.title}`);
        } catch (error) {
          console.error(`Failed to migrate property: ${property.title}`, error);
          migrationResults.push({ success: false, error: error.message, property });
        }
      }
      
      const successCount = migrationResults.filter(r => r.success).length;
      const failureCount = migrationResults.filter(r => !r.success).length;
      
      console.log(`Migration completed: ${successCount} successful, ${failureCount} failed`);
      
      // Clear localStorage after successful migration
      if (successCount > 0) {
        localStorage.removeItem('speedhome_properties');
        console.log('Cleared localStorage after migration');
      }
      
      return {
        success: true,
        migrated: successCount,
        failed: failureCount,
        results: migrationResults
      };
    } catch (error) {
      console.error('Error during migration:', error);
      throw error;
    }
  }
  // Get properties for tenant favorites (includes Active and Rented properties)
  static async getPropertiesForFavorites(filters = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      // Add filters to query parameters
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          queryParams.append(key, filters[key]);
        }
      });
      
      const url = `${API_BASE_URL}/properties/favorites${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching properties for favorites:', error);
      throw error;
    }
  }

  // Add recurring availability for a property
  static async addRecurringAvailability(propertyId, scheduleData) {
    try {
      const response = await fetch(`${API_BASE_URL}/properties/${propertyId}/recurring-availability`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session authentication
        body: JSON.stringify(scheduleData)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error adding recurring availability:', error);
      throw error;
    }
  }

  // Add recurring availability for a landlord (landlord-based, not property-specific)
  static async addLandlordRecurringAvailability(landlordId, scheduleData) {
    try {
      const response = await fetch(`${API_BASE_URL}/landlord/${landlordId}/recurring-availability`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session authentication
        body: JSON.stringify(scheduleData)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error adding landlord recurring availability:', error);
      throw error;
    }
  }

  static async getAvailableSlots(propertyId) {
    try {
        const response = await fetch(`${API_BASE_URL}/properties/${propertyId}/available-slots`);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.slots; // Return the array of slots

    } catch (error) {
        console.error('Error fetching available slots:', error);
        throw error;
    }
  }
  // Get all viewing slots for a landlord across all properties
  static async getLandlordViewingSlots(landlordId) {
    try {
      const response = await fetch(`${API_BASE_URL}/landlord/${landlordId}/viewing-slots`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching landlord viewing slots:', error);
      throw error;
    }
  }

  // Get calendar statistics for a landlord
  static async getLandlordCalendarStats(landlordId) {
    try {
      const response = await fetch(`${API_BASE_URL}/landlord/${landlordId}/calendar-stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching landlord calendar stats:', error);
      throw error;
    }
  }

  // Get viewing slots for a landlord on a specific date
  static async getLandlordSlotsByDate(landlordId, date) {
    try {
      const response = await fetch(`${API_BASE_URL}/landlord/${landlordId}/calendar-slots/${date}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching landlord slots by date:', error);
      throw error;
    }
  }

}

export default PropertyAPI;


  



