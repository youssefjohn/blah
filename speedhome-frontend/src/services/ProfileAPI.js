// In: src/services/ProfileAPI.js

// Using the config file we created
import { API_BASE_URL } from './config';

const ProfileAPI = {
  getProfile: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/profile`, {
        method: 'GET',
        headers: {
          // 'Authorization' header is NOT needed for session auth
        },
        credentials: 'include', // 👈 This is the crucial line for session cookies
      });
      return response.json();
    } catch (error) {
      console.error('Error fetching profile:', error);
      return { success: false, error: error.message };
    }
  },

  updateProfile: async (profileData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          // 'Authorization' header is NOT needed for session auth
        },
        body: JSON.stringify(profileData),
        credentials: 'include', // 👈 Also needed here for the update request
      });
      return response.json();
    } catch (error) {
      console.error('Error updating profile:', error);
      return { success: false, error: error.message };
    }
  },
};

export default ProfileAPI;