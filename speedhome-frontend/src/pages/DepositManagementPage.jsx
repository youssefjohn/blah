import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DepositManagementPage = () => {
  const { agreementId } = useParams();
  const navigate = useNavigate();
  const { user, isLandlord, isTenant } = useAuth();
  
  const [deposit, setDeposit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showReleaseModal, setShowReleaseModal] = useState(false);
  const [showClaimModal, setShowClaimModal] = useState(false);

  useEffect(() => {
    loadDepositData();
  }, [agreementId]);

  const loadDepositData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/deposits/agreement/${agreementId}`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to load deposit data');
      }
      
      const data = await response.json();
      if (data.success) {
        setDeposit(data.deposit);
      } else {
        setError(data.error || 'Failed to load deposit');
      }
    } catch (err) {
      setError('Failed to load deposit data');
      console.error('Error loading deposit:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFullRelease = async () => {
    try {
      const response = await fetch(`/api/deposits/${deposit.id}/release`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          release_type: 'full',
          amount: deposit.amount
        })
      });

      const result = await response.json();
      if (result.success) {
        setShowReleaseModal(false);
        await loadDepositData();
        alert('Deposit released successfully!');
      } else {
        alert(result.error || 'Failed to release deposit');
      }
    } catch (err) {
      console.error('Error releasing deposit:', err);
      alert('Failed to release deposit');
    }
  };

  const handleMakeClaim = () => {
    navigate(`/deposit/${deposit.id}/claim`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-600">Loading deposit information...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Deposit</h2>
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

  if (!deposit) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">💰</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Deposit Found</h2>
          <p className="text-gray-600 mb-4">No deposit transaction found for this agreement.</p>
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

  const isNearingEnd = deposit.tenancy_ending_soon;
  const hasEnded = deposit.tenancy_has_ended;
  const canRelease = isLandlord() && deposit.status === 'held_in_escrow' && hasEnded; // Only after tenancy ends
  
  // Claims should only be visible to tenants AFTER inspection period expires
  const inspectionActive = deposit.inspection_status?.is_active;
  const canViewClaims = (deposit.status === 'disputed' || deposit.claims?.length > 0) && 
                        (!isTenant() || !inspectionActive); // Hide from tenants during inspection

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
              <h1 className="text-2xl font-bold text-gray-900">Deposit Management</h1>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(deposit.status)}`}>
                {getStatusText(deposit.status)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Deposit Overview */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Deposit Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <span className="text-sm font-medium text-gray-500">Property Address</span>
                  <p className="text-gray-900">{deposit.property_address}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Tenant Name</span>
                  <p className="text-gray-900">{deposit.tenant_name}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Total Deposit Amount</span>
                  <p className="text-2xl font-bold text-green-600">RM {deposit.amount}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Paid On</span>
                  <p className="text-gray-900">{new Date(deposit.paid_at).toLocaleDateString()}</p>
                </div>
              </div>

              {/* Fund Breakdown Section */}
              {deposit.fund_breakdown && (
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Fund Breakdown</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Released to Landlord */}
                    {deposit.fund_breakdown.released_to_landlord > 0 && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <div className="text-sm font-medium text-blue-600 mb-1">
                          Released to {deposit.landlord_name} (Landlord)
                        </div>
                        <div className="text-xl font-bold text-blue-700">
                          RM {deposit.fund_breakdown.released_to_landlord.toFixed(2)}
                        </div>
                        <div className="text-xs text-blue-600 mt-1">Accepted claims</div>
                      </div>
                    )}

                    {/* Refunded to Tenant */}
                    {deposit.fund_breakdown.refunded_to_tenant > 0 && (
                      <div className="bg-green-50 p-4 rounded-lg">
                        <div className="text-sm font-medium text-green-600 mb-1">
                          Refunded to {deposit.tenant_name} (Tenant)
                        </div>
                        <div className="text-xl font-bold text-green-700">
                          RM {deposit.fund_breakdown.refunded_to_tenant.toFixed(2)}
                        </div>
                        <div className="text-xs text-green-600 mt-1">Undisputed balance</div>
                      </div>
                    )}

                    {/* Refunded to Tenant */}
                    {deposit.fund_breakdown.refunded_to_tenant > 0 && (
                      <div className="bg-green-50 p-4 rounded-lg">
                        <div className="text-sm font-medium text-green-600 mb-1">
                          Refunded to {deposit.tenant_name} (Tenant)
                        </div>
                        <div className="text-xl font-bold text-green-700">
                          RM {deposit.fund_breakdown.refunded_to_tenant.toFixed(2)}
                        </div>
                        <div className="text-xs text-green-600 mt-1">
                          {deposit.fund_breakdown.status === 'refunded' ? 'Inspection period ended - No claims' : 'Refunded amount'}
                        </div>
                      </div>
                    )}

                    {/* Remaining in Escrow */}
                    {deposit.fund_breakdown.remaining_in_escrow > 0 && (
                      <div className="bg-yellow-50 p-4 rounded-lg">
                        <div className="text-sm font-medium text-yellow-600 mb-1">Held in Escrow</div>
                        <div className="text-xl font-bold text-yellow-700">
                          RM {deposit.fund_breakdown.remaining_in_escrow.toFixed(2)}
                        </div>
                        <div className="text-xs text-yellow-600 mt-1">Disputed amounts</div>
                      </div>
                    )}
                  </div>

                  {/* Summary Message */}
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Fair Release System:</span> Only disputed amounts are held in escrow. 
                      Undisputed balances and accepted claims are released immediately.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Tenancy Status Notices */}
            {isNearingEnd && !hasEnded && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h4 className="font-medium text-blue-800 mb-2">📅 Tenancy Ending Soon</h4>
                <p className="text-sm text-blue-700 mb-4">
                  The lease for this property is ending within 7 days. Prepare for the deposit release process.
                </p>
                {isLandlord() && (
                  <p className="text-sm text-blue-600">
                    You'll be able to inspect the property and manage the deposit after the tenant vacates.
                  </p>
                )}
                {isTenant() && (
                  <p className="text-sm text-blue-600">
                    Please prepare for move-out. Your landlord will have 7 days after tenancy ends to process the deposit.
                  </p>
                )}
              </div>
            )}

            {hasEnded && (
              <div className={`border rounded-lg p-4 mb-6 ${
                (deposit.inspection_status?.days_remaining || 0) > 0 
                  ? 'bg-yellow-50 border-yellow-200' 
                  : 'bg-red-50 border-red-200'
              }`}>
                <h4 className={`font-medium mb-2 ${
                  (deposit.inspection_status?.days_remaining || 0) > 0 
                    ? 'text-yellow-800' 
                    : 'text-red-800'
                }`}>
                  🏠 Tenancy Has Ended - {(deposit.inspection_status?.days_remaining || 0) > 0 ? 'Inspection Period Active' : 'Inspection Period Ended'}
                </h4>
                <p className={`text-sm mb-4 ${
                  (deposit.inspection_status?.days_remaining || 0) > 0 
                    ? 'text-yellow-700' 
                    : 'text-red-700'
                }`}>
                  The tenancy has ended and the property is now vacant. {
                    (deposit.inspection_status?.days_remaining || 0) > 0 
                      ? 'The 7-day inspection period is active.' 
                      : 'The 7-day inspection period has ended.'
                  }
                </p>
                {isLandlord() && (
                  <p className={`text-sm ${
                    (deposit.inspection_status?.days_remaining || 0) > 0 
                      ? 'text-yellow-600' 
                      : 'text-red-600'
                  }`}>
                    {(deposit.inspection_status?.days_remaining || 0) > 0 
                      ? `You have ${deposit.inspection_status?.days_remaining || 0} days remaining to inspect the property and submit any deduction claims, or release the full deposit.`
                      : 'The inspection period has expired. Any undisputed deposit amounts have been automatically released to the tenant.'
                    }
                  </p>
                )}
                {isTenant() && (
                  <p className={`text-sm ${
                    (deposit.inspection_status?.days_remaining || 0) > 0 
                      ? 'text-yellow-600' 
                      : 'text-red-600'
                  }`}>
                    {(deposit.inspection_status?.days_remaining || 0) > 0 
                      ? `Your landlord has ${deposit.inspection_status?.days_remaining || 0} days to inspect and process your deposit. You'll be notified of any claims.`
                      : 'The inspection period has ended. Any undisputed deposit amounts have been automatically released to you.'
                    }
                  </p>
                )}
              </div>
            )}

            {/* Current Claims */}
            {canViewClaims && (
              <div className="bg-white shadow rounded-lg p-6 mb-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold text-gray-900">Deposit Claims</h3>
                  {deposit.claims?.length > 0 && isTenant() && (
                    <button
                      onClick={() => navigate(`/deposit/claims/${deposit.claims[0].id}`)}
                      className={`px-4 py-2 rounded-lg font-medium ${
                        allClaimsResponded(deposit.claims)
                          ? 'bg-gray-600 hover:bg-gray-700 text-white'
                          : 'bg-blue-600 hover:bg-blue-700 text-white'
                      }`}
                    >
                      {allClaimsResponded(deposit.claims) 
                        ? 'View Your Responses' 
                        : 'Review & Respond to Claims'
                      }
                    </button>
                  )}
                </div>
                {deposit.claims?.length > 0 ? (
                  <div className="space-y-4">
                    {deposit.claims.map((claim, index) => (
                      <div key={claim.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-medium text-gray-900">
                              Item {index + 1}: {formatClaimType(claim.title || claim.claim_type)}
                            </h4>
                            <p className="text-sm text-gray-600 mt-1">
                              <span className="font-medium">Landlord's Comments:</span> {claim.description}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="text-lg font-bold text-red-600">RM {claim.claimed_amount || claim.amount}</span>
                            <div className="mt-1">
                              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getClaimStatusColor(claim.status)}`}>
                                {getClaimStatusText(claim.status)}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        {/* Show tenant response details if available */}
                        {claim.tenant_response && (
                          <div className="mt-3 p-3 bg-gray-50 rounded-lg border-l-4 border-blue-500">
                            <h5 className="text-sm font-medium text-gray-900 mb-2">Tenant's Response:</h5>
                            <div className="space-y-2">
                              <div className="flex items-center">
                                <span className={`text-sm font-medium ${
                                  claim.tenant_response === 'accept' 
                                    ? 'text-green-600' 
                                    : claim.tenant_response === 'partial_accept'
                                      ? 'text-orange-600'
                                      : 'text-red-600'
                                }`}>
                                  {claim.tenant_response === 'accept' 
                                    ? '✅ Accepted - Tenant agreed to pay full amount'
                                    : claim.tenant_response === 'partial_accept'
                                      ? '⚖️ Partial Accept - Tenant offered different amount'
                                      : '❌ Rejected - Tenant disputed this charge'
                                  }
                                </span>
                              </div>
                              
                              {/* Show counter amount for partial accepts */}
                              {claim.tenant_response === 'partial_accept' && claim.tenant_counter_amount && (
                                <div className="text-sm">
                                  <span className="font-medium text-orange-800">Counter-Offer:</span>
                                  <span className="ml-1 font-bold text-orange-600">RM {parseFloat(claim.tenant_counter_amount).toFixed(2)}</span>
                                </div>
                              )}
                              
                              {/* Show tenant explanation if provided */}
                              {claim.tenant_explanation && (
                                <div className="text-sm">
                                  <span className="font-medium text-gray-700">Tenant's Explanation:</span>
                                  <p className="mt-1 text-gray-600 italic">"{claim.tenant_explanation}"</p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-800">
                        <strong>Total Claimed:</strong> RM {deposit.claims.reduce((sum, claim) => sum + (claim.claimed_amount || claim.amount || 0), 0).toFixed(2)}
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">No claims have been made yet.</p>
                )}
              </div>
            )}
          </div>

          {/* Sidebar Actions */}
          <div>
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Actions</h3>
              
              <div className="space-y-3">
                {/* Landlord Actions */}
                {isLandlord() && canRelease && (
                  <>
                    <button
                      onClick={() => setShowReleaseModal(true)}
                      className="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md text-sm font-medium"
                    >
                      ✅ Release Full Deposit
                    </button>
                    
                    <button
                      onClick={handleMakeClaim}
                      className="w-full bg-orange-500 hover:bg-orange-600 text-white py-2 px-4 rounded-md text-sm font-medium"
                    >
                      📋 Make Deduction Claim
                    </button>
                  </>
                )}

                {/* Landlord Response to Disputes */}
                {isLandlord() && deposit.claims?.some(claim => claim.status === 'disputed') && (
                  <button
                    onClick={() => navigate(`/deposit/${deposit.id}/landlord-response`)}
                    className="w-full bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded-md text-sm font-medium"
                  >
                    ⚖️ Respond to Disputes
                  </button>
                )}

                {/* View Claims Button */}
                {canViewClaims && (
                  <button
                    onClick={() => navigate(`/deposit/${deposit.id}/claims`)}
                    className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium"
                  >
                    📄 View All Claims
                  </button>
                )}

                {/* Status Information */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">Status Information</h4>
                  <p className="text-sm text-gray-600">
                    {getStatusDescription(deposit.status, isLandlord())}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Release Confirmation Modal */}
      {showReleaseModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Release Full Deposit</h3>
            <p className="text-gray-600 mb-4">
              Are you sure you want to release the full deposit amount of <strong>RM {deposit.amount}</strong> to the tenant?
            </p>
            <p className="text-sm text-gray-500 mb-6">
              This action cannot be undone. The tenant will receive the full deposit amount.
            </p>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowReleaseModal(false)}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleFullRelease}
                className="flex-1 bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md"
              >
                Release Deposit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper functions
const getStatusColor = (status) => {
  switch (status) {
    case 'held_in_escrow':
      return 'bg-blue-100 text-blue-800';
    case 'pending_release':
      return 'bg-yellow-100 text-yellow-800';
    case 'disputed':
      return 'bg-red-100 text-red-800';
    case 'released':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getStatusText = (status) => {
  switch (status) {
    case 'held_in_escrow':
      return 'Held in Escrow';
    case 'pending_release':
      return 'Pending Release';
    case 'disputed':
      return 'Under Dispute';
    case 'released':
      return 'Released';
    default:
      return status;
  }
};

const getStatusDescription = (status, isLandlord) => {
  switch (status) {
    case 'held_in_escrow':
      return isLandlord 
        ? 'The deposit is securely held in escrow. You can release it or make claims when the tenancy ends.'
        : 'Your deposit is securely held in escrow and will be returned at the end of your tenancy.';
    case 'pending_release':
      return 'The deposit release process has been initiated and is being processed.';
    case 'disputed':
      return 'There are disputed claims that need to be resolved before the deposit can be released.';
    case 'released':
      return 'The deposit has been released to the tenant.';
    default:
      return 'Status information not available.';
  }
};

const getClaimStatusColor = (status) => {
  switch (status) {
    case 'submitted':
      return 'bg-yellow-100 text-yellow-800';
    case 'accepted':
      return 'bg-green-100 text-green-800';
    case 'disputed':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getClaimStatusText = (status) => {
  switch (status) {
    case 'submitted':
      return 'Pending Response';
    case 'accepted':
      return 'Accepted';
    case 'disputed':
      return 'Disputed';
    default:
      return status;
  }
};

// Helper function to format claim types from snake_case to Title Case
const formatClaimType = (claimType) => {
  if (!claimType) return '';
  return claimType
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Helper function to check if all claims have been responded to
const allClaimsResponded = (claims) => {
  if (!claims || claims.length === 0) return false;
  return claims.every(claim => 
    claim.status && 
    !['submitted', 'tenant_notified'].includes(claim.status.toLowerCase())
  );
};

export default DepositManagementPage;

