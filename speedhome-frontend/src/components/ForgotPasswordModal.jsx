import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const ForgotPasswordModal = ({ isOpen, onClose }) => {
  const { requestPasswordReset } = useAuth();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    if (!email) {
      setMessage('Please enter your email address.');
      setLoading(false);
      return;
    }

    try {
      const result = await requestPasswordReset(email);
      
      if (result.success) {
        setIsSuccess(true);
        setMessage('Password reset instructions have been sent to your email address.');
      } else {
        setMessage(result.error || 'Failed to send password reset email.');
      }
    } catch (error) {
      setMessage('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setEmail('');
    setMessage('');
    setIsSuccess(false);
    setLoading(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            {isSuccess ? 'Check Your Email' : 'Reset Password'}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {!isSuccess ? (
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <p className="text-gray-600 mb-4">
                Enter your email address and we'll send you instructions to reset your password.
              </p>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your email"
                required
              />
            </div>

            {message && (
              <div className={`mb-4 p-3 rounded ${
                message.includes('error') || message.includes('Failed')
                  ? 'bg-red-50 text-red-800'
                  : 'bg-blue-50 text-blue-800'
              }`}>
                {message}
              </div>
            )}

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </div>
          </form>
        ) : (
          <div>
            <div className="text-center mb-4">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-gray-600 mb-4">
                {message}
              </p>
              <p className="text-sm text-gray-500">
                If you don't see the email in your inbox, please check your spam folder.
              </p>
            </div>

            <button
              onClick={handleClose}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ForgotPasswordModal;

