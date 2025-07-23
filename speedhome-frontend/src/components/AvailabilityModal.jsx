import React, { useState, useEffect } from 'react';
import PropertyAPI from '../services/PropertyAPI';
import BookingAPI from '../services/BookingAPI';
import { useAuth } from '../contexts/AuthContext';

const AvailabilityModal = ({ onClose, onSuccess }) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // --- NEW STATE FOR CONFLICT MANAGEMENT ---
  const [view, setView] = useState('form'); // Can be 'form' or 'conflict'
  const [conflicts, setConflicts] = useState([]);
  const [scheduleDataToSubmit, setScheduleDataToSubmit] = useState(null); // To hold the data that caused the conflict

  // State for the weekly schedule with memory functionality
  const [schedule, setSchedule] = useState(() => {
    const savedSchedule = localStorage.getItem(`landlord_availability_${user?.id}`);
    if (savedSchedule) {
      return JSON.parse(savedSchedule);
    }
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
    const today = new Date();
    const nextMonth = new Date();
    nextMonth.setDate(today.getDate() + 30);
    return {
      startDate: today.toISOString().split('T')[0],
      endDate: nextMonth.toISOString().split('T')[0]
    };
  });

  // Save to localStorage whenever state changes
  useEffect(() => {
    if (user) {
      localStorage.setItem(`landlord_availability_${user.id}`, JSON.stringify(schedule));
      localStorage.setItem(`landlord_daterange_${user.id}`, JSON.stringify(dateRange));
    }
  }, [schedule, dateRange, user]);

  const daysOfWeek = [
    { key: 'monday', label: 'Monday' },
    { key: 'tuesday', label: 'Tuesday' },
    { key: 'wednesday', label: 'Wednesday' },
    { key: 'thursday', label: 'Thursday' },
    { key: 'friday', label: 'Friday' },
    { key: 'saturday', label: 'Saturday' },
    { key: 'sunday', label: 'Sunday' }
  ];

  const handleDayToggle = (day) => {
    setSchedule(prev => ({ ...prev, [day]: { ...prev[day], enabled: !prev[day].enabled } }));
  };

  const handleTimeChange = (day, timeType, value) => {
    setSchedule(prev => ({ ...prev, [day]: { ...prev[day], [timeType]: value } }));
  };

  const handleDateRangeChange = (field, value) => {
    setDateRange(prev => ({ ...prev, [field]: value }));
  };

  const validateForm = () => {
    const hasEnabledDay = Object.values(schedule).some(day => day.enabled);
    if (!hasEnabledDay) {
      setError('Please select at least one day of the week.');
      return false;
    }
    if (!dateRange.startDate || !dateRange.endDate) {
      setError('Please provide both start and end dates.');
      return false;
    }
    if (new Date(dateRange.endDate) <= new Date(dateRange.startDate)) {
      setError('End date must be after start date.');
      return false;
    }
    for (const [day, config] of Object.entries(schedule)) {
      if (config.enabled && config.from >= config.to) {
        setError(`Invalid time range for ${day}. End time must be after start time.`);
        return false;
      }
    }
    return true;
  };

  const formatScheduleData = () => {
    const scheduleObject = {};
    Object.entries(schedule).forEach(([day, config]) => {
      if (config.enabled) {
        scheduleObject[day] = { from: config.from, to: config.to };
      }
    });
    return {
      schedule: scheduleObject,
      start_date: dateRange.startDate,
      end_date: dateRange.endDate
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!validateForm()) return;

    const formattedData = formatScheduleData();
    setScheduleDataToSubmit(formattedData); // Save data in case of conflict

    setIsLoading(true);
    try {
      const result = await PropertyAPI.addLandlordRecurringAvailability(user.id, formattedData);
      if (result.success) {
        onSuccess(result);
        onClose();
      }
    } catch (error) {
      if (error.response && error.response.status === 409) {
        setConflicts(error.response.data.conflicts || []);
        setView('conflict');
        setError('Your new schedule conflicts with existing bookings.');
      } else {
        setError(error.message || 'Failed to set availability. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResolveConflict = async (resolution) => {
    setError('');
    setIsLoading(true);
    try {
        const result = await BookingAPI.resolveAvailabilityConflicts({
            ...scheduleDataToSubmit,
            resolution: resolution,
            conflict_ids: conflicts.map(c => c.id)
        });

        if (result.success) {
            // First, signal the parent component to refresh its data.
            onSuccess(result);
            // Then, close the modal.
            onClose();
        }
    } catch (error) {
        setError(error.message || 'Failed to resolve conflicts. Please try again.');
    } finally {
        setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        <div className="p-6 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">
              {view === 'form' ? 'Set Your Availability' : 'Resolve Scheduling Conflicts'}
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl" disabled={isLoading}>
              ×
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto">
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          {view === 'form' && (
            <form id="availability-form" onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                  <input type="date" value={dateRange.startDate} onChange={(e) => handleDateRangeChange('startDate', e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md" required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                  <input type="date" value={dateRange.endDate} onChange={(e) => handleDateRangeChange('endDate', e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md" required />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Weekly Schedule</label>
                <div className="space-y-3">
                  {daysOfWeek.map(({ key, label }) => (
                    <div key={key} className="flex items-center space-x-4 p-3 border rounded-lg">
                      <label className="flex items-center space-x-2 min-w-[100px]">
                        <input type="checkbox" checked={schedule[key].enabled} onChange={() => handleDayToggle(key)} className="rounded" />
                        <span className="text-sm font-medium text-gray-700">{label}</span>
                      </label>
                      {schedule[key].enabled && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-600">From:</span>
                          <input type="time" value={schedule[key].from} onChange={(e) => handleTimeChange(key, 'from', e.target.value)} className="px-2 py-1 border border-gray-300 rounded text-sm" />
                          <span className="text-sm text-gray-600">To:</span>
                          <input type="time" value={schedule[key].to} onChange={(e) => handleTimeChange(key, 'to', e.target.value)} className="px-2 py-1 border border-gray-300 rounded text-sm" />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </form>
          )}

          {view === 'conflict' && (
            <div className="space-y-4">
              <p className="text-gray-700">Your new schedule conflicts with the following confirmed appointments. Please choose how to resolve them.</p>
              <div className="border rounded-lg max-h-60 overflow-y-auto">
                <ul className="divide-y">
                  {conflicts.map(booking => (
                    <li key={booking.id} className="p-3">
                      <p className="font-semibold">{booking.property?.title || `Booking ID: ${booking.id}`}</p>
                      <p className="text-sm text-gray-600">
                        with {booking.name} on {new Date(booking.appointment_date + 'T00:00:00').toLocaleDateString()} at {booking.appointment_time}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg space-y-4">
                <div>
                  <h4 className="font-semibold">Option 1: Cancel Conflicting Viewings</h4>
                  <p className="text-sm text-gray-600 mb-2">Tenants will be notified that their viewings have been cancelled due to a schedule change.</p>
                  <button onClick={() => handleResolveConflict('cancel')} disabled={isLoading} className="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50">
                    {isLoading ? 'Processing...' : 'Cancel Viewings & Update Schedule'}
                  </button>
                </div>
                <div>
                  <h4 className="font-semibold">Option 2: Request Reschedule</h4>
                  <p className="text-sm text-gray-600 mb-2">Tenants will be notified to choose a new time from your updated availability. Their current slots will be cancelled.</p>
                  <button onClick={() => handleResolveConflict('reschedule')} disabled={isLoading} className="w-full px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 disabled:opacity-50">
                    {isLoading ? 'Processing...' : 'Request Reschedule & Update Schedule'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-6 border-t mt-auto bg-gray-50">
          <div className="flex justify-end space-x-3">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50" disabled={isLoading}>
              Cancel
            </button>
            {view === 'form' && (
              <button type="submit" form="availability-form" disabled={isLoading} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
                {isLoading ? 'Setting...' : 'Set Availability'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AvailabilityModal;
