import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TenancyAgreementAPI from '../services/TenancyAgreementAPI';

const PaymentSuccessPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [agreement, setAgreement] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAgreement();
  }, [id]);

  const loadAgreement = async () => {
    try {
      const result = await TenancyAgreementAPI.getById(id);
      
      if (result.success) {
        setAgreement(result.agreement);
      }
    } catch (error) {
      console.error('Error loading agreement:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadFinalAgreement = async () => {
    try {
      const result = await TenancyAgreementAPI.downloadFinalPDF(id);
      
      if (result.success) {
        // Create download link
        const link = document.createElement('a');
        link.href = result.download_url;
        link.download = `Tenancy_Agreement_${agreement.property_address.replace(/\s+/g, '_')}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      console.error('Error downloading agreement:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading agreement details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
            <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🎉 Payment Successful!</h1>
          <p className="text-xl text-gray-600">Website fee paid! Next step: Pay your security deposit to activate the agreement.</p>
        </div>

        {/* Progress Indicator - Website Fee Paid, Deposit Next */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-8 h-8 bg-green-500 text-white rounded-full text-sm font-medium">
                ✓
              </div>
              <span className="ml-2 text-sm font-medium text-green-600">Agreement Signed</span>
            </div>
            
            <div className="flex-1 mx-4">
              <div className="h-1 bg-green-500 rounded"></div>
            </div>
            
            <div className="flex items-center">
              <div className="flex items-center justify-center w-8 h-8 bg-green-500 text-white rounded-full text-sm font-medium">
                ✓
              </div>
              <span className="ml-2 text-sm font-medium text-green-600">Website Fee Paid</span>
            </div>
            
            <div className="flex-1 mx-4">
              <div className="h-1 bg-gray-300 rounded"></div>
            </div>
            
            <div className="flex items-center">
              <div className="flex items-center justify-center w-8 h-8 bg-yellow-500 text-white rounded-full text-sm font-medium">
                2
              </div>
              <span className="ml-2 text-sm font-medium text-yellow-600">Pay Security Deposit</span>
            </div>
          </div>
        </div>

        {/* Success Details */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Agreement Details */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Agreement Details</h3>
              
              {agreement && (
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Property Address</p>
                    <p className="font-medium">{agreement.property_address}</p>
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
                  
                  <div>
                    <p className="text-sm text-gray-600">Agreement Status</p>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                      Website Fee Paid
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Next Steps */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">What's Next?</h3>
              
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-6 w-6 rounded-full bg-yellow-500 text-white text-sm font-medium">
                      1
                    </div>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">Pay Security Deposit</p>
                    <p className="text-sm text-gray-600">Complete your security deposit payment to activate your tenancy agreement.</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-6 w-6 rounded-full bg-gray-300 text-gray-600 text-sm font-medium">
                      2
                    </div>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Download Your Agreement</p>
                    <p className="text-sm text-gray-400">Available after deposit payment is complete.</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-6 w-6 rounded-full bg-gray-300 text-gray-600 text-sm font-medium">
                      3
                    </div>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Prepare for Move-in</p>
                    <p className="text-sm text-gray-400">Contact your landlord after agreement is fully active.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => navigate(`/deposit-payment/${id}`)}
            className="bg-orange-600 text-white px-6 py-3 rounded-md hover:bg-orange-700 focus:ring-2 focus:ring-orange-500 flex items-center justify-center"
          >
            <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Pay Security Deposit (RM {agreement?.security_deposit || '0'})
          </button>
          
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-gray-600 text-white px-6 py-3 rounded-md hover:bg-gray-700 focus:ring-2 focus:ring-gray-500"
          >
            Return to Dashboard
          </button>
          
          <button
            onClick={() => navigate(`/agreement/${id}`)}
            className="border border-gray-300 text-gray-700 px-6 py-3 rounded-md hover:bg-gray-50 focus:ring-2 focus:ring-blue-500"
          >
            View Agreement Details
          </button>
        </div>

        {/* Contact Information */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600">
            Need help? Contact our support team at{' '}
            <a href="mailto:support@speedhome.com" className="text-blue-600 hover:text-blue-500">
              support@speedhome.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentSuccessPage;

