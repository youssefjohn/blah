import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DepositResolutionPage = () => {
  const { disputeId } = useParams();
  const navigate = useNavigate();
  const { user, isLandlord, isTenant } = useAuth();
  
  const [dispute, setDispute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    loadDisputeData();
    loadMessages();
  }, [disputeId]);

  const loadDisputeData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/deposits/disputes/${disputeId}`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to load dispute data');
      }
      
      const data = await response.json();
      if (data.success) {
        setDispute(data.dispute);
      } else {
        setError(data.error || 'Failed to load dispute');
      }
    } catch (err) {
      setError('Failed to load dispute data');
      console.error('Error loading dispute:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async () => {
    try {
      const response = await fetch(`/api/deposits/disputes/${disputeId}/messages`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setMessages(data.messages || []);
        }
      }
    } catch (err) {
      console.error('Error loading messages:', err);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    try {
      setSending(true);
      const response = await fetch(`/api/deposits/disputes/${disputeId}/messages`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: newMessage.trim()
        })
      });

      const result = await response.json();
      if (result.success) {
        setNewMessage('');
        await loadMessages();
      } else {
        alert(result.error || 'Failed to send message');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const escalateToMediation = async () => {
    try {
      const response = await fetch(`/api/deposits/disputes/${disputeId}/escalate`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const result = await response.json();
      if (result.success) {
        alert('Case escalated to platform mediation. Our team will review and contact you within 2 business days.');
        await loadDisputeData();
      } else {
        alert(result.error || 'Failed to escalate case');
      }
    } catch (err) {
      console.error('Error escalating case:', err);
      alert('Failed to escalate case');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-600">Loading dispute information...</p>
        </div>
      </div>
    );
  }

  if (error || !dispute) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Dispute</h2>
          <p className="text-gray-600 mb-4">{error || 'Dispute not found'}</p>
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

  const canEscalate = dispute.status === 'under_mediation' && !dispute.escalated_at;
  const isResolved = dispute.status === 'resolved';

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
              <h1 className="text-2xl font-bold text-gray-900">Deposit Resolution</h1>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getDisputeStatusColor(dispute.status)}`}>
                {getDisputeStatusText(dispute.status)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Dispute Overview */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Dispute Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Property Address</span>
                  <p className="text-gray-900">{dispute.property_address}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Dispute Created</span>
                  <p className="text-gray-900">{new Date(dispute.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Total Disputed Amount</span>
                  <p className="text-2xl font-bold text-red-600">RM {dispute.disputed_amount}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Mediation Deadline</span>
                  <p className="text-orange-600 font-medium">{new Date(dispute.mediation_deadline).toLocaleDateString()}</p>
                </div>
              </div>
            </div>

            {/* Disputed Items */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Disputed Items</h3>
              <div className="space-y-4">
                {dispute.claim_items?.filter(item => item.tenant_response !== 'accept').map((item, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-gray-900">{item.reason_display}</h4>
                      <div className="text-right">
                        <p className="text-lg font-bold text-red-600">RM {item.amount}</p>
                        {item.tenant_response === 'partial_accept' && (
                          <p className="text-sm text-green-600">Tenant offers: RM {item.tenant_counter_amount}</p>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{item.description}</p>
                    
                    {/* Landlord's Position */}
                    <div className="bg-red-50 p-3 rounded-lg mb-3">
                      <h5 className="font-medium text-red-800 mb-1">Landlord's Position:</h5>
                      <p className="text-sm text-red-700">{item.description}</p>
                      {item.evidence_photos?.length > 0 && (
                        <p className="text-xs text-red-600 mt-1">📷 {item.evidence_photos.length} photo(s) provided</p>
                      )}
                    </div>

                    {/* Tenant's Response */}
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <h5 className="font-medium text-blue-800 mb-1">Tenant's Response:</h5>
                      <p className="text-sm text-blue-700">
                        <strong>{item.tenant_response === 'reject' ? 'Disagrees' : 'Partially Agrees'}:</strong> {item.tenant_explanation}
                      </p>
                      {item.tenant_evidence_photos?.length > 0 && (
                        <p className="text-xs text-blue-600 mt-1">📷 {item.tenant_evidence_photos.length} counter-evidence photo(s)</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Resolution Status */}
            {isResolved && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-bold text-green-800 mb-4">✅ Dispute Resolved</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-green-600">Final Resolution Amount</span>
                    <p className="text-2xl font-bold text-green-800">RM {dispute.final_resolution_amount}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-green-600">Resolved On</span>
                    <p className="text-green-800">{new Date(dispute.resolved_at).toLocaleDateString()}</p>
                  </div>
                  {dispute.resolution_notes && (
                    <div className="md:col-span-2">
                      <span className="text-sm font-medium text-green-600">Resolution Notes</span>
                      <p className="text-green-700">{dispute.resolution_notes}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Communication Thread */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Discussion Thread</h3>
              
              {/* Messages */}
              <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
                {messages.length > 0 ? (
                  messages.map((message, index) => (
                    <div key={index} className={`flex ${message.sender_id === user.id ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.sender_id === user.id
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-900'
                      }`}>
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.sender_id === user.id ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {message.sender_name} • {new Date(message.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-8">No messages yet. Start the discussion below.</p>
                )}
              </div>

              {/* Message Input */}
              {!isResolved && (
                <div className="flex space-x-3">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm"
                    rows="3"
                    placeholder="Type your message here..."
                    disabled={sending}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!newMessage.trim() || sending}
                    className={`px-4 py-2 rounded-md text-sm font-medium ${
                      newMessage.trim() && !sending
                        ? 'bg-blue-500 hover:bg-blue-600 text-white'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    {sending ? 'Sending...' : 'Send'}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar Actions */}
          <div>
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Resolution Actions</h3>
              
              <div className="space-y-3">
                {canEscalate && (
                  <button
                    onClick={escalateToMediation}
                    className="w-full bg-orange-500 hover:bg-orange-600 text-white py-2 px-4 rounded-md text-sm font-medium"
                  >
                    🏛️ Escalate to Platform Mediation
                  </button>
                )}

                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">💡 Resolution Tips</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Try to reach a mutual agreement through discussion</li>
                    <li>• Provide clear evidence to support your position</li>
                    <li>• Consider compromise solutions</li>
                    <li>• Escalate to mediation if no agreement is reached</li>
                  </ul>
                </div>

                {dispute.mediation_deadline && !isResolved && (
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-medium text-yellow-900 mb-2">⏰ Timeline</h4>
                    <p className="text-sm text-yellow-700">
                      Mediation deadline: {new Date(dispute.mediation_deadline).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-yellow-600 mt-1">
                      If no resolution is reached, the case will be automatically escalated.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Refund Calculation */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Refund Calculation</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Original Deposit:</span>
                  <span className="font-medium">RM {dispute.deposit_amount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Accepted Deductions:</span>
                  <span className="font-medium text-red-600">-RM {dispute.accepted_amount || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Disputed Amount:</span>
                  <span className="font-medium text-orange-600">RM {dispute.disputed_amount}</span>
                </div>
                <div className="border-t pt-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-900">
                      {isResolved ? 'Final Refund:' : 'Minimum Refund:'}
                    </span>
                    <span className="font-bold text-green-600">
                      RM {isResolved 
                        ? (dispute.deposit_amount - dispute.final_resolution_amount).toFixed(2)
                        : (dispute.deposit_amount - (dispute.accepted_amount || 0) - dispute.disputed_amount).toFixed(2)
                      }
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper functions
const getDisputeStatusColor = (status) => {
  switch (status) {
    case 'under_mediation':
      return 'bg-yellow-100 text-yellow-800';
    case 'escalated':
      return 'bg-orange-100 text-orange-800';
    case 'resolved':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getDisputeStatusText = (status) => {
  switch (status) {
    case 'under_mediation':
      return 'Under Mediation';
    case 'escalated':
      return 'Escalated to Platform';
    case 'resolved':
      return 'Resolved';
    default:
      return status;
  }
};

export default DepositResolutionPage;

