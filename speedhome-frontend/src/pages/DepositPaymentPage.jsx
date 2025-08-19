import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import TenancyAgreementAPI from '../services/TenancyAgreementAPI';
import DepositAPI from '../services/DepositAPI';

const DepositPaymentPage = () => {
  const { agreementId } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated, isTenant } = useAuth();
  
  const [agreement, setAgreement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('credit_card');
  const [paymentData, setPaymentData] = useState({
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    cardholderName: '',
    email: '',
    phone: ''
  });

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
        setPaymentData(prev => ({
          ...prev,
          email: user?.email || '',
          cardholderName: `${user?.first_name || ''} ${user?.last_name || ''}`.trim()
        }));
      } else {
        alert('Agreement not found');
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Error loading agreement:', error);
      alert('Error loading agreement details');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const calculateDepositAmount = () => {
    if (!agreement) return 0;
    const monthlyRent = parseFloat(agreement.monthly_rent) || 0;
    return monthlyRent * 2.5; // 2 months security + 0.5 month utility
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPaymentData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProcessing(true);

    try {
      // Call the backend API to process deposit payment
      const response = await fetch(`/api/deposit-payment/process/${agreementId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          payment_method: paymentMethod,
          payment_data: paymentData
        })
      });

      const result = await response.json();

      if (result.success) {
        alert(`Deposit payment successful!\n\nAmount: RM ${calculateDepositAmount().toFixed(2)}\nPayment Method: ${paymentMethod}\n\n✅ Your tenancy agreement is now ACTIVE!\n🏠 Your security deposit is held in escrow.`);
        
        // Navigate back to dashboard
        navigate('/dashboard');
      } else {
        alert(`Payment failed: ${result.error}`);
      }
      
    } catch (error) {
      console.error('Error processing deposit payment:', error);
      alert('Payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading payment details...</p>
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
              <h1 className="text-2xl font-bold text-gray-900">Security Deposit Payment</h1>
              <p className="text-gray-600 mt-1">Complete your tenancy setup</p>
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
          {/* Payment Form */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-6">Payment Information</h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Payment Method Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Payment Method
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setPaymentMethod('credit_card')}
                    className={`p-3 border rounded-lg text-center ${
                      paymentMethod === 'credit_card'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    💳 Credit Card
                  </button>
                  <button
                    type="button"
                    onClick={() => setPaymentMethod('online_banking')}
                    className={`p-3 border rounded-lg text-center ${
                      paymentMethod === 'online_banking'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    🏦 Online Banking
                  </button>
                </div>
              </div>

              {/* Credit Card Fields */}
              {paymentMethod === 'credit_card' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Cardholder Name
                    </label>
                    <input
                      type="text"
                      name="cardholderName"
                      value={paymentData.cardholderName}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Card Number
                    </label>
                    <input
                      type="text"
                      name="cardNumber"
                      value={paymentData.cardNumber}
                      onChange={handleInputChange}
                      placeholder="1234 5678 9012 3456"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Expiry Date
                      </label>
                      <input
                        type="text"
                        name="expiryDate"
                        value={paymentData.expiryDate}
                        onChange={handleInputChange}
                        placeholder="MM/YY"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        CVV
                      </label>
                      <input
                        type="text"
                        name="cvv"
                        value={paymentData.cvv}
                        onChange={handleInputChange}
                        placeholder="123"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                  </div>
                </>
              )}

              {/* Contact Information */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={paymentData.email}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={paymentData.phone}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={processing}
                className={`w-full py-3 px-4 rounded-lg font-semibold ${
                  processing
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                } text-white transition-colors`}
              >
                {processing ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Processing Payment...
                  </div>
                ) : (
                  `Pay Security Deposit ${DepositAPI.formatMYR(depositAmount)}`
                )}
              </button>
            </form>
          </div>

          {/* Payment Summary */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-6">Payment Summary</h2>
            
            {/* Property Information */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-gray-900 mb-2">Property Details</h3>
              <p className="text-gray-600 text-sm mb-1">
                {agreement.property?.title || 'Property Title'}
              </p>
              <p className="text-gray-600 text-sm mb-2">
                {agreement.property?.address || 'Property Address'}
              </p>
              <p className="text-gray-900 font-semibold">
                Monthly Rent: {DepositAPI.formatMYR(agreement.monthly_rent || 0)}
              </p>
            </div>

            {/* Deposit Breakdown */}
            <div className="space-y-3 mb-6">
              <h3 className="font-semibold text-gray-900">Deposit Breakdown</h3>
              
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Security Deposit (2 months)</span>
                <span className="font-medium">
                  {DepositAPI.formatMYR((agreement.monthly_rent || 0) * 2)}
                </span>
              </div>
              
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Utility Deposit (0.5 month)</span>
                <span className="font-medium">
                  {DepositAPI.formatMYR((agreement.monthly_rent || 0) * 0.5)}
                </span>
              </div>
              
              <div className="border-t pt-3">
                <div className="flex justify-between">
                  <span className="font-semibold text-gray-900">Total Deposit</span>
                  <span className="font-bold text-lg text-blue-600">
                    {DepositAPI.formatMYR(depositAmount)}
                  </span>
                </div>
              </div>
            </div>

            {/* Security Information */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start">
                <div className="text-green-600 mr-3">🔒</div>
                <div>
                  <h4 className="font-semibold text-green-800 mb-1">Secure Escrow</h4>
                  <p className="text-green-700 text-sm">
                    Your deposit will be held securely in escrow and protected according to Malaysian tenancy laws.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DepositPaymentPage;

