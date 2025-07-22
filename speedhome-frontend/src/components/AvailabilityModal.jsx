import React, { useState, useEffect } from 'react';
import PropertyAPI from '../services/PropertyAPI';
import { useAuth } from '../contexts/AuthContext';

const AvailabilityModal = ({ onClose, onSuccess }) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // State for the weekly schedule with memory functionality
  const [schedule, setSchedule] = useState(() => {
    // Try to load from localStorage first
    const savedSchedule = localStorage.getItem(`landlord_availability_${user?.id}`);
    if (savedSchedule) {
      return JSON.parse(savedSchedule);
    }
    
    // Default schedule if no saved data
    return {
      monday: { enabled: false, from: '09:00', to: '17:00' },
      tuesday: { enabled: false, from: '09:00', to: '17:00' },
      wednesday: { enabled: false, from: '09:00', to: '17:00' },
      thursday: { enabled: false, from: '09:00', to: '17:00' },
      friday: { enabled: false, from: '09:00', to: '17:00' },
      saturday: { enabled: false, from: '09:00', to: '17:00' },
      sunday: { enabled: false, from: '09:00', to: '17:00' }
    };
  });
  
  // State for date range with memory functionality
  const [dateRange, setDateRange] = useState(() => {
    const savedDateRange = localStorage.getItem(`landlord_daterange_${user?.id}`);
    if (savedDateRange) {
      return JSON.parse(savedDateRange);
    }
    
    // Default to next 30 days
    const today = new Date();
    const nextMonth = new Date();
    nextMonth.setDate(today.getDate() + 30);
    
    return {
      startDate: today.toISOString().split('T')[0],
      endDate: nextMonth.toISOString().split('T')[0]
    };
  });

  // State for properties
  const [properties, setProperties] = useState([]);
  const [selectedProperties, setSelectedProperties] = useState(() => {
    const savedProperties = localStorage.getItem(`landlord_selected_properties_${user?.id}`);
    if (savedProperties) {
      return JSON.parse(savedProperties);
    }
    return [];
  });

  // Load landlord's properties
  useEffect(() => {
    const loadProperties = async () => {
      if (!user) return;
      
      try {
        const result = await PropertyAPI.getPropertiesByOwner(user.id);
        if (result.success) {
          setProperties(result.properties);
          
          // If no properties are selected yet, select all by default
          if (selectedProperties.length === 0) {
            const allPropertyIds = result.properties.map(p => p.id);
            setSelectedProperties(allPropertyIds);
          }
        }
      } catch (error) {
        console.error('Error loading properties:', error);
      }
    };

    loadProperties();
  }, [user]);

  // Save to localStorage whenever state changes
  useEffect(() => {
    if (user) {
      localStorage.setItem(`landlord_availability_${user.id}`, JSON.stringify(schedule));
    }
  }, [schedule, user]);

  useEffect(() => {
    if (user) {
      localStorage.setItem(`landlord_daterange_${user.id}`, JSON.stringify(dateRange));
    }
  }, [dateRange, user]);

  useEffect(() => {
    if (user) {
      localStorage.setItem(`landlord_selected_properties_${user.id}`, JSON.stringify(selectedProperties));
    }
  }, [selectedProperties, user]);

  const daysOfWeek = [
    { key: 'monday', label: 'Monday' },
    { key: 'tuesday', label: 'Tuesday' },
    { key: 'wednesday', label: 'Wednesday' },
    { key: 'thursday', label: 'Thursday' },
    { key: 'friday', label: 'Friday' },
    { key: 'saturday', label: 'Saturday' },
    { key: 'sunday', label: 'Sunday' }
  ];

  // Handle day checkbox toggle
  const handleDayToggle = (day) => {
    setSchedule(prev => ({
      ...prev,
      [day]: {
        ...prev[day],
        enabled: !prev[day].enabled
      }
    }));
  };

  // Handle time change for a specific day
  const handleTimeChange = (day, timeType, value) => {
    setSchedule(prev => ({
      ...prev,
      [day]: {
        ...prev[day],
        [timeType]: value
      }
    }));
  };

  // Handle date range change
  const handleDateRangeChange = (field, value) => {
    setDateRange(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle property selection
  const handlePropertyToggle = (propertyId) => {
    setSelectedProperties(prev => {
      if (prev.includes(propertyId)) {
        return prev.filter(id => id !== propertyId);
      } else {
        return [...prev, propertyId];
      }
    });
  };

  // Select/Deselect all properties
  const handleSelectAllProperties = () => {
    if (selectedProperties.length === properties.length) {
      setSelectedProperties([]);
    } else {
      setSelectedProperties(properties.map(p => p.id));
    }
  };

  // Validate form data
  const validateForm = () => {
    // Check if at least one day is selected
    const hasEnabledDay = Object.values(schedule).some(day => day.enabled);
    if (!hasEnabledDay) {
      setError('Please select at least one day of the week.');
      return false;
    }

    // Check if at least one property is selected
    if (selectedProperties.length === 0) {
      setError('Please select at least one property.');
      return false;
    }

    // Check if date range is provided
    if (!dateRange.startDate || !dateRange.endDate) {
      setError('Please provide both start and end dates.');
      return false;
    }

    // Check if end date is after start date
    if (new Date(dateRange.endDate) <= new Date(dateRange.startDate)) {
      setError('End date must be after start date.');
      return false;
    }

    // Validate time ranges for enabled days
    for (const [day, config] of Object.entries(schedule)) {
      if (config.enabled) {
        if (config.from >= config.to) {
          setError(`Invalid time range for ${day}. End time must be after start time.`);
          return false;
        }
      }
    }

    return true;
  };

  // Format schedule data for API
  const formatScheduleData = () => {
    // Convert enabled days to object format expected by backend
    const scheduleObject = {};
    
    Object.entries(schedule).forEach(([day, config]) => {
      if (config.enabled) {
        scheduleObject[day] = {
          from: config.from,
          to: config.to
        };
      }
    });

    return {
      schedule: scheduleObject,
      start_date: dateRange.startDate,
      end_date: dateRange.endDate
    };
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const scheduleData = formatScheduleData();
      
      // Call API for each selected property
      let totalSlotsCreated = 0;
      
      for (const propertyId of selectedProperties) {
        const result = await PropertyAPI.addRecurringAvailability(propertyId, scheduleData);
        if (result.success) {
          totalSlotsCreated += result.slots_created || 0;
        } else {
          throw new Error(result.error || 'Failed to set availability');
        }
      }

      if (onSuccess) {
        onSuccess({ 
          slots_created: totalSlotsCreated,
          properties_updated: selectedProperties.length
        });
      }
      
      onClose();
    } catch (error) {
      console.error('Error setting availability:', error);
      setError(error.message || 'Failed to set availability. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Set Your Availability</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Property Selection */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700">
                  Select Properties
                </label>
                <button
                  type="button"
                  onClick={handleSelectAllProperties}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  {selectedProperties.length === properties.length ? 'Deselect All' : 'Select All'}
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-32 overflow-y-auto border rounded-lg p-3">
                {properties.map(property => (
                  <label key={property.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={selectedProperties.includes(property.id)}
                      onChange={() => handlePropertyToggle(property.id)}
                      className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                    />
                    <span className="text-sm text-gray-700 truncate">{property.title}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={dateRange.startDate}
                  onChange={(e) => handleDateRangeChange('startDate', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={dateRange.endDate}
                  onChange={(e) => handleDateRangeChange('endDate', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  required
                />
              </div>
            </div>

            {/* Weekly Schedule */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Weekly Schedule
              </label>
              <div className="space-y-3">
                {daysOfWeek.map(({ key, label }) => (
                  <div key={key} className="flex items-center space-x-4 p-3 border rounded-lg">
                    <label className="flex items-center space-x-2 min-w-[100px]">
                      <input
                        type="checkbox"
                        checked={schedule[key].enabled}
                        onChange={() => handleDayToggle(key)}
                        className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                      />
                      <span className="text-sm font-medium text-gray-700">{label}</span>
                    </label>
                    
                    {schedule[key].enabled && (
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600">From:</span>
                        <input
                          type="time"
                          value={schedule[key].from}
                          onChange={(e) => handleTimeChange(key, 'from', e.target.value)}
                          className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-green-500 focus:border-green-500"
                        />
                        <span className="text-sm text-gray-600">To:</span>
                        <input
                          type="time"
                          value={schedule[key].to}
                          onChange={(e) => handleTimeChange(key, 'to', e.target.value)}
                          className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-green-500 focus:border-green-500"
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Setting Availability...' : 'Set Availability'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AvailabilityModal;

