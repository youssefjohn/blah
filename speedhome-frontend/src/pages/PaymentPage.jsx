import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PaymentForm from '../components/PaymentForm';
import TenancyAgreementAPI from '../services/TenancyAgreementAPI';

const PaymentPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [agreement, setAgreement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState('pending'); // pending, processing, success, error

  useEffect(() => {
    loadAgreement();
  }, [id]);

  const loadAgreement = async () => {
    try {
      const result = await TenancyAgreementAPI.getById(id);
      
      if (result.success) {
        setAgreement(result.agreement);
        
        // Check if agreement is in correct status for payment
        if (result.agreement.status !== 'pending_payment') {
          setError('This agreement is not ready for payment');
        }
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Failed to load agreement details');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentSuccess = (paymentIntent) => {
    setPaymentStatus('success');
    
    // Redirect to success page after a short delay
    setTimeout(() => {
      navigate(`/agreement/${id}/payment-success`);
    }, 2000);
  };

  const handlePaymentError = (errorMessage) => {
    setPaymentStatus('error');
    setError(errorMessage);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading payment details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Payment Error</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'success') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Payment Successful!</h3>
            <p className="text-gray-600 mb-4">
              Your payment has been processed successfully. Redirecting to confirmation page...
            </p>
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(`/agreement/${id}`)}
            className="flex items-center text-blue-600 hover:text-blue-500 mb-4"
          >
            <svg className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Agreement
          </button>
          
          <h1 className="text-3xl font-bold text-gray-900">Complete Payment</h1>
          <p className="text-gray-600 mt-2">
            Finalize your tenancy agreement by completing the payment process
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-8 h-8 bg-green-500 text-white rounded-full text-sm font-medium">
                ✓
              </div>
              <span className="ml-2 text-sm font-medium text-green-600">Agreement Signed</span>
            </div>
            
            <div className="flex-1 mx-4">
              <div className="h-1 bg-gray-200 rounded">
                <div className="h-1 bg-blue-500 rounded" style={{ width: '50%' }}></div>
              </div>
            </div>
            
            <div className="flex items-center">
              <div className="flex items-center justify-center w-8 h-8 bg-blue-500 text-white rounded-full text-sm font-medium">
                2
              </div>
              <span className="ml-2 text-sm font-medium text-blue-600">Payment</span>
            </div>
            
            <div className="flex-1 mx-4">
              <div className="h-1 bg-gray-200 rounded"></div>
            </div>
            
            <div className="flex items-center">
              <div className="flex items-center justify-center w-8 h-8 bg-gray-300 text-gray-600 rounded-full text-sm font-medium">
                3
              </div>
              <span className="ml-2 text-sm font-medium text-gray-500">Complete</span>
            </div>
          </div>
        </div>

        {/* Payment Form */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Agreement Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6 sticky top-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Agreement Summary</h3>
              
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Property</p>
                  <p className="font-medium">{agreement.property_address}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Tenant</p>
                  <p className="font-medium">{agreement.tenant_full_name}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Landlord</p>
                  <p className="font-medium">{agreement.landlord_full_name}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Lease Period</p>
                  <p className="font-medium">
                    {new Date(agreement.lease_start_date).toLocaleDateString()} - {' '}
                    {new Date(agreement.lease_end_date).toLocaleDateString()}
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Monthly Rent</p>
                  <p className="font-medium">RM {agreement.monthly_rent}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Security Deposit</p>
                  <p className="font-medium">RM {agreement.security_deposit}</p>
                </div>
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold text-gray-900">Agreement Fee</span>
                  <span className="text-lg font-bold text-blue-600">RM {agreement.agreement_fee}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">One-time processing fee</p>
              </div>
            </div>
          </div>

          {/* Payment Form */}
          <div className="lg:col-span-2">
            <PaymentForm
              agreement={agreement}
              onPaymentSuccess={handlePaymentSuccess}
              onPaymentError={handlePaymentError}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;

