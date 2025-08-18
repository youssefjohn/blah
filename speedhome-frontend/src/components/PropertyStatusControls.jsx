import React, { useState } from 'react';

const PropertyStatusControls = ({ 
  property, 
  onStatusChange, 
  onRelistProperty,
  disabled = false 
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showRelistModal, setShowRelistModal] = useState(false);
  const [relistDate, setRelistDate] = useState('');

  const handleStatusChange = async (newStatus) => {
    if (disabled || isLoading) return;
    
    setIsLoading(true);
    try {
      await onStatusChange(property.id, newStatus);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRelistSubmit = async (e) => {
    e.preventDefault();
    if (!relistDate || isLoading) return;

    setIsLoading(true);
    try {
      await onRelistProperty(property.id, relistDate);
      setShowRelistModal(false);
      setRelistDate('');
    } finally {
      setIsLoading(false);
    }
  };

  const getAvailableActions = () => {
    const actions = [];
    
    switch (property.status) {
      case 'Active':
        actions.push({
          label: 'Deactivate',
          action: () => handleStatusChange('Inactive'),
          color: 'text-gray-600 hover:text-gray-800',
          icon: '⏸️'
        });
        break;
        
      case 'Inactive':
        actions.push({
          label: 'Re-activate Listing',
          action: () => handleStatusChange('Active'),
          color: 'text-green-600 hover:text-green-800',
          icon: '✅'
        });
        break;
        
      case 'Rented':
        actions.push({
          label: 'Find New Tenant',
          action: () => setShowRelistModal(true),
          color: 'text-blue-600 hover:text-blue-800',
          icon: '🔄'
        });
        break;
        
      case 'Pending':
        // No manual actions available during pending state
        break;
        
      default:
        break;
    }
    
    return actions;
  };

  const actions = getAvailableActions();

  if (actions.length === 0) {
    return (
      <div className="text-xs text-gray-400">
        {property.status === 'Pending' ? 'Agreement in progress' : 'No actions available'}
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-col space-y-1">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={action.action}
            disabled={disabled || isLoading}
            className={`
              text-xs font-medium transition-colors duration-200
              ${action.color}
              ${disabled || isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <span className="mr-1">{action.icon}</span>
            {isLoading ? 'Loading...' : action.label}
          </button>
        ))}
      </div>

      {/* Relist Modal */}
      {showRelistModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Find New Tenant
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Set when this property will be available for new tenants:
              </p>
              
              <form onSubmit={handleRelistSubmit}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Available From Date
                  </label>
                  <input
                    type="date"
                    value={relistDate}
                    onChange={(e) => setRelistDate(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Property will be re-listed and visible to tenants from this date
                  </p>
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowRelistModal(false);
                      setRelistDate('');
                    }}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                    disabled={isLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                    disabled={isLoading || !relistDate}
                  >
                    {isLoading ? 'Re-listing...' : 'Re-list Property'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PropertyStatusControls;

