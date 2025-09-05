import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TenancyAgreementAPI from '../services/TenancyAgreementAPI';

const DepositPaymentSuccessPage = () => {
  const { agreementId } = useParams();
  const navigate = useNavigate();
  const [agreement, setAgreement] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAgreement();
  }, [agreementId]);

  const loadAgreement = async () => {
    try {
      const result = await TenancyAgreementAPI.getById(agreementId);
      
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
      const result = await TenancyAgreementAPI.downloadFinalPDF(agreementId);
      
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading agreement details...</p>
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

  const depositAmount = parseFloat(agreement.monthly_rent) * 2.5;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🎉 Deposit Payment Successful!</h1>
          <p className="text-gray-600">Your tenancy agreement is now fully active and ready!</p>
        </div>

        {/* Progress Indicator */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-10 h-10 bg-green-500 text-white rounded-full">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <span className="ml-3 text-sm font-medium text-green-600">Agreement Signed</span>
            </div>
            
            <div className="flex-1 h-1 bg-green-500 mx-4"></div>
            
            <div className="flex items-center">
              <div className="flex items-center justify-center w-10 h-10 bg-green-500 text-white rounded-full">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <span className="ml-3 text-sm font-medium text-green-600">Website Fee Paid</span>
            </div>
            
            <div className="flex-1 h-1 bg-green-500 mx-4"></div>
            
            <div className="flex items-center">
              <div className="flex items-center justify-center w-10 h-10 bg-green-500 text-white rounded-full">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <span className="ml-3 text-sm font-medium text-green-600">Deposit Paid - Complete!</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Agreement Details */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Agreement Details</h2>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Property Address</span>
                <span className="font-medium">{agreement.property_address}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Lease Period</span>
                <span className="font-medium">{agreement.lease_start_date} - {agreement.lease_end_date}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Monthly Rent</span>
                <span className="font-medium">RM {agreement.monthly_rent}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Security Deposit</span>
                <span className="font-medium">RM {depositAmount.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between items-center pt-3 border-t">
                <span className="text-gray-600">Agreement Status</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active
                </span>
              </div>
            </div>
          </div>

          {/* What's Next */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">What's Next?</h2>
            
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full text-sm font-medium mr-3 mt-0.5">
                  1
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Download Your Agreement</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Keep a copy of your signed tenancy agreement for your records.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full text-sm font-medium mr-3 mt-0.5">
                  2
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Prepare for Move-in</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Contact your landlord to arrange key collection and move-in details.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full text-sm font-medium mr-3 mt-0.5">
                  3
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Set Up Utilities</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Arrange for electricity, water, internet, and other utilities as needed.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mt-8 justify-center">
          <button
            onClick={downloadFinalAgreement}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center justify-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Download Agreement
          </button>
          
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium"
          >
            Return to Dashboard
          </button>
          
          <button
            onClick={() => navigate(`/agreements/${agreementId}`)}
            className="border border-gray-300 hover:bg-gray-50 text-gray-700 px-6 py-3 rounded-lg font-medium"
          >
            View Agreement Details
          </button>
        </div>

        {/* Support */}
        <div className="text-center mt-8">
          <p className="text-gray-600">
            Need help? Contact our support team at{' '}
            <a href="mailto:support@speedhome.com" className="text-blue-600 hover:underline">
              support@speedhome.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default DepositPaymentSuccessPage;

