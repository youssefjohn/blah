import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import TenancyAgreementAPI from '../services/TenancyAgreementAPI';
import PaymentForm from '../components/PaymentForm';

const DepositPaymentPage = () => {
  const { agreementId } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated, isTenant } = useAuth();
  
  const [agreement, setAgreement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState('pending'); // pending, processing, success, error

  useEffect(() => {
    if (!isAuthenticated || !isTenant()) {
      navigate('/');
      return;
    }
    loadAgreement();
  }, [isAuthenticated, isTenant, agreementId]);

  const loadAgreement = async () => {
    try {
      const result = await TenancyAgreementAPI.getById(agreementId);
      if (result.success) {
        setAgreement(result.agreement);
        
        // Check if agreement is in correct status for deposit payment
        if (result.agreement.status !== 'website_fee_paid') {
          setError('This agreement is not ready for deposit payment');
        }
      } else {
        setError(result.error || 'Agreement not found');
      }
    } catch (error) {
      console.error('Error loading agreement:', error);
      setError('Error loading agreement details');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentSuccess = async (paymentIntent) => {
    setPaymentStatus('success');
    
    try {
      // Record the deposit payment completion in our backend
      const paymentData = {
        payment_intent_id: paymentIntent.id,
        payment_method: paymentIntent.payment_method,
        amount: paymentIntent.amount,
        currency: paymentIntent.currency,
        status: paymentIntent.status
      };

      const result = await TenancyAgreementAPI.completeDepositPayment(agreementId, paymentData);

      if (result.success) {
        // Navigate to success page
        navigate(`/deposit/payment/${agreementId}/success`);
      } else {
        setError('Failed to record payment completion');
        setPaymentStatus('error');
      }
    } catch (error) {
      console.error('Error completing deposit payment:', error);
      setError('Failed to complete payment process');
      setPaymentStatus('error');
    }
  };

  const handlePaymentError = (error) => {
    console.error('Deposit payment error:', error);
    setError(error.message || 'Payment failed');
    setPaymentStatus('error');
  };

  const calculateDepositAmount = () => {
    if (!agreement) return 0;
    const monthlyRent = parseFloat(agreement.monthly_rent) || 0;
    return monthlyRent * 2.5; // 2 months security + 0.5 month utility
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading deposit payment details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!agreement) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Agreement not found</p>
        </div>
      </div>
    );
  }

  const depositAmount = calculateDepositAmount();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">💰 Security Deposit Payment</h1>
              <p className="text-gray-600 mt-1">Complete your security deposit to activate your tenancy agreement</p>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-500 hover:text-gray-700"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Payment Summary */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Payment Summary</h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Property Address</span>
                <span className="font-medium">{agreement.property_address}</span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Monthly Rent</span>
                <span className="font-medium">RM {agreement.monthly_rent}</span>
              </div>
              
              <div className="border-t pt-4">
                <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
                  <span className="text-orange-700 font-medium">Security Deposit (2 months)</span>
                  <span className="font-bold text-orange-900">RM {(parseFloat(agreement.monthly_rent) * 2).toFixed(2)}</span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg mt-2">
                  <span className="text-orange-700 font-medium">Utility Deposit (0.5 month)</span>
                  <span className="font-bold text-orange-900">RM {(parseFloat(agreement.monthly_rent) * 0.5).toFixed(2)}</span>
                </div>
                
                <div className="flex justify-between items-center p-4 bg-orange-100 rounded-lg mt-4 border-2 border-orange-200">
                  <span className="text-orange-800 font-bold text-lg">Total Deposit</span>
                  <span className="font-bold text-2xl text-orange-900">RM {depositAmount.toFixed(2)}</span>
                </div>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-blue-700">
                  🔒 <strong>Secure Escrow:</strong> Your deposit will be held in a secure escrow account and returned at the end of your tenancy, subject to property condition.
                </p>
              </div>
            </div>
          </div>

          {/* Payment Form */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Payment Details</h2>
            
            {paymentStatus === 'pending' && (
              <PaymentForm
                agreement={{
                  ...agreement,
                  payment_required: depositAmount.toFixed(2),
                  payment_type: 'deposit'
                }}
                onPaymentSuccess={handlePaymentSuccess}
                onPaymentError={handlePaymentError}
              />
            )}
            
            {paymentStatus === 'processing' && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Processing your deposit payment...</p>
              </div>
            )}
            
            {paymentStatus === 'error' && (
              <div className="text-center py-8">
                <p className="text-red-600 mb-4">{error}</p>
                <button
                  onClick={() => {
                    setPaymentStatus('pending');
                    setError(null);
                  }}
                  className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-md"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DepositPaymentPage;

