import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DepositDisputePage = () => {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const { user, isTenant, isLandlord } = useAuth();
  
  // --- FIX: State updated to handle a list of claims and page-level data ---
  const [claims, setClaims] = useState([]);
  const [pageData, setPageData] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const [responses, setResponses] = useState({});

  // Helper function to format claim types from snake_case to Title Case
  const formatClaimType = (claimType) => {
    if (!claimType) return '';
    return claimType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  useEffect(() => {
    loadClaimData();
  }, [claimId]);

  useEffect(() => {
    // This effect runs after claims are loaded to initialize the responses state
    if (claims.length > 0) {
      const initialResponses = {};
      claims.forEach(item => {
        initialResponses[item.id] = {
          response: '',
          counter_amount: '',
          explanation: '',
          evidence_photos: [],
          evidence_documents: []
        };
      });
      setResponses(initialResponses);
    }
  }, [claims]);

  const loadClaimData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/deposits/claims/${claimId}`, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to load claim data');
      }

      const data = await response.json();
      if (data.success) {
        // --- FIX: Set the new state variables from the API response ---
        setClaims(data.claims);
        setPageData({
          property_address: data.property_address,
          landlord_name: data.landlord_name,
          deposit_amount: data.deposit_amount,
          created_at: data.claims[0]?.created_at, // Use first claim for general dates
          response_deadline: data.claims[0]?.tenant_response_deadline
        });
      } else {
        setError(data.error || 'Failed to load claim');
      }
    } catch (err) {
      setError('Failed to load claim data');
      console.error('Error loading claim:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateResponse = (itemId, field, value) => {
    setResponses(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        [field]: value
      }
    }));
  };

  const handleFileUpload = async (itemId, field, files) => {
    const fileNames = Array.from(files).map(file => file.name);
    updateResponse(itemId, field, fileNames);
  };

  const calculateTotalAccepted = () => {
    return claims.reduce((total, item) => {
      const response = responses[item.id];
      if (response?.response === 'accept') {
        return total + item.claimed_amount;
      } else if (response?.response === 'partial_accept') {
        return total + (parseFloat(response.counter_amount) || 0);
      }
      return total;
    }, 0);
  };

  const calculateTotalDisputed = () => {
    return claims.reduce((total, item) => {
      const response = responses[item.id];
      if (response?.response === 'reject') {
        return total + item.claimed_amount;
      } else if (response?.response === 'partial_accept') {
        return total + (item.claimed_amount - (parseFloat(response.counter_amount) || 0));
      }
      return total;
    }, 0);
  };

  const totalClaimedAmount = claims.reduce((total, item) => total + item.claimed_amount, 0);


  const validateResponses = () => {
    if (claims.length === 0) return false;
    for (const item of claims) {
      const response = responses[item.id];
      if (!response?.response) {
        return false;
      }
      if (response.response === 'partial_accept') {
        if (!response.counter_amount || parseFloat(response.counter_amount) <= 0) {
          return false;
        }
        if (parseFloat(response.counter_amount) >= item.claimed_amount) {
          return false;
        }
      }
      if (response.response !== 'accept' && !response.explanation) {
        return false;
      }
    }
    return true;
  };

  const submitResponse = async () => {
    if (!validateResponses()) {
      alert('Please respond to all items and provide explanations where required.');
      return;
    }

    try {
      setSubmitting(true);

      const response = await fetch(`/api/deposits/claims/${claimId}/respond`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          responses: Object.entries(responses).map(([itemId, response]) => ({
            claim_id: parseInt(itemId), // Changed from item_id
            response_type: response.response, // Changed from response
            counter_amount: response.response === 'partial_accept' ? parseFloat(response.counter_amount) : null,
            explanation: response.explanation,
            evidence_photos: response.evidence_photos,
            evidence_documents: response.evidence_documents
          }))
        })
      });

      const result = await response.json();
      if (result.success) {
        alert('Response submitted successfully! Your landlord will be notified.');
        navigate('/dashboard');
      } else {
        alert(result.error || 'Failed to submit response');
      }
    } catch (err) {
      console.error('Error submitting response:', err);
      alert('Failed to submit response');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-600">Loading claim information...</p>
        </div>
      </div>
    );
  }

  if (error || !pageData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Claim</h2>
          <p className="text-gray-600 mb-4">{error || 'Claim not found'}</p>
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

  const totalAccepted = calculateTotalAccepted();
  const totalDisputed = calculateTotalDisputed();
  const isValid = validateResponses();

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
              <h1 className="text-2xl font-bold text-gray-900">
                {isLandlord() ? 'Deposit Claim Status' : 'Review Your Landlord\'s Deposit Claims'}
              </h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Claim Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Property Address</span>
                  <p className="text-gray-900">{pageData.property_address}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Landlord</span>
                  <p className="text-gray-900">{pageData.landlord_name}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Claim Submitted</span>
                  <p className="text-gray-900">{new Date(pageData.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Response Deadline</span>
                  <p className="text-red-600 font-medium">{new Date(pageData.response_deadline).toLocaleDateString()}</p>
                </div>
              </div>
            </div>

            {isTenant() && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h4 className="font-medium text-blue-800 mb-2">📋 How to Respond</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• <strong>Agree:</strong> Accept the charge as valid</li>
                  <li>• <strong>Disagree:</strong> Dispute the charge completely</li>
                  <li>• <strong>Partial Accept:</strong> Accept a different amount</li>
                  <li>• You must provide an explanation for disagreements or partial acceptances</li>
                  <li>• You can upload counter-evidence to support your position</li>
                </ul>
              </div>
            )}

            {isLandlord() && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <h4 className="font-medium text-green-800 mb-2">📋 Claim Status</h4>
                <p className="text-sm text-green-700">
                  You are viewing the deposit claims you submitted. The tenant has until{' '}
                  <strong>{new Date(pageData?.response_deadline).toLocaleDateString()}</strong> to respond.
                </p>
              </div>
            )}

            <div className="space-y-6">
              {claims.map((item, index) => (
                <div key={item.id} className="bg-white shadow rounded-lg p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      Item {index + 1}: {formatClaimType(item.title)}
                    </h3>
                    <span className="text-xl font-bold text-red-600">RM {item.claimed_amount}</span>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 mb-1">Landlord's Comments:</p>
                    <p className="text-gray-600">{item.description}</p>
                  </div>

                  {/* Show evidence section for both landlords and tenants */}
                  {(item.evidence_photos?.length > 0 || item.evidence_documents?.length > 0) && (
                    <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">
                        {isLandlord() ? 'Your Evidence:' : 'Landlord\'s Evidence:'}
                      </h4>
                      {item.evidence_photos?.length > 0 && (
                        <p className="text-sm text-gray-600">📷 {item.evidence_photos.length} photo(s)</p>
                      )}
                      {item.evidence_documents?.length > 0 && (
                        <p className="text-sm text-gray-600">📄 {item.evidence_documents.length} document(s)</p>
                      )}
                      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium mt-1">
                        View {isLandlord() ? 'Your' : 'Landlord\'s'} Evidence →
                      </button>
                    </div>
                  )}

                  {/* Tenant response form - only show for tenants */}
                  {isTenant() && (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Your Response *
                        </label>
                        <div className="space-y-2">
                          <label className="flex items-center">
                            <input
                              type="radio"
                              name={`response_${item.id}`}
                              value="accept"
                              checked={responses[item.id]?.response === 'accept'}
                              onChange={(e) => updateResponse(item.id, 'response', e.target.value)}
                              className="mr-2"
                            />
                            <span className="text-green-600 font-medium">✅ Agree - This charge is valid</span>
                          </label>
                          <label className="flex items-center">
                            <input
                              type="radio"
                              name={`response_${item.id}`}
                              value="partial_accept"
                              checked={responses[item.id]?.response === 'partial_accept'}
                              onChange={(e) => updateResponse(item.id, 'response', e.target.value)}
                              className="mr-2"
                            />
                            <span className="text-orange-600 font-medium">⚖️ Partial Accept - I agree to a different amount</span>
                          </label>
                          <label className="flex items-center">
                            <input
                              type="radio"
                              name={`response_${item.id}`}
                              value="reject"
                              checked={responses[item.id]?.response === 'reject'}
                              onChange={(e) => updateResponse(item.id, 'response', e.target.value)}
                              className="mr-2"
                            />
                            <span className="text-red-600 font-medium">❌ Disagree - This charge is not valid</span>
                          </label>
                        </div>
                      </div>

                      {responses[item.id]?.response === 'partial_accept' && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Amount You Agree To Pay (RM) *
                          </label>
                          <input
                            type="number"
                            step="0.01"
                            min="0.01"
                            max={item.claimed_amount - 0.01}
                            value={responses[item.id]?.counter_amount || ''}
                            onChange={(e) => updateResponse(item.id, 'counter_amount', e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                            placeholder="0.00"
                            required
                          />
                        </div>
                      )}

                      {responses[item.id]?.response && responses[item.id]?.response !== 'accept' && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Explanation *
                          </label>
                          <textarea
                            value={responses[item.id]?.explanation || ''}
                            onChange={(e) => updateResponse(item.id, 'explanation', e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                            rows="3"
                            placeholder="Please explain why you dispute this charge..."
                            required
                          />
                        </div>
                      )}

                      {responses[item.id]?.response && responses[item.id]?.response !== 'accept' && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Upload Counter-Evidence Photos
                            </label>
                            <input
                              type="file"
                              multiple
                              accept="image/*"
                              onChange={(e) => handleFileUpload(item.id, 'evidence_photos', e.target.files)}
                              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Upload Counter-Evidence Documents
                            </label>
                            <input
                              type="file"
                              multiple
                              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                              onChange={(e) => handleFileUpload(item.id, 'evidence_documents', e.target.files)}
                              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Landlord view - show status only */}
                  {isLandlord() && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-700 mb-2">Status</h4>
                      <p className="text-sm text-gray-600">
                        Waiting for tenant response by {new Date(pageData?.response_deadline).toLocaleDateString()}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                {isLandlord() ? 'Claim Summary' : 'Response Summary'}
              </h3>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Claimed:</span>
                  <span className="font-medium text-red-600">RM {totalClaimedAmount.toFixed(2)}</span>
                </div>
                {isTenant() && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Amount Accepted:</span>
                      <span className="font-medium text-green-600">RM {totalAccepted.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Amount Disputed:</span>
                      <span className="font-medium text-orange-600">RM {totalDisputed.toFixed(2)}</span>
                    </div>
                    <div className="border-t pt-3">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium text-gray-900">Estimated Refund:</span>
                        <span className="font-bold text-blue-600">
                          RM {(pageData.deposit_amount - totalAccepted).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </>
                )}
                {isLandlord() && (
                  <div className="border-t pt-3">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium text-gray-900">Status:</span>
                      <span className="font-medium text-orange-600">Pending Response</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {isTenant() && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Actions</h3>

                <div className="space-y-3">
                  <button
                    onClick={submitResponse}
                    disabled={!isValid || submitting}
                    className={`w-full py-2 px-4 rounded-md text-sm font-medium ${
                      isValid && !submitting
                        ? 'bg-blue-500 hover:bg-blue-600 text-white'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    {submitting ? 'Submitting...' : 'Submit Response to Landlord'}
                  </button>
                </div>
              </div>
            )}

            {isLandlord() && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Information</h3>
                <div className="text-sm text-gray-600 space-y-2">
                  <p>• The tenant has until <strong>{new Date(pageData?.response_deadline).toLocaleDateString()}</strong> to respond</p>
                  <p>• You will be notified when the tenant submits their response</p>
                  <p>• Any disputed amounts will go to mediation</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DepositDisputePage;