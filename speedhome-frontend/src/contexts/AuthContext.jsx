import React, { createContext, useContext, useState, useEffect } from 'react';
import authAPI from '../services/AuthAPI';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize authentication state
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      // Check if user is stored in localStorage
      const storedUser = authAPI.getCurrentUserFromStorage();
      const isStoredAuth = authAPI.isAuthenticated();
      
      if (storedUser && isStoredAuth) {
        // Set initial state from localStorage immediately
        setUser(storedUser);
        setIsAuthenticated(true);
        
        // Then verify session with backend
        try {
          const sessionResult = await authAPI.checkSession();
          
          if (sessionResult.success && sessionResult.authenticated) {
            // Update with fresh user data from server
            setUser(sessionResult.user);
            setIsAuthenticated(true);
          } else {
            // Session expired, clear local storage
            localStorage.removeItem('speedhome_user');
            localStorage.removeItem('speedhome_authenticated');
            setUser(null);
            setIsAuthenticated(false);
          }
        } catch (sessionError) {
          console.error('Session check failed, keeping localStorage data:', sessionError);
          // Keep localStorage data if session check fails (offline mode)
          setUser(storedUser);
          setIsAuthenticated(true);
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      const result = await authAPI.login(credentials);
      
      if (result.success) {
        setUser(result.user);
        setIsAuthenticated(true);
        return { success: true, user: result.user };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  const register = async (userData) => {
    try {
      const result = await authAPI.register(userData);
      
      if (result.success) {
        setUser(result.user);
        setIsAuthenticated(true);
        
        // Return full registration result including KYC setup info
        return { 
          success: true, 
          user: result.user,
          setupRequired: result.setupRequired || false,
          setupMessage: result.setupMessage,
          nextSteps: result.nextSteps,
          kycEndpoint: result.kycEndpoint,
          setupPriority: result.setupPriority
        };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  const checkKYCStatus = async () => {
    try {
      const response = await fetch('/api/auth/kyc-status', {
        credentials: 'include'
      });
      const data = await response.json();
      return data.success ? data : { success: false, error: 'Failed to check KYC status' };
    } catch (error) {
      console.error('KYC status check error:', error);
      return { success: false, error: 'Network error' };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
      setIsAuthenticated(false);
      
      // Redirect to home page after logout
      window.location.href = '/';
      
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear state even if API call fails
      setUser(null);
      setIsAuthenticated(false);
      return { success: true };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const result = await authAPI.updateProfile(profileData);
      
      if (result.success) {
        setUser(result.profile);
        return { success: true, profile: result.profile };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  const refreshUser = async () => {
    try {
      const result = await authAPI.getCurrentUser();
      
      if (result.success) {
        setUser(result.user);
        setIsAuthenticated(true);
        return { success: true, user: result.user };
      } else {
        setUser(null);
        setIsAuthenticated(false);
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Refresh user error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  // Helper functions
  const isLandlord = () => {
    return user && user.role === 'landlord';
  };

  const isTenant = () => {
    return user && user.role === 'tenant';
  };

  const getUserFullName = () => {
    if (!user) return '';
    return user.full_name || user.username || '';
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      const result = await authAPI.changePassword(currentPassword, newPassword);
      
      if (result.success) {
        return { success: true };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Password change error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  const deleteAccount = async () => {
    try {
      const result = await authAPI.deleteAccount();
      
      if (result.success) {
        // Clear authentication state
        setUser(null);
        setIsAuthenticated(false);
        localStorage.removeItem('speedhome_user');
        localStorage.removeItem('speedhome_authenticated');
        return { success: true };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Account deletion error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  const requestPasswordReset = async (email) => {
    try {
      const result = await authAPI.forgotPassword(email);
      return result;
    } catch (error) {
      console.error('Password reset request error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  const resetPassword = async (token, newPassword) => {
    try {
      const result = await authAPI.resetPassword(token, newPassword);
      return result;
    } catch (error) {
      console.error('Password reset error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  const verifyEmail = async (token) => {
    try {
      const result = await authAPI.verifyEmail(token);
      
      if (result.success && result.user) {
        // Update user data if verification was successful
        setUser(result.user);
        localStorage.setItem('speedhome_user', JSON.stringify(result.user));
      }
      
      return result;
    } catch (error) {
      console.error('Email verification error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  const requestEmailVerification = async (email) => {
    try {
      const result = await authAPI.requestEmailVerification(email);
      return result;
    } catch (error) {
      console.error('Email verification request error:', error);
      return { success: false, error: 'An unexpected error occurred' };
    }
  };

  const value = {
    // State
    user,
    isAuthenticated,
    isLoading,
    
    // Actions
    login,
    register,
    logout,
    updateProfile,
    refreshUser,
    changePassword,
    deleteAccount,
    requestPasswordReset,
    resetPassword,
    verifyEmail,
    requestEmailVerification,
    checkKYCStatus,
    
    // Helper functions
    isLandlord,
    isTenant,
    getUserFullName
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

