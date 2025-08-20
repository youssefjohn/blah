import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DepositDisputePage = () => {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const { user, isTenant } = useAuth();
  
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  
  const [responses, setResponses] = useState({});
  const [counterEvidence, setCounterEvidence] = useState({});

  useEffect(() => {
    if (!isTenant()) {
      navigate('/dashboard');
      return;
    }
    loadClaimData();
  }, [claimId]);

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
        setClaim(data.claim);
        // Initialize responses for each claim item
        const initialResponses = {};
        data.claim.items.forEach(item => {
          initialResponses[item.id] = {
            response: '',
            counter_amount: '',
            explanation: '',
            evidence_photos: [],
            evidence_documents: []
          };
        });
        setResponses(initialResponses);
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
    // In a real implementation, you would upload files to S3 or similar
    const fileNames = Array.from(files).map(file => file.name);
    updateResponse(itemId, field, fileNames);
  };

  const calculateTotalAccepted = () => {
    if (!claim) return 0;
    return claim.items.reduce((total, item) => {
      const response = responses[item.id];
      if (response?.response === 'accept') {
        return total + item.amount;
      } else if (response?.response === 'partial_accept') {
        return total + (parseFloat(response.counter_amount) || 0);
      }
      return total;
    }, 0);
  };

  const calculateTotalDisputed = () => {
    if (!claim) return 0;
    return claim.items.reduce((total, item) => {
      const response = responses[item.id];
      if (response?.response === 'reject') {
        return total + item.amount;
      } else if (response?.response === 'partial_accept') {
        return total + (item.amount - (parseFloat(response.counter_amount) || 0));
      }
      return total;
    }, 0);
  };

  const validateResponses = () => {
    for (const item of claim.items) {
      const response = responses[item.id];
      if (!response?.response) {
        return false;
      }
      if (response.response === 'partial_accept') {
        if (!response.counter_amount || parseFloat(response.counter_amount) <= 0) {
          return false;
        }
        if (parseFloat(response.counter_amount) >= item.amount) {
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
            item_id: parseInt(itemId),
            response: response.response,
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

  if (error || !claim) {
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
              <h1 className="text-2xl font-bold text-gray-900">Review Your Landlord's Deposit Claims</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Claim Overview */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Claim Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Property Address</span>
                  <p className="text-gray-900">{claim.property_address}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Landlord</span>
                  <p className="text-gray-900">{claim.landlord_name}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Claim Submitted</span>
                  <p className="text-gray-900">{new Date(claim.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Response Deadline</span>
                  <p className="text-red-600 font-medium">{new Date(claim.response_deadline).toLocaleDateString()}</p>
                </div>
              </div>
            </div>

            {/* Instructions */}
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

            {/* Claim Items */}
            <div className="space-y-6">
              {claim.items.map((item, index) => (
                <div key={item.id} className="bg-white shadow rounded-lg p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      Item {index + 1}: {item.reason_display}
                    </h3>
                    <span className="text-xl font-bold text-red-600">RM {item.amount}</span>
                  </div>

                  <p className="text-gray-600 mb-4">{item.description}</p>

                  {/* Landlord's Evidence */}
                  {(item.evidence_photos?.length > 0 || item.evidence_documents?.length > 0) && (
                    <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">Landlord's Evidence:</h4>
                      {item.evidence_photos?.length > 0 && (
                        <p className="text-sm text-gray-600">📷 {item.evidence_photos.length} photo(s)</p>
                      )}
                      {item.evidence_documents?.length > 0 && (
                        <p className="text-sm text-gray-600">📄 {item.evidence_documents.length} document(s)</p>
                      )}
                      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium mt-1">
                        View Landlord's Evidence →
                      </button>
                    </div>
                  )}

                  {/* Response Options */}
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

                    {/* Counter Amount for Partial Accept */}
                    {responses[item.id]?.response === 'partial_accept' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Amount You Agree To Pay (RM) *
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          min="0.01"
                          max={item.amount - 0.01}
                          value={responses[item.id]?.counter_amount || ''}
                          onChange={(e) => updateResponse(item.id, 'counter_amount', e.target.value)}
                          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                          placeholder="0.00"
                          required
                        />
                      </div>
                    )}

                    {/* Explanation for Disagree or Partial Accept */}
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

                    {/* Counter Evidence Upload */}
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
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar Summary */}
          <div>
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Response Summary</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Claimed:</span>
                  <span className="font-medium text-red-600">RM {claim.total_amount}</span>
                </div>
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
                      RM {(claim.deposit_amount - totalAccepted).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            </div>

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

                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-xs text-yellow-700">
                    ⏰ You have until {new Date(claim.response_deadline).toLocaleDateString()} to respond. 
                    Accepted amounts will be deducted immediately. Disputed amounts will go to mediation.
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

export default DepositDisputePage;

