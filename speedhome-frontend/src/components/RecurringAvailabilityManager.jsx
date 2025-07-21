import React, { useState } from 'react';
import PropertyAPI from '../services/PropertyAPI';

const RecurringAvailabilityManager = ({ propertyId, onClose, onSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // State for the weekly schedule
  const [schedule, setSchedule] = useState({
    monday: { enabled: false, from: '09:00', to: '17:00' },
    tuesday: { enabled: false, from: '09:00', to: '17:00' },
    wednesday: { enabled: false, from: '09:00', to: '17:00' },
    thursday: { enabled: false, from: '09:00', to: '17:00' },
    friday: { enabled: false, from: '09:00', to: '17:00' },
    saturday: { enabled: false, from: '09:00', to: '17:00' },
    sunday: { enabled: false, from: '09:00', to: '17:00' }
  });
  
  // State for date range
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: ''
  });

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

  // Validate form data
  const validateForm = () => {
    // Check if at least one day is selected
    const hasEnabledDay = Object.values(schedule).some(day => day.enabled);
    if (!hasEnabledDay) {
      setError('Please select at least one day of the week.');
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
    const enabledDays = {};
    
    Object.entries(schedule).forEach(([day, config]) => {
      if (config.enabled) {
        enabledDays[day] = {
          from: config.from,
          to: config.to
        };
      }
    });

    return {
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
      schedule: enabledDays
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
      const result = await PropertyAPI.addRecurringAvailability(propertyId, scheduleData);
      
      if (result.success) {
        onSuccess && onSuccess(result);
        onClose && onClose();
      } else {
        setError(result.error || 'Failed to set recurring availability');
      }
    } catch (error) {
      console.error('Error setting recurring availability:', error);
      setError('An error occurred while setting availability. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Get today's date in YYYY-MM-DD format for min date
  const getTodayDate = () => {
    return new Date().toISOString().split('T')[0];
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Manage Availability</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
              disabled={isLoading}
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
            {/* Weekly Schedule */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Schedule</h3>
              <div className="space-y-3">
                {daysOfWeek.map(({ key, label }) => (
                  <div key={key} className="flex items-center space-x-4">
                    {/* Day Checkbox */}
                    <div className="flex items-center min-w-[120px]">
                      <input
                        type="checkbox"
                        id={`day-${key}`}
                        checked={schedule[key].enabled}
                        onChange={() => handleDayToggle(key)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        disabled={isLoading}
                      />
                      <label htmlFor={`day-${key}`} className="ml-2 text-sm font-medium text-gray-700">
                        {label}
                      </label>
                    </div>

                    {/* Time Inputs - Only show when day is enabled */}
                    {schedule[key].enabled && (
                      <div className="flex items-center space-x-2 flex-1">
                        <span className="text-sm text-gray-600">From:</span>
                        <input
                          type="time"
                          value={schedule[key].from}
                          onChange={(e) => handleTimeChange(key, 'from', e.target.value)}
                          className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          disabled={isLoading}
                        />
                        <span className="text-sm text-gray-600">To:</span>
                        <input
                          type="time"
                          value={schedule[key].to}
                          onChange={(e) => handleTimeChange(key, 'to', e.target.value)}
                          className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          disabled={isLoading}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Date Range */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Date Range</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    id="start-date"
                    value={dateRange.startDate}
                    onChange={(e) => handleDateRangeChange('startDate', e.target.value)}
                    min={getTodayDate()}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isLoading}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    id="end-date"
                    value={dateRange.endDate}
                    onChange={(e) => handleDateRangeChange('endDate', e.target.value)}
                    min={dateRange.startDate || getTodayDate()}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isLoading}
              >
                {isLoading ? 'Setting Availability...' : 'Set Availability'}
              </button>
            </div>
          </form>

          {/* Info Box */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="text-sm font-semibold text-blue-900 mb-2">How it works:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Select the days of the week when you're available for viewings</li>
              <li>• Set your preferred time slots for each day</li>
              <li>• Choose the date range for this availability schedule</li>
              <li>• Tenants will be able to book 30-minute viewing slots during your available times</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecurringAvailabilityManager;

