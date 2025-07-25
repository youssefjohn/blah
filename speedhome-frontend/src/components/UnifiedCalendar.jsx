import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import PropertyAPI from '../services/PropertyAPI';
import AvailabilityModal from './AvailabilityModal';

const UnifiedCalendar = () => {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewingSlots, setViewingSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAvailabilityModal, setShowAvailabilityModal] = useState(false);

  // --- STEP 1: The data loading logic is extracted into a reusable function ---
  const loadData = useCallback(async () => {
    if (!user) return;

    try {
      setLoading(true);
      // Load all viewing slots for the landlord
      const slotsResult = await PropertyAPI.getLandlordViewingSlots(user.id);
      if (slotsResult.success) {
        setViewingSlots(slotsResult.slots);
      }
    } catch (error) {
      console.error('Error loading calendar data:', error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  // --- STEP 2: This calls the loadData function on initial component load ---
  useEffect(() => {
    loadData();
  }, [loadData]);


  // Calendar navigation
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Get calendar days for current month
  const getCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - startDate.getDay());

    const days = [];
    const currentDay = new Date(startDate);

    for (let i = 0; i < 42; i++) {
      days.push(new Date(currentDay));
      currentDay.setDate(currentDay.getDate() + 1);
    }

    return days;
  };

  const createLocalDate = (dateStr) => {
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day);
  };

  const getSlotsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return viewingSlots.filter(slot => {
      const slotDateObj = createLocalDate(slot.date);
      return slotDateObj.toISOString().split('T')[0] === dateStr;
    });
  };

  const formatMonthYear = (date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isCurrentMonth = (date) => {
    return date.getMonth() === currentDate.getMonth();
  };

  if (loading && viewingSlots.length === 0) { // Only show initial loading spinner
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500"></div>
      </div>
    );
  }

  const calendarDays = getCalendarDays();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Calendar Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold text-gray-900">My Availability Calendar</h2>
          <button
            onClick={goToToday}
            className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-md hover:bg-yellow-200 transition-colors"
          >
            Today
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowAvailabilityModal(true)}
            className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors text-sm font-medium"
          >
            Manage Availability
          </button>
        </div>
      </div>

      {/* Month Navigation */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={goToPreviousMonth}
          className="p-2 hover:bg-gray-100 rounded-md transition-colors"
        >
          &lt;
        </button>

        <h3 className="text-xl font-semibold text-gray-900">
          {formatMonthYear(currentDate)}
        </h3>

        <button
          onClick={goToNextMonth}
          className="p-2 hover:bg-gray-100 rounded-md transition-colors"
        >
          &gt;
        </button>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1 mb-4">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="p-3 text-center text-sm font-medium text-gray-500 bg-gray-50">
            {day}
          </div>
        ))}

        {calendarDays.map((day, index) => {
          const slots = getSlotsForDate(day);
          const isCurrentMonthDay = isCurrentMonth(day);
          const isTodayDay = isToday(day);

          return (
            <div
              key={index}
              className={`min-h-[120px] p-2 border border-gray-200 ${
                isCurrentMonthDay ? 'bg-white' : 'bg-gray-50'
              } ${isTodayDay ? 'ring-2 ring-yellow-400' : ''}`}
            >
              <div className={`text-sm font-medium mb-1 ${
                isCurrentMonthDay ? 'text-gray-900' : 'text-gray-400'
              } ${isTodayDay ? 'text-yellow-600 font-bold' : ''}`}>
                {day.getDate()}
              </div>

              <div className="space-y-1">
                {slots.slice(0, 3).map((slot, slotIndex) => (
                  <div
                    key={slotIndex}
                    className={`text-xs p-1 rounded text-white truncate ${
                      slot.is_available ? 'bg-green-500' : 'bg-red-500'
                    }`}
                    title={`${slot.property_title || 'No Property Assigned'} - ${slot.start_time}-${slot.end_time}`}
                  >
                    {slot.start_time}-{slot.end_time}
                  </div>
                ))}

                {slots.length > 3 && (
                  <div className="text-xs text-gray-500 font-medium">
                    +{slots.length - 3} more
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center space-x-6 text-sm">
        <div className="flex items-center space-x-2"><div className="w-3 h-3 bg-green-500 rounded"></div><span>Available</span></div>
        <div className="flex items-center space-x-2"><div className="w-3 h-3 bg-red-500 rounded"></div><span>Booked</span></div>
        <div className="flex items-center space-x-2"><div className="w-3 h-3 border-2 border-yellow-400 rounded"></div><span>Today</span></div>
      </div>

      {/* Statistics */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-green-50 p-4 rounded-lg"><div className="text-2xl font-bold text-green-600">{viewingSlots.filter(slot => slot.is_available).length}</div><div className="text-sm text-green-700">Available Slots</div></div>
        <div className="bg-red-50 p-4 rounded-lg"><div className="text-2xl font-bold text-red-600">{viewingSlots.filter(slot => !slot.is_available).length}</div><div className="text-sm text-red-700">Booked Slots</div></div>
        <div className="bg-blue-50 p-4 rounded-lg"><div className="text-2xl font-bold text-blue-600">{viewingSlots.length}</div><div className="text-sm text-blue-700">Total Slots</div></div>
      </div>

      {/* Availability Modal */}
      {showAvailabilityModal && (
        <AvailabilityModal
          onClose={() => setShowAvailabilityModal(false)}
          // --- STEP 3: The onSuccess handler now correctly calls the main loadData function ---
          onSuccess={(result) => {
            const message = result?.message || result?.success_message || 'Availability updated successfully!';
            alert(message);
            setShowAvailabilityModal(false);
            loadData(); // This will re-fetch the slots and update the calendar
          }}
        />
      )}
    </div>
  );
};

export default UnifiedCalendar;
