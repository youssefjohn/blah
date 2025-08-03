import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import TenancyAgreementAPI from '../services/TenancyAgreementAPI';

const AgreementView = () => {
  const { agreementId } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated, isLandlord, isTenant } = useAuth();
  const [agreement, setAgreement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showSignatureModal, setShowSignatureModal] = useState(false);
  const [signing, setSigning] = useState(false);

  useEffect(() => {
    loadAgreement();
  }, [agreementId]);

  const loadAgreement = async () => {
    try {
      setLoading(true);
      // Add cache-busting parameter to ensure fresh data
      const response = await TenancyAgreementAPI.getById(agreementId, { 
        _t: Date.now() // Cache-busting timestamp
      });
      if (response.success) {
        setAgreement(response.agreement);
        console.log('Agreement loaded:', response.agreement.status, 'Payment completed:', response.agreement.payment_completed_at);
      } else {
        setError(response.error || 'Failed to load agreement');
      }
    } catch (err) {
      setError('Failed to load agreement');
      console.error('Error loading agreement:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSign = async () => {
    try {
      setSigning(true);
      // For now, we'll simulate signing - in Phase 5 we'll integrate with SignWell
      const response = await TenancyAgreementAPI.signAgreement(agreementId, {
        signature_id: `temp_signature_${Date.now()}`,
        signed_at: new Date().toISOString()
      });
      
      if (response.success) {
        setShowSignatureModal(false);
        await loadAgreement(); // Reload to show updated status
        alert('Agreement signed successfully!');
      } else {
        alert(response.error || 'Failed to sign agreement');
      }
    } catch (err) {
      console.error('Error signing agreement:', err);
      alert('Failed to sign agreement');
    } finally {
      setSigning(false);
    }
  };

  const downloadPDF = (type = 'draft') => {
    const url = `http://localhost:5001/api/tenancy-agreements/${agreementId}/download/${type}`;
    window.open(url, '_blank');
  };

  const previewAgreement = () => {
    const url = `http://localhost:5001/api/tenancy-agreements/${agreementId}/preview`;
    window.open(url, '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-600">Loading agreement...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Agreement</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!agreement) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">📄</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Agreement Not Found</h2>
          <p className="text-gray-600 mb-4">The requested agreement could not be found.</p>
          <button
            onClick={() => navigate(-1)}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const userIsLandlord = isLandlord();
  const userIsTenant = isTenant();
  const landlordSigned = agreement.landlord_signed_at;
  const tenantSigned = agreement.tenant_signed_at;
  const canSign = (userIsLandlord && !landlordSigned) || (userIsTenant && !tenantSigned);
  const allSigned = landlordSigned && tenantSigned;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <button
                onClick={() => navigate(-1)}
                className="mr-4 text-gray-500 hover:text-gray-700"
              >
                ← Back
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Tenancy Agreement</h1>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
                TenancyAgreementAPI.getStatusColor(agreement.status)
              }`}>
                {TenancyAgreementAPI.formatStatus(agreement.status)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Agreement Details */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Agreement Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Agreement ID</span>
                  <p className="text-gray-900">{agreement.id}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Created Date</span>
                  <p className="text-gray-900">{new Date(agreement.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Lease Duration</span>
                  <p className="text-gray-900">{agreement.lease_duration_months} months</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Agreement Fee</span>
                  <p className="text-gray-900">RM {agreement.payment_required}</p>
                </div>
              </div>
            </div>

            {/* Property Details */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Property Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <span className="text-sm font-medium text-gray-500">Address</span>
                  <p className="text-gray-900">{agreement.property_address}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Property Type</span>
                  <p className="text-gray-900">{agreement.property_type}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Bedrooms</span>
                  <p className="text-gray-900">{agreement.property_bedrooms}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Bathrooms</span>
                  <p className="text-gray-900">{agreement.property_bathrooms}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Floor Area</span>
                  <p className="text-gray-900">{agreement.property_sqft} sq ft</p>
                </div>
              </div>
            </div>

            {/* Financial Terms */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Financial Terms</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <span className="text-sm font-medium text-blue-600">Monthly Rent</span>
                  <p className="text-2xl font-bold text-blue-900">RM {agreement.monthly_rent}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <span className="text-sm font-medium text-green-600">Security Deposit</span>
                  <p className="text-2xl font-bold text-green-900">RM {agreement.security_deposit}</p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg text-center">
                  <span className="text-sm font-medium text-yellow-600">Agreement Fee</span>
                  <p className="text-2xl font-bold text-yellow-900">RM {agreement.payment_required}</p>
                </div>
              </div>
            </div>

            {/* Lease Terms */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Lease Terms</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Lease Start Date</span>
                  <p className="text-gray-900">{new Date(agreement.lease_start_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Lease End Date</span>
                  <p className="text-gray-900">{new Date(agreement.lease_end_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Utilities Included</span>
                  <p className="text-gray-900">{agreement.utilities_included ? 'Yes' : 'No'}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Parking Included</span>
                  <p className="text-gray-900">{agreement.parking_included ? 'Yes' : 'No'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Signature Status */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Signature Status</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Landlord</p>
                    <p className="text-sm text-gray-600">{agreement.landlord_full_name}</p>
                  </div>
                  <div className="text-right">
                    {landlordSigned ? (
                      <div>
                        <span className="text-green-600 font-medium">✓ Signed</span>
                        <p className="text-xs text-gray-500">
                          {new Date(agreement.landlord_signed_at).toLocaleDateString()}
                        </p>
                      </div>
                    ) : (
                      <span className="text-yellow-600 font-medium">⏳ Pending</span>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Tenant</p>
                    <p className="text-sm text-gray-600">{agreement.tenant_full_name}</p>
                  </div>
                  <div className="text-right">
                    {tenantSigned ? (
                      <div>
                        <span className="text-green-600 font-medium">✓ Signed</span>
                        <p className="text-xs text-gray-500">
                          {new Date(agreement.tenant_signed_at).toLocaleDateString()}
                        </p>
                      </div>
                    ) : (
                      <span className="text-yellow-600 font-medium">⏳ Pending</span>
                    )}
                  </div>
                </div>
              </div>

              {allSigned && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800 font-medium text-center">
                    🎉 All parties have signed!
                  </p>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Actions</h3>
              
              <div className="space-y-3">
                <button
                  onClick={previewAgreement}
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium"
                >
                  📄 Preview Agreement
                </button>
                
                <button
                  onClick={() => downloadPDF('draft')}
                  className="w-full bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-md text-sm font-medium"
                >
                  📥 Download Draft PDF
                </button>

                {allSigned && (
                  <button
                    onClick={() => downloadPDF('final')}
                    className="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md text-sm font-medium"
                  >
                    📥 Download Final PDF
                  </button>
                )}

                {canSign && (
                  <button
                    onClick={() => setShowSignatureModal(true)}
                    className="w-full bg-orange-500 hover:bg-orange-600 text-white py-2 px-4 rounded-md text-sm font-medium"
                  >
                    ✍️ Sign Agreement
                  </button>
                )}
              </div>
            </div>

            {/* Next Steps */}
            {!allSigned && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 className="font-medium text-yellow-800 mb-2">Next Steps</h4>
                <div className="text-sm text-yellow-700">
                  {!landlordSigned && !tenantSigned && (
                    <p>Both landlord and tenant need to review and sign this agreement.</p>
                  )}
                  {landlordSigned && !tenantSigned && (
                    <p>Waiting for tenant to sign the agreement.</p>
                  )}
                  {!landlordSigned && tenantSigned && (
                    <p>Waiting for landlord to sign the agreement.</p>
                  )}
                  <p className="mt-2">Once both parties sign, the tenant will be prompted for payment to activate the tenancy.</p>
                </div>
              </div>
            )}

            {/* Payment Section */}
            {agreement.status === 'pending_payment' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-800 mb-2">🎉 Agreement Signed!</h4>
                
                {/* Tenant View - Show Payment Button */}
                {userIsTenant && (
                  <>
                    <p className="text-sm text-blue-700 mb-4">
                      Both parties have signed the agreement. Complete the payment to finalize your tenancy.
                    </p>
                    <Link
                      to={`/agreement/${agreement.id}/payment`}
                      className="inline-flex items-center bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm font-medium"
                    >
                      <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3 3v8a3 3 0 003 3z" />
                      </svg>
                      Complete Payment (RM {agreement.payment_required})
                    </Link>
                  </>
                )}
                
                {/* Landlord View - Show Waiting Message */}
                {userIsLandlord && (
                  <div className="flex items-center">
                    <svg className="h-5 w-5 text-blue-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <p className="text-sm text-blue-700 font-medium">Waiting for tenant payment</p>
                      <p className="text-xs text-blue-600 mt-1">
                        The tenant needs to complete the RM {agreement.payment_required} agreement fee to activate the tenancy.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Active Agreement */}
            {agreement.status === 'active' && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium text-green-800 mb-2">✅ Agreement Active</h4>
                <p className="text-sm text-green-700">
                  Your tenancy agreement is now active and in effect. Welcome to your new home!
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Signature Modal */}
      {showSignatureModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Sign Agreement</h3>
            <p className="text-gray-600 mb-6">
              By signing this agreement, you confirm that you have read, understood, and agree to all terms and conditions.
            </p>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowSignatureModal(false)}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-md"
                disabled={signing}
              >
                Cancel
              </button>
              <button
                onClick={handleSign}
                disabled={signing}
                className="flex-1 bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md disabled:opacity-50"
              >
                {signing ? 'Signing...' : 'Confirm & Sign'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgreementView;

