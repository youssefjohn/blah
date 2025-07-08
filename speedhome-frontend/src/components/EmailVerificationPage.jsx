import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const EmailVerificationPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { verifyEmail, user } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [token, setToken] = useState('');

  useEffect(() => {
    const tokenParam = searchParams.get('token');
    if (!tokenParam) {
      setMessage('Invalid or missing verification token.');
      setLoading(false);
      return;
    }
    setToken(tokenParam);
    handleVerification(tokenParam);
  }, [searchParams]);

  const handleVerification = async (verificationToken) => {
    try {
      const result = await verifyEmail(verificationToken);
      
      if (result.success) {
        setIsSuccess(true);
        setMessage('Your email has been verified successfully!');
      } else {
        setMessage(result.error || 'Failed to verify email. The link may be expired or invalid.');
      }
    } catch (error) {
      setMessage('An unexpected error occurred during verification.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    if (!user?.email) {
      setMessage('No email address found. Please log in and try again.');
      return;
    }

    try {
      setLoading(true);
      const result = await requestEmailVerification(user.email);
      
      if (result.success) {
        setMessage('A new verification email has been sent to your email address.');
      } else {
        setMessage(result.error || 'Failed to send verification email.');
      }
    } catch (error) {
      setMessage('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verifying your email...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          {isSuccess ? (
            <div>
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-3xl font-extrabold text-gray-900 mb-2">
                Email Verified!
              </h2>
              <p className="text-gray-600 mb-6">{message}</p>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Go to Dashboard
                </button>
                <button
                  onClick={() => navigate('/')}
                  className="w-full bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
                >
                  Back to Home
                </button>
              </div>
            </div>
          ) : (
            <div>
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h2 className="text-3xl font-extrabold text-gray-900 mb-2">
                Verification Failed
              </h2>
              <p className="text-gray-600 mb-6">{message}</p>
              <div className="space-y-3">
                {user && (
                  <button
                    onClick={handleResendVerification}
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                  >
                    {loading ? 'Sending...' : 'Resend Verification Email'}
                  </button>
                )}
                <button
                  onClick={() => navigate('/')}
                  className="w-full bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
                >
                  Back to Home
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="text-center">
          <p className="text-sm text-gray-500">
            Need help? <a href="/contact" className="text-blue-600 hover:text-blue-500">Contact Support</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationPage;

