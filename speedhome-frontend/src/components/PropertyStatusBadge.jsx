import React from 'react';

const PropertyStatusBadge = ({ status, availableFromDate = null, size = 'sm' }) => {
  const getStatusConfig = (status) => {
    switch (status) {
      case 'Active':
        return {
          color: 'bg-green-100 text-green-800 border-green-200',
          icon: '✓',
          label: 'Active'
        };
      case 'Pending':
        return {
          color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: '⏳',
          label: 'Pending'
        };
      case 'Rented':
        return {
          color: 'bg-blue-100 text-blue-800 border-blue-200',
          icon: '🏠',
          label: 'Rented'
        };
      case 'Inactive':
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '⏸️',
          label: 'Inactive'
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '?',
          label: status || 'Unknown'
        };
    }
  };

  const config = getStatusConfig(status);
  
  const sizeClasses = {
    xs: 'px-1.5 py-0.5 text-xs',
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  const formatAvailableDate = (dateStr) => {
    if (!dateStr) return null;
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
      });
    } catch (e) {
      return null;
    }
  };

  return (
    <div className="flex flex-col items-start space-y-1">
      <span 
        className={`
          inline-flex items-center font-semibold rounded-full border
          ${config.color} ${sizeClasses[size]}
        `}
      >
        <span className="mr-1">{config.icon}</span>
        {config.label}
      </span>
      
      {availableFromDate && status === 'Active' && (
        <span className="text-xs text-gray-500">
          Available from {formatAvailableDate(availableFromDate)}
        </span>
      )}
    </div>
  );
};

export default PropertyStatusBadge;

