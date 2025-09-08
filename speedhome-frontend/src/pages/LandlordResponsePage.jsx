import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const LandlordResponsePage = () => {
  const { depositId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [deposit, setDeposit] = useState(null);
  const [disputedClaims, setDisputedClaims] = useState([]);
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [viewingEvidence, setViewingEvidence] = useState(null); // For evidence modal

  useEffect(() => {
    fetchDepositDetails();
  }, [depositId]);

  const fetchDepositDetails = async () => {
    try {
      const response = await fetch(`/api/deposits/agreement/${depositId}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setDeposit(data.deposit);
          
          // Filter only disputed claims
          const disputed = data.deposit.claims.filter(claim => claim.status === 'disputed');
          setDisputedClaims(disputed);
          
          // Initialize responses state
          const initialResponses = {};
          disputed.forEach(claim => {
            initialResponses[claim.id] = {
              response: '', // 'accept_counter', 'reject_counter', 'escalate'
              landlord_notes: ''
            };
          });
          setResponses(initialResponses);
        } else {
          console.error('Failed to fetch deposit details:', data.error);
        }
      } else {
        console.error('Failed to fetch deposit details');
      }
    } catch (error) {
      console.error('Error fetching deposit details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResponseChange = (claimId, field, value) => {
    setResponses(prev => ({
      ...prev,
      [claimId]: {
        ...prev[claimId],
        [field]: value
      }
    }));
  };

  const formatClaimType = (title) => {
    if (!title) return 'Other';
    return title.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const submitLandlordResponse = async () => {
    setSubmitting(true);
    
    try {
      const responseData = {
        responses: Object.entries(responses).map(([claimId, response]) => ({
          claim_id: parseInt(claimId),
          response: response.response,
          landlord_notes: response.landlord_notes
        }))
      };

      console.log('Submitting landlord response:', responseData);
      console.log('Response details:', JSON.stringify(responseData, null, 2));

      const response = await fetch(`/api/deposits/${depositId}/landlord-respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(responseData)
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      // Handle both successful responses and redirects (302)
      if (response.ok || response.status === 302) {
        console.log('Response successful, processing result...');
        const result = await response.json();
        
        if (result.success) {
          alert('Response submitted successfully!');
          
          // Use the redirect URL provided by the backend
          if (result.redirect_url) {
            console.log('Redirecting to:', result.redirect_url);
            navigate(result.redirect_url);
          } else {
            // Fallback to deposit management
            navigate(`/deposit/${depositId}/manage`);
          }
        } else {
          alert(`Error: ${result.message || 'Failed to submit response'}`);
        }
      } else {
        console.error('Response failed with status:', response.status);
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        alert(`Error: ${errorData.message || 'Failed to submit response'}`);
      }
    } catch (error) {
      console.error('Error submitting response:', error);
      alert('Error submitting response. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const canSubmit = () => {
    return Object.values(responses).every(response => response.response !== '');
  };

  const handleViewEvidence = (claim) => {
    setViewingEvidence(claim);
  };

  const closeEvidenceModal = () => {
    setViewingEvidence(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dispute details...</p>
        </div>
      </div>
    );
  }

  if (!deposit || disputedClaims.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">No Disputes Found</h2>
          <p className="text-gray-600 mb-6">There are no disputed claims to respond to.</p>
          <button
            onClick={() => navigate(`/deposit/${depositId}/manage`)}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md"
          >
            Back to Deposit Management
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(`/deposit/${depositId}/manage`)}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
          >
            ← Back to Deposit Management
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Respond to Tenant Disputes</h1>
          <p className="mt-2 text-gray-600">
            Review the tenant's responses and decide how to proceed with each disputed claim.
          </p>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="font-medium text-blue-900 mb-2">Instructions:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Review each tenant response carefully</li>
            <li>• You can accept their counter-offer or escalate to mediation</li>
            <li>• Add notes to explain your decision</li>
            <li>• All disputed claims must be addressed before submitting</li>
          </ul>
        </div>

        {/* Disputed Claims */}
        <div className="space-y-6">
          {disputedClaims.map((claim, index) => (
            <div key={claim.id} className="bg-white shadow rounded-lg p-6">
              <div className="border-b border-gray-200 pb-4 mb-4">
                <h3 className="text-lg font-bold text-gray-900">
                  Item {index + 1}: {formatClaimType(claim.title)}
                </h3>
                <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Your Original Claim:</span> RM {claim.claimed_amount}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Your Comments:</span> {claim.description}
                    </p>
                  </div>
                  <div>
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                      Disputed by Tenant
                    </span>
                  </div>
                </div>
              </div>

              {/* Tenant Response Details */}
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Tenant's Response:</h4>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <span className={`text-sm font-medium ${
                      claim.tenant_response === 'partial_accept' ? 'text-orange-600' : 'text-red-600'
                    }`}>
                      {claim.tenant_response === 'partial_accept' 
                        ? '⚖️ Partial Accept - Offered different amount'
                        : '❌ Rejected - Completely disputed this charge'
                      }
                    </span>
                  </div>
                  
                  {claim.tenant_response === 'partial_accept' && claim.tenant_counter_amount && (
                    <div className="text-sm">
                      <span className="font-medium text-orange-800">Counter-Offer:</span>
                      <span className="ml-1 font-bold text-orange-600">RM {parseFloat(claim.tenant_counter_amount).toFixed(2)}</span>
                    </div>
                  )}
                  
                  {claim.tenant_explanation && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700">Tenant's Explanation:</span>
                      <p className="mt-1 text-gray-600 italic">"{claim.tenant_explanation}"</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Tenant Counter-Evidence Section */}
              {(claim.tenant_evidence_photos?.length > 0 || claim.tenant_evidence_documents?.length > 0) && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                  <h4 className="font-medium text-yellow-800 mb-2">Tenant's Counter-Evidence:</h4>
                  <div className="space-y-1">
                    {claim.tenant_evidence_photos?.length > 0 && (
                      <p className="text-sm text-yellow-700">📷 {claim.tenant_evidence_photos.length} photo(s)</p>
                    )}
                    {claim.tenant_evidence_documents?.length > 0 && (
                      <p className="text-sm text-yellow-700">📄 {claim.tenant_evidence_documents.length} document(s)</p>
                    )}
                    <button 
                      onClick={() => handleViewEvidence(claim)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium mt-1 cursor-pointer"
                    >
                      View Tenant's Evidence →
                    </button>
                  </div>
                </div>
              )}

              {/* Landlord Response Options */}
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Your Response:</h4>
                
                <div className="space-y-3">
                  {claim.tenant_response === 'partial_accept' && (
                    <label className="flex items-start">
                      <input
                        type="radio"
                        name={`response_${claim.id}`}
                        value="accept_counter"
                        checked={responses[claim.id]?.response === 'accept_counter'}
                        onChange={(e) => handleResponseChange(claim.id, 'response', e.target.value)}
                        className="mt-1 mr-3"
                      />
                      <div>
                        <span className="text-green-600 font-medium">✅ Accept Counter-Offer</span>
                        <p className="text-sm text-gray-600">
                          Accept the tenant's offer of RM {claim.tenant_counter_amount}
                        </p>
                      </div>
                    </label>
                  )}
                  
                  <label className="flex items-start">
                    <input
                      type="radio"
                      name={`response_${claim.id}`}
                      value="escalate"
                      checked={responses[claim.id]?.response === 'escalate'}
                      onChange={(e) => handleResponseChange(claim.id, 'response', e.target.value)}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <span className="text-purple-600 font-medium">⚖️ Escalate to Mediation</span>
                      <p className="text-sm text-gray-600">
                        Let a neutral third party resolve this dispute
                      </p>
                    </div>
                  </label>
                </div>

                {/* Landlord Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Notes (Optional)
                  </label>
                  <textarea
                    value={responses[claim.id]?.landlord_notes || ''}
                    onChange={(e) => handleResponseChange(claim.id, 'landlord_notes', e.target.value)}
                    placeholder="Explain your decision or provide additional context..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Submit Button */}
        <div className="mt-8 flex justify-end">
          <button
            onClick={submitLandlordResponse}
            disabled={!canSubmit() || submitting}
            className={`px-6 py-3 rounded-md font-medium ${
              canSubmit() && !submitting
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {submitting ? 'Submitting...' : 'Submit Response'}
          </button>
        </div>
      </div>

      {/* Evidence Viewing Modal */}
      {viewingEvidence && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] w-full flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">
                Tenant's Counter-Evidence: {formatClaimType(viewingEvidence.title)}
              </h3>
              <button
                onClick={closeEvidenceModal}
                className="h-8 w-8 flex items-center justify-center text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 p-4 overflow-auto">
              {/* Photos Section */}
              {viewingEvidence.tenant_evidence_photos && viewingEvidence.tenant_evidence_photos.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">📷 Photos ({viewingEvidence.tenant_evidence_photos.length})</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {viewingEvidence.tenant_evidence_photos.map((photo, index) => (
                      <div key={index} className="border rounded-lg overflow-hidden">
                        <img
                          src={`/api/deposits/evidence/view/${photo.split('/').pop()}`}
                          alt={`Tenant evidence photo ${index + 1}`}
                          className="w-full h-48 object-cover cursor-pointer hover:opacity-90"
                          onClick={() => window.open(`/api/deposits/evidence/view/${photo.split('/').pop()}`, '_blank')}
                        />
                        <div className="p-2 bg-gray-50">
                          <p className="text-xs text-gray-600 truncate">{photo.split('/').pop()}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Documents Section */}
              {viewingEvidence.tenant_evidence_documents && viewingEvidence.tenant_evidence_documents.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">📄 Documents ({viewingEvidence.tenant_evidence_documents.length})</h4>
                  <div className="space-y-2">
                    {viewingEvidence.tenant_evidence_documents.map((document, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                        <div className="flex items-center space-x-3">
                          <div className="text-red-500">📄</div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{document.split('/').pop()}</p>
                            <p className="text-xs text-gray-500">PDF Document</p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => window.open(`/api/deposits/evidence/view/${document.split('/').pop()}`, '_blank')}
                            className="px-3 py-1 text-sm bg-blue-100 text-blue-700 hover:bg-blue-200 rounded"
                          >
                            View
                          </button>
                          <button
                            onClick={() => {
                              const link = document.createElement('a');
                              link.href = `/api/deposits/evidence/download/${document.split('/').pop()}`;
                              link.download = document.split('/').pop();
                              link.click();
                            }}
                            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 hover:bg-gray-200 rounded"
                          >
                            Download
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* No Evidence Message */}
              {(!viewingEvidence.tenant_evidence_photos || viewingEvidence.tenant_evidence_photos.length === 0) &&
               (!viewingEvidence.tenant_evidence_documents || viewingEvidence.tenant_evidence_documents.length === 0) && (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">📁</div>
                  <p>The tenant did not upload any counter-evidence for this claim.</p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end p-4 border-t">
              <button
                onClick={closeEvidenceModal}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandlordResponsePage;

