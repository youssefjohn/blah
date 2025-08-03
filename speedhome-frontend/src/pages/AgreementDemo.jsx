import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const AgreementDemo = () => {
  // Mock agreement data with different scenarios
  const [selectedScenario, setSelectedScenario] = useState('landlord_pending');
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [withdrawing, setWithdrawing] = useState(false);
  const [withdrawalReason, setWithdrawalReason] = useState('');

  // Mock scenarios
  const scenarios = {
    landlord_pending: {
      id: 1,
      status: 'pending_signatures',
      landlord_signed_at: '2025-08-03T20:00:00Z',
      tenant_signed_at: null,
      expires_at: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours from now
      is_expired: false,
      can_landlord_withdraw: false, // Landlord already signed
      can_tenant_withdraw: false,
      userRole: 'landlord',
      title: 'Landlord View - Waiting for Tenant Signature'
    },
    tenant_pending: {
      id: 2,
      status: 'pending_signatures',
      landlord_signed_at: null,
      tenant_signed_at: null,
      expires_at: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(), // 5 hours from now
      is_expired: false,
      can_landlord_withdraw: true, // Landlord can withdraw before tenant signs
      can_tenant_withdraw: false,
      userRole: 'tenant',
      title: 'Tenant View - Can Sign Agreement'
    },
    tenant_signed: {
      id: 3,
      status: 'pending_signatures',
      landlord_signed_at: null,
      tenant_signed_at: '2025-08-03T21:00:00Z',
      expires_at: new Date(Date.now() + 1 * 60 * 60 * 1000).toISOString(), // 1 hour from now
      is_expired: false,
      can_landlord_withdraw: false,
      can_tenant_withdraw: true, // Tenant can withdraw signature before landlord signs
      userRole: 'tenant',
      title: 'Tenant View - Can Withdraw Signature'
    },
    both_signed: {
      id: 4,
      status: 'pending_payment',
      landlord_signed_at: '2025-08-03T20:00:00Z',
      tenant_signed_at: '2025-08-03T21:00:00Z',
      expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString(), // 30 minutes from now
      is_expired: false,
      can_landlord_withdraw: false,
      can_tenant_withdraw: false, // No withdrawal after both sign
      userRole: 'tenant',
      title: 'Both Signed - Pending Payment'
    },
    expired: {
      id: 5,
      status: 'expired',
      landlord_signed_at: null,
      tenant_signed_at: null,
      expires_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1 hour ago
      is_expired: true,
      can_landlord_withdraw: false,
      can_tenant_withdraw: false,
      userRole: 'landlord',
      title: 'Expired Agreement'
    }
  };

  const currentAgreement = scenarios[selectedScenario];

  // Countdown timer effect
  useEffect(() => {
    if (currentAgreement && currentAgreement.expires_at && !currentAgreement.is_expired) {
      const timer = setInterval(() => {
        const now = new Date().getTime();
        const expiry = new Date(currentAgreement.expires_at).getTime();
        const difference = expiry - now;
        
        if (difference > 0) {
          const hours = Math.floor(difference / (1000 * 60 * 60));
          const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((difference % (1000 * 60)) / 1000);
          setTimeRemaining({ hours, minutes, seconds });
        } else {
          setTimeRemaining(null);
        }
      }, 1000);

      return () => clearInterval(timer);
    } else {
      setTimeRemaining(null);
    }
  }, [currentAgreement]);

  const handleWithdraw = async () => {
    setWithdrawing(true);
    // Simulate API call
    setTimeout(() => {
      alert(`Withdrawal successful! Reason: ${withdrawalReason}`);
      setShowWithdrawModal(false);
      setWithdrawalReason('');
      setWithdrawing(false);
    }, 1000);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending_signatures':
        return 'text-yellow-600 bg-yellow-100';
      case 'pending_payment':
        return 'text-blue-600 bg-blue-100';
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'expired':
        return 'text-gray-600 bg-gray-100';
      case 'withdrawn':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatStatus = (status) => {
    switch (status) {
      case 'pending_signatures':
        return 'Pending Signatures';
      case 'pending_payment':
        return 'Pending Payment';
      case 'active':
        return 'Active';
      case 'expired':
        return 'Expired';
      case 'withdrawn':
        return 'Withdrawn';
      default:
        return status;
    }
  };

  const canWithdraw = (agreement, userRole) => {
    if (userRole === 'landlord') {
      return agreement.can_landlord_withdraw;
    } else if (userRole === 'tenant') {
      return agreement.can_tenant_withdraw;
    }
    return false;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link to="/" className="text-blue-600 hover:text-blue-800 mr-4">
                ← Back
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Tenancy Agreement Demo</h1>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(currentAgreement.status)}`}>
                {formatStatus(currentAgreement.status)}
              </span>
              
              {/* Countdown Timer */}
              {timeRemaining && !currentAgreement.is_expired && currentAgreement.status !== 'active' && (
                <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-1">
                  <div className="flex items-center text-red-700">
                    <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium">
                      {timeRemaining.hours}h {timeRemaining.minutes}m {timeRemaining.seconds}s remaining
                    </span>
                  </div>
                </div>
              )}
              
              {/* Expired Notice */}
              {currentAgreement.is_expired && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg px-3 py-1">
                  <span className="text-sm font-medium text-gray-600">⏰ Expired</span>
                </div>
              )}
              
              {/* Withdrawal Button */}
              {canWithdraw(currentAgreement, currentAgreement.userRole) && (
                <button
                  onClick={() => setShowWithdrawModal(true)}
                  className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded-md text-sm font-medium"
                >
                  {currentAgreement.userRole === 'landlord' ? 'Withdraw Offer' : 'Withdraw Signature'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Scenario Selector */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Demo Scenarios</h2>
          <p className="text-gray-600 mb-4">Select different scenarios to test the countdown timer and withdrawal buttons:</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(scenarios).map(([key, scenario]) => (
              <button
                key={key}
                onClick={() => setSelectedScenario(key)}
                className={`p-4 rounded-lg border text-left transition-colors ${
                  selectedScenario === key
                    ? 'border-blue-500 bg-blue-50 text-blue-900'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
              >
                <div className="font-medium">{scenario.title}</div>
                <div className="text-sm mt-1">
                  Status: {formatStatus(scenario.status)}
                </div>
                <div className="text-sm">
                  Role: {scenario.userRole}
                </div>
                {scenario.can_landlord_withdraw && scenario.userRole === 'landlord' && (
                  <div className="text-sm text-orange-600 mt-1">✓ Can withdraw</div>
                )}
                {scenario.can_tenant_withdraw && scenario.userRole === 'tenant' && (
                  <div className="text-sm text-orange-600 mt-1">✓ Can withdraw</div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Current Scenario Details */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Scenario: {currentAgreement.title}</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Agreement Details</h3>
              <dl className="space-y-2">
                <div>
                  <dt className="text-sm text-gray-500">Agreement ID</dt>
                  <dd className="text-sm font-medium">{currentAgreement.id}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Status</dt>
                  <dd className="text-sm font-medium">{formatStatus(currentAgreement.status)}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">User Role</dt>
                  <dd className="text-sm font-medium capitalize">{currentAgreement.userRole}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Expires At</dt>
                  <dd className="text-sm font-medium">
                    {new Date(currentAgreement.expires_at).toLocaleString()}
                  </dd>
                </div>
              </dl>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Signature Status</h3>
              <dl className="space-y-2">
                <div>
                  <dt className="text-sm text-gray-500">Landlord Signed</dt>
                  <dd className="text-sm font-medium">
                    {currentAgreement.landlord_signed_at ? (
                      <span className="text-green-600">✓ Signed</span>
                    ) : (
                      <span className="text-yellow-600">⏳ Pending</span>
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Tenant Signed</dt>
                  <dd className="text-sm font-medium">
                    {currentAgreement.tenant_signed_at ? (
                      <span className="text-green-600">✓ Signed</span>
                    ) : (
                      <span className="text-yellow-600">⏳ Pending</span>
                    )}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* Feature Testing */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="font-medium text-gray-900 mb-4">Feature Testing</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">Countdown Timer</div>
                  <div className="text-sm text-gray-600">
                    {timeRemaining ? (
                      `Active: ${timeRemaining.hours}h ${timeRemaining.minutes}m ${timeRemaining.seconds}s remaining`
                    ) : currentAgreement.is_expired ? (
                      'Expired'
                    ) : (
                      'Not applicable for this scenario'
                    )}
                  </div>
                </div>
                <div className="text-2xl">
                  {timeRemaining ? '⏰' : currentAgreement.is_expired ? '❌' : '⏸️'}
                </div>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">Withdrawal Button</div>
                  <div className="text-sm text-gray-600">
                    {canWithdraw(currentAgreement, currentAgreement.userRole) ? (
                      `Available: ${currentAgreement.userRole === 'landlord' ? 'Withdraw Offer' : 'Withdraw Signature'}`
                    ) : (
                      'Not available for this scenario'
                    )}
                  </div>
                </div>
                <div className="text-2xl">
                  {canWithdraw(currentAgreement, currentAgreement.userRole) ? '🔴' : '🚫'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Withdrawal Modal */}
      {showWithdrawModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {currentAgreement.userRole === 'landlord' ? 'Withdraw Offer' : 'Withdraw Signature'}
            </h3>
            <p className="text-gray-600 mb-4">
              Please provide a reason for withdrawal:
            </p>
            <textarea
              value={withdrawalReason}
              onChange={(e) => setWithdrawalReason(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md resize-none"
              rows="3"
              placeholder="Enter reason for withdrawal..."
            />
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowWithdrawModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
                disabled={withdrawing}
              >
                Cancel
              </button>
              <button
                onClick={handleWithdraw}
                disabled={withdrawing || !withdrawalReason.trim()}
                className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-md disabled:opacity-50"
              >
                {withdrawing ? 'Processing...' : 'Confirm Withdrawal'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgreementDemo;

