import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const AccountSettings = () => {
  const { user, changePassword, deleteAccount, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('password');
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
          <p className="text-gray-600">Please log in to access account settings.</p>
        </div>
      </div>
    );
  }

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage('New passwords do not match.');
      setLoading(false);
      return;
    }

    if (passwordData.newPassword.length < 8) {
      setMessage('New password must be at least 8 characters long.');
      setLoading(false);
      return;
    }

    try {
      await changePassword(passwordData.currentPassword, passwordData.newPassword);
      setMessage('Password changed successfully!');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (error) {
      setMessage('Failed to change password. Please check your current password.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setLoading(true);
    try {
      await deleteAccount();
      // User will be logged out and redirected
    } catch (error) {
      setMessage('Failed to delete account. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Account Settings</h1>
            <p className="text-gray-600">Manage your account security and preferences</p>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('password')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'password'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Change Password
              </button>
              <button
                onClick={() => setActiveTab('security')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'security'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Security
              </button>
              <button
                onClick={() => setActiveTab('danger')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'danger'
                    ? 'border-red-500 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Danger Zone
              </button>
            </nav>
          </div>

          {/* Message */}
          {message && (
            <div className={`px-6 py-3 ${message.includes('success') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
              {message}
            </div>
          )}

          {/* Tab Content */}
          <div className="px-6 py-6">
            {activeTab === 'password' && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
                <form onSubmit={handlePasswordSubmit} className="max-w-md">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Current Password
                      </label>
                      <input
                        type="password"
                        name="currentPassword"
                        value={passwordData.currentPassword}
                        onChange={handlePasswordChange}
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        New Password
                      </label>
                      <input
                        type="password"
                        name="newPassword"
                        value={passwordData.newPassword}
                        onChange={handlePasswordChange}
                        required
                        minLength={8}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Confirm New Password
                      </label>
                      <input
                        type="password"
                        name="confirmPassword"
                        value={passwordData.confirmPassword}
                        onChange={handlePasswordChange}
                        required
                        minLength={8}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={loading}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                    >
                      {loading ? 'Changing...' : 'Change Password'}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Security Settings</h3>
                <div className="space-y-6">
                  <div className="bg-gray-50 p-4 rounded-md">
                    <h4 className="font-medium text-gray-900 mb-2">Email Verification</h4>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">
                          Your email address is {user?.emailVerified ? 'verified' : 'not verified'}
                        </p>
                      </div>
                      <div>
                        {user?.emailVerified ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Verified
                          </span>
                        ) : (
                          <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                            Verify Email
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-md">
                    <h4 className="font-medium text-gray-900 mb-2">Two-Factor Authentication</h4>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">
                          Add an extra layer of security to your account
                        </p>
                      </div>
                      <div>
                        <button className="bg-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-400">
                          Enable 2FA
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-md">
                    <h4 className="font-medium text-gray-900 mb-2">Login History</h4>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">
                          View your recent login activity
                        </p>
                      </div>
                      <div>
                        <button className="bg-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-400">
                          View History
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'danger' && (
              <div>
                <h3 className="text-lg font-medium text-red-900 mb-4">Danger Zone</h3>
                <div className="border border-red-200 rounded-md p-4">
                  <h4 className="font-medium text-red-900 mb-2">Delete Account</h4>
                  <p className="text-sm text-red-700 mb-4">
                    Once you delete your account, there is no going back. Please be certain.
                    All your properties, bookings, and data will be permanently deleted.
                  </p>
                  
                  {!showDeleteConfirm ? (
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                    >
                      Delete Account
                    </button>
                  ) : (
                    <div className="space-y-3">
                      <p className="text-sm font-medium text-red-900">
                        Are you absolutely sure? This action cannot be undone.
                      </p>
                      <div className="flex space-x-3">
                        <button
                          onClick={() => setShowDeleteConfirm(false)}
                          className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={handleDeleteAccount}
                          disabled={loading}
                          className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors disabled:opacity-50"
                        >
                          {loading ? 'Deleting...' : 'Yes, Delete My Account'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountSettings;

