// Authentication API service
class AuthAPI {
  constructor() {
    this.baseURL = 'http://localhost:5001/api/auth';
    this.profileURL = 'http://localhost:5001/api';
  }

  async register(userData) {
    try {
      const response = await fetch(`${this.baseURL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(userData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Store user data in localStorage for persistence
        localStorage.setItem('speedhome_user', JSON.stringify(data.user));
        localStorage.setItem('speedhome_authenticated', 'true');
        return { success: true, user: data.user, message: data.message };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async login(credentials) {
    try {
      const response = await fetch(`${this.baseURL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(credentials)
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Store user data in localStorage for persistence
        localStorage.setItem('speedhome_user', JSON.stringify(data.user));
        localStorage.setItem('speedhome_authenticated', 'true');
        return { success: true, user: data.user, message: data.message };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async logout() {
    try {
      const response = await fetch(`${this.baseURL}/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      
      // Clear local storage regardless of response
      localStorage.removeItem('speedhome_user');
      localStorage.removeItem('speedhome_authenticated');
      
      const data = await response.json();
      return { success: true, message: data.message || 'Logged out successfully' };
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local storage on error
      localStorage.removeItem('speedhome_user');
      localStorage.removeItem('speedhome_authenticated');
      return { success: true, message: 'Logged out successfully' };
    }
  }

  async getCurrentUser() {
    try {
      const response = await fetch(`${this.baseURL}/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Update localStorage with fresh user data
        localStorage.setItem('speedhome_user', JSON.stringify(data.user));
        localStorage.setItem('speedhome_authenticated', 'true');
        return { success: true, user: data.user };
      } else {
        // Clear localStorage if session is invalid
        localStorage.removeItem('speedhome_user');
        localStorage.removeItem('speedhome_authenticated');
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Get current user error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async checkSession() {
    try {
      const response = await fetch(`${this.baseURL}/check-session`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      
      const data = await response.json();
      
      if (data.success && data.authenticated) {
        localStorage.setItem('speedhome_user', JSON.stringify(data.user));
        localStorage.setItem('speedhome_authenticated', 'true');
        return { success: true, authenticated: true, user: data.user };
      } else {
        localStorage.removeItem('speedhome_user');
        localStorage.removeItem('speedhome_authenticated');
        return { success: true, authenticated: false };
      }
    } catch (error) {
      console.error('Session check error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async updateProfile(profileData) {
    try {
      const response = await fetch(`${this.profileURL}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(profileData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Update localStorage with new profile data
        localStorage.setItem('speedhome_user', JSON.stringify(data.profile));
        return { success: true, profile: data.profile, message: data.message };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async changePassword(passwordData) {
    try {
      const response = await fetch(`${this.baseURL}/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(passwordData)
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Password change error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async forgotPassword(email) {
    try {
      const response = await fetch(`${this.baseURL}/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Forgot password error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async resetPassword(token, password) {
    try {
      const response = await fetch(`${this.baseURL}/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ token, password })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Reset password error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async verifyEmail(token) {
    try {
      const response = await fetch(`${this.baseURL}/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ token })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Email verification error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async requestEmailVerification(email) {
    try {
      const response = await fetch(`${this.baseURL}/request-email-verification`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Email verification request error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  async deleteAccount() {
    try {
      const response = await fetch(`${this.baseURL}/delete-account`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Clear local storage
        localStorage.removeItem('speedhome_user');
        localStorage.removeItem('speedhome_authenticated');
      }
      
      return data;
    } catch (error) {
      console.error('Account deletion error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  }

  // Helper methods
  isAuthenticated() {
    return localStorage.getItem('speedhome_authenticated') === 'true';
  }

  getCurrentUserFromStorage() {
    const userData = localStorage.getItem('speedhome_user');
    return userData ? JSON.parse(userData) : null;
  }

  getUserRole() {
    const user = this.getCurrentUserFromStorage();
    return user ? user.role : null;
  }

  isLandlord() {
    return this.getUserRole() === 'landlord';
  }

  isTenant() {
    return this.getUserRole() === 'tenant';
  }
}

// Create and export singleton instance
const authAPI = new AuthAPI();
export default authAPI;

