import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DepositTestingPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [agreements, setAgreements] = useState([]);
  const [deposits, setDeposits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadTestData();
  }, []);

  const loadTestData = async () => {
    try {
      setLoading(true);
      
      // Load agreements
      const agreementsResponse = await fetch('/api/tenancy-agreements', {
        credentials: 'include'
      });
      
      if (agreementsResponse.ok) {
        const agreementsData = await agreementsResponse.json();
        setAgreements(agreementsData.agreements || []);
      }

      // Load deposits
      const depositsResponse = await fetch('/api/deposits', {
        credentials: 'include'
      });
      
      if (depositsResponse.ok) {
        const depositsData = await depositsResponse.json();
        setDeposits(depositsData.deposits || []);
      }
      
    } catch (err) {
      console.error('Error loading test data:', err);
    } finally {
      setLoading(false);
    }
  };

  const simulateEndingTenancy = async (agreementId) => {
    try {
      setProcessing(true);
      const response = await fetch(`/api/admin/testing/simulate-ending-tenancy/${agreementId}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const result = await response.json();
      if (result.success) {
        alert('Tenancy ending simulation triggered! The agreement lease end date has been set to 5 days from now.');
        await loadTestData();
      } else {
        alert(result.error || 'Failed to simulate ending tenancy');
      }
    } catch (err) {
      console.error('Error simulating ending tenancy:', err);
      alert('Failed to simulate ending tenancy');
    } finally {
      setProcessing(false);
    }
  };

  const createTestClaim = async (depositId) => {
    try {
      setProcessing(true);
      const response = await fetch(`/api/admin/testing/create-test-claim/${depositId}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const result = await response.json();
      if (result.success) {
        alert('Test claim created! The tenant will now see a claim to respond to.');
        await loadTestData();
      } else {
        alert(result.error || 'Failed to create test claim');
      }
    } catch (err) {
      console.error('Error creating test claim:', err);
      alert('Failed to create test claim');
    } finally {
      setProcessing(false);
    }
  };

  const simulateDisputeResponse = async (claimId, responseType) => {
    try {
      setProcessing(true);
      const response = await fetch(`/api/admin/testing/simulate-dispute-response/${claimId}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          response_type: responseType
        })
      });

      const result = await response.json();
      if (result.success) {
        alert(`Dispute response simulated! The claim is now ${responseType === 'accept' ? 'accepted' : 'disputed'}.`);
        await loadTestData();
      } else {
        alert(result.error || 'Failed to simulate dispute response');
      }
    } catch (err) {
      console.error('Error simulating dispute response:', err);
      alert('Failed to simulate dispute response');
    } finally {
      setProcessing(false);
    }
  };

  const resetDepositSystem = async () => {
    if (!confirm('Are you sure you want to reset all deposit data? This will delete all deposits, claims, and disputes.')) {
      return;
    }

    try {
      setProcessing(true);
      const response = await fetch('/api/admin/testing/reset-deposit-system', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const result = await response.json();
      if (result.success) {
        alert('Deposit system reset successfully! All deposit data has been cleared.');
        await loadTestData();
      } else {
        alert(result.error || 'Failed to reset deposit system');
      }
    } catch (err) {
      console.error('Error resetting deposit system:', err);
      alert('Failed to reset deposit system');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-600">Loading test data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="mr-4 text-gray-500 hover:text-gray-700"
              >
                ← Back to Dashboard
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Deposit System Testing</h1>
            </div>
            <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
              🧪 Testing Mode
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-bold text-blue-900 mb-4">🧪 How to Test the Deposit Lifecycle</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-blue-800 mb-2">Testing Steps:</h3>
              <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
                <li>Start with an active agreement that has a paid deposit</li>
                <li>Click "Simulate Ending Tenancy" to trigger the 7-day notice</li>
                <li>Navigate to the deposit management page</li>
                <li>As landlord: Create claims or release deposit</li>
                <li>As tenant: Respond to claims (accept/dispute)</li>
                <li>Test the mediation and resolution process</li>
              </ol>
            </div>
            <div>
              <h3 className="font-medium text-blue-800 mb-2">Quick Actions:</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Use "Create Test Claim" for instant claim scenarios</li>
                <li>• Use "Simulate Response" to test dispute workflows</li>
                <li>• Use "Reset System" to start fresh</li>
                <li>• Check different user roles (landlord/tenant)</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Active Agreements */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Active Agreements</h2>
            
            {agreements.length > 0 ? (
              <div className="space-y-4">
                {agreements.filter(agreement => agreement.status === 'active').map((agreement) => (
                  <div key={agreement.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-medium text-gray-900">{agreement.property_address}</h3>
                        <p className="text-sm text-gray-600">
                          Tenant: {agreement.tenant_first_name} {agreement.tenant_last_name}
                        </p>
                        <p className="text-sm text-gray-600">
                          Lease End: {agreement.lease_end_date ? new Date(agreement.lease_end_date).toLocaleDateString() : 'Not set'}
                        </p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        agreement.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {agreement.status}
                      </span>
                    </div>
                    
                    <div className="flex flex-wrap gap-2 mt-3">
                      <button
                        onClick={() => simulateEndingTenancy(agreement.id)}
                        disabled={processing}
                        className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50"
                      >
                        ⏰ Simulate Ending Tenancy
                      </button>
                      
                      <button
                        onClick={() => navigate(`/deposit/${agreement.id}/manage`)}
                        className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm font-medium"
                      >
                        📋 Manage Deposit
                      </button>
                      
                      <button
                        onClick={() => navigate(`/agreement/${agreement.id}`)}
                        className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm font-medium"
                      >
                        📄 View Agreement
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-400 text-4xl mb-2">📋</div>
                <p className="text-gray-500">No active agreements found</p>
                <p className="text-sm text-gray-400 mt-1">Create a tenancy agreement and pay the deposit first</p>
              </div>
            )}
          </div>

          {/* Deposit Status */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Deposit Status</h2>
            
            {deposits.length > 0 ? (
              <div className="space-y-4">
                {deposits.map((deposit) => (
                  <div key={deposit.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-medium text-gray-900">RM {deposit.amount}</h3>
                        <p className="text-sm text-gray-600">{deposit.property_address}</p>
                        <p className="text-sm text-gray-600">
                          Paid: {new Date(deposit.paid_at || deposit.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getDepositStatusColor(deposit.status)}`}>
                        {getDepositStatusText(deposit.status)}
                      </span>
                    </div>
                    
                    <div className="flex flex-wrap gap-2 mt-3">
                      {deposit.status === 'held_in_escrow' && (
                        <button
                          onClick={() => createTestClaim(deposit.id)}
                          disabled={processing}
                          className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50"
                        >
                          📋 Create Test Claim
                        </button>
                      )}
                      
                      {deposit.claims?.length > 0 && (
                        <>
                          <button
                            onClick={() => simulateDisputeResponse(deposit.claims[0].id, 'accept')}
                            disabled={processing}
                            className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50"
                          >
                            ✅ Simulate Accept
                          </button>
                          
                          <button
                            onClick={() => simulateDisputeResponse(deposit.claims[0].id, 'dispute')}
                            disabled={processing}
                            className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50"
                          >
                            ❌ Simulate Dispute
                          </button>
                        </>
                      )}
                    </div>
                    
                    {deposit.claims?.length > 0 && (
                      <div className="mt-3 p-2 bg-gray-50 rounded text-sm">
                        <strong>Claims:</strong> {deposit.claims.length} claim(s) totaling RM {
                          deposit.claims.reduce((sum, claim) => sum + claim.claimed_amount, 0)
                        }
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-400 text-4xl mb-2">💰</div>
                <p className="text-gray-500">No deposits found</p>
                <p className="text-sm text-gray-400 mt-1">Complete a deposit payment first</p>
              </div>
            )}
          </div>
        </div>

        {/* System Controls */}
        <div className="bg-white shadow rounded-lg p-6 mt-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">System Controls</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <button
                onClick={resetDepositSystem}
                disabled={processing}
                className="w-full bg-red-500 hover:bg-red-600 text-white py-3 px-4 rounded-md font-medium disabled:opacity-50"
              >
                🔄 Reset Deposit System
              </button>
              <p className="text-sm text-gray-500 mt-2">Clear all deposit data</p>
            </div>
            
            <div className="text-center">
              <button
                onClick={loadTestData}
                disabled={processing}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 px-4 rounded-md font-medium disabled:opacity-50"
              >
                🔄 Refresh Data
              </button>
              <p className="text-sm text-gray-500 mt-2">Reload current status</p>
            </div>
            
            <div className="text-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full bg-gray-500 hover:bg-gray-600 text-white py-3 px-4 rounded-md font-medium"
              >
                📊 View Dashboard
              </button>
              <p className="text-sm text-gray-500 mt-2">Return to main dashboard</p>
            </div>
          </div>
        </div>

        {/* Testing Scenarios */}
        <div className="bg-white shadow rounded-lg p-6 mt-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Common Testing Scenarios</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">🟢 Happy Path - Full Release</h3>
              <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
                <li>Simulate ending tenancy</li>
                <li>Go to deposit management</li>
                <li>Click "Release Full Deposit"</li>
                <li>Confirm release</li>
                <li>Verify tenant receives full amount</li>
              </ol>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">🟡 Dispute Path - Claims & Resolution</h3>
              <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
                <li>Simulate ending tenancy</li>
                <li>Create test claim or make manual claim</li>
                <li>Switch to tenant view</li>
                <li>Respond to claim (accept/dispute)</li>
                <li>Test mediation process</li>
                <li>Resolve dispute</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper functions
const getDepositStatusColor = (status) => {
  switch (status) {
    case 'held_in_escrow':
      return 'bg-blue-100 text-blue-800';
    case 'disputed':
      return 'bg-red-100 text-red-800';
    case 'released':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getDepositStatusText = (status) => {
  switch (status) {
    case 'held_in_escrow':
      return 'Held in Escrow';
    case 'disputed':
      return 'Under Dispute';
    case 'released':
      return 'Released';
    default:
      return status;
  }
};

export default DepositTestingPage;

