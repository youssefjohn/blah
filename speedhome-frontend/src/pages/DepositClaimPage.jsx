import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DepositClaimPage = () => {
  const { depositId } = useParams();
  const navigate = useNavigate();
  const { user, isLandlord } = useAuth();
  
  const [deposit, setDeposit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  
  const [claimItems, setClaimItems] = useState([{
    id: Date.now(),
    reason: '',
    amount: '',
    description: '',
    evidence_photos: [],
    evidence_documents: []
  }]);

  useEffect(() => {
    if (!isLandlord()) {
      navigate('/dashboard');
      return;
    }
    loadDepositData();
  }, [depositId]);

  const loadDepositData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/deposits/${depositId}`, {
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

  const addClaimItem = () => {
    setClaimItems([...claimItems, {
      id: Date.now(),
      reason: '',
      amount: '',
      description: '',
      evidence_photos: [],
      evidence_documents: []
    }]);
  };

  const removeClaimItem = (id) => {
    if (claimItems.length > 1) {
      setClaimItems(claimItems.filter(item => item.id !== id));
    }
  };

  const updateClaimItem = (id, field, value) => {
    setClaimItems(claimItems.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    ));
  };

  const handleFileUpload = async (id, field, files) => {
    const fileNames = Array.from(files).map(file => file.name);
    updateClaimItem(id, field, fileNames);
  };

  const calculateTotalClaimed = () => {
    return claimItems.reduce((total, item) => {
      const amount = parseFloat(item.amount) || 0;
      return total + amount;
    }, 0);
  };

  const calculateRefundAmount = () => {
    if (!deposit) return 0;
    return Math.max(0, deposit.amount - calculateTotalClaimed());
  };

  const validateClaims = () => {
    for (const item of claimItems) {
      if (!item.reason || !item.amount || !item.description) {
        return false;
      }
      if (parseFloat(item.amount) <= 0) {
        return false;
      }
    }

    const totalClaimed = calculateTotalClaimed();
    if (totalClaimed > deposit.amount) {
      return false;
    }

    return true;
  };

  const submitClaim = async () => {
    if (!validateClaims()) {
      alert('Please fill in all required fields and ensure claim amounts are valid.');
      return;
    }

    try {
      setSubmitting(true);

      const payload = {
        title: "Landlord Claim for Security Deposit",
        description: "Claim for deductions from the security deposit at the end of the tenancy.",
        claim_items: claimItems.map(item => ({
          title: item.reason,
          amount: parseFloat(item.amount),
          description: item.description,
          evidence_photos: item.evidence_photos,
          evidence_documents: item.evidence_documents
        }))
      };

      const response = await fetch(`/api/deposits/${depositId}/claims`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (result.success) {
        alert('Claim submitted successfully! The tenant will be notified.');
        navigate(`/deposit/${depositId}/manage`);
      } else {
        alert(result.error || 'Failed to submit claim');
      }
    } catch (err) {
      console.error('Error submitting claim:', err);
      alert('Failed to submit claim');
    } finally {
      setSubmitting(false);
    }
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

  if (error || !deposit) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Deposit</h2>
          <p className="text-gray-600 mb-4">{error || 'Deposit not found'}</p>
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

  const totalClaimed = calculateTotalClaimed();
  const refundAmount = calculateRefundAmount();
  const isValid = validateClaims();

  return (
    <div className="min-h-screen bg-gray-50">
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
              <h1 className="text-2xl font-bold text-gray-900">Claim Deductions from Deposit</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Property Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Property Address</span>
                  <p className="text-gray-900">{deposit.property_address}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Tenant Name</span>
                  <p className="text-gray-900">{deposit.tenant_name}</p>
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-900">Deduction Items</h2>
                <button
                  onClick={addClaimItem}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  + Add Item
                </button>
              </div>

              <div className="space-y-6">
                {claimItems.map((item, index) => (
                  <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-lg font-medium text-gray-900">Item {index + 1}</h3>
                      {claimItems.length > 1 && (
                        <button
                          onClick={() => removeClaimItem(item.id)}
                          className="text-red-500 hover:text-red-700 text-sm"
                        >
                          Remove
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Reason for Deduction *
                        </label>
                        <select
                          value={item.reason}
                          onChange={(e) => updateClaimItem(item.id, 'reason', e.target.value)}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                          required
                        >
                          <option value="">Select a reason</option>
                          <option value="cleaning_fees">Cleaning Fees</option>
                          <option value="repair_damages">Repairs for Damages</option>
                          <option value="unpaid_rent">Unpaid Rent</option>
                          <option value="unpaid_utilities">Unpaid Utilities</option>
                          <option value="missing_items">Missing Items</option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Amount (RM) *
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={item.amount}
                          onChange={(e) => updateClaimItem(item.id, 'amount', e.target.value)}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                          placeholder="0.00"
                          required
                        />
                      </div>
                    </div>

                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description *
                      </label>
                      <textarea
                        value={item.description}
                        onChange={(e) => updateClaimItem(item.id, 'description', e.target.value)}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                        rows="3"
                        placeholder="Please provide a detailed explanation of this charge..."
                        required
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Upload Photos
                        </label>
                        <input
                          type="file"
                          multiple
                          accept="image/*"
                          onChange={(e) => handleFileUpload(item.id, 'evidence_photos', e.target.files)}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                        />
                        {item.evidence_photos.length > 0 && (
                          <p className="text-xs text-gray-500 mt-1">
                            {item.evidence_photos.length} photo(s) selected
                          </p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Upload Documents
                        </label>
                        <input
                          type="file"
                          multiple
                          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                          onChange={(e) => handleFileUpload(item.id, 'evidence_documents', e.target.files)}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                        />
                        {item.evidence_documents.length > 0 && (
                          <p className="text-xs text-gray-500 mt-1">
                            {item.evidence_documents.length} document(s) selected
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Claim Summary</h3>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Held:</span>
                  <span className="font-medium">RM {deposit.amount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Claimed:</span>
                  <span className="font-medium text-red-600">RM {totalClaimed.toFixed(2)}</span>
                </div>
                <div className="border-t pt-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-900">Amount to be Refunded:</span>
                    <span className="font-bold text-green-600">RM {refundAmount.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {totalClaimed > deposit.amount && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-700">
                    ⚠️ Total claimed amount exceeds the deposit. Please adjust your claims.
                  </p>
                </div>
              )}
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Actions</h3>
              
              <div className="space-y-3">
                <button
                  onClick={submitClaim}
                  disabled={!isValid || submitting}
                  className={`w-full py-2 px-4 rounded-md text-sm font-medium ${
                    isValid && !submitting
                      ? 'bg-orange-500 hover:bg-orange-600 text-white'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {submitting ? 'Submitting...' : 'Submit Claim to Tenant'}
                </button>

                <button
                  onClick={() => navigate(`/deposit/${depositId}/manage`)}
                  className="w-full bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-md text-sm font-medium"
                >
                  Cancel
                </button>
              </div>

              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs text-blue-700">
                  💡 The tenant will have 7 days to review and respond to your claim. 
                  Undisputed amounts will be automatically deducted.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DepositClaimPage;