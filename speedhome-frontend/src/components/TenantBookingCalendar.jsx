import React, { useState, useEffect } from 'react';
import PropertyAPI from '../services/PropertyAPI';
import BookingAPI from '../services/BookingAPI';
import { useAuth } from '../contexts/AuthContext';

const TenantBookingCalendar = ({ propertyId, onBookingSuccess, onClose }) => {
  const { user } = useAuth();
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());

  // Load available slots for the property
  useEffect(() => {
    const loadSlots = async () => {
      if (!propertyId) return;
      
      try {
        setLoading(true);
        const slots = await PropertyAPI.getAvailableSlots(propertyId);
        setAvailableSlots(slots);
      } catch (error) {
        console.error('Error loading available slots:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSlots();
  }, [propertyId]);

  // Group slots by date
  const groupSlotsByDate = () => {
    const grouped = {};
    availableSlots.forEach(slot => {
      if (slot.is_available) {
        const date = slot.date;
        if (!grouped[date]) {
          grouped[date] = [];
        }
        grouped[date].push(slot);
      }
    });
    return grouped;
  };

  // Get next 14 days starting from today
  const getNext14Days = () => {
    const days = [];
    const today = new Date();
    
    for (let i = 0; i < 14; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      days.push(date);
    }
    
    return days;
  };

  // Format date for display
  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  // Format date for comparison
  const formatDateKey = (date) => {
    return date.toISOString().split('T')[0];
  };

  // Check if date is today
  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  // Handle slot selection
  const handleSlotSelect = (slot) => {
    setSelectedSlot(slot);
  };

  // Handle booking confirmation
  const handleBooking = async () => {
    if (!selectedSlot || !user) return;
    
    try {
      setBooking(true);
      const result = await BookingAPI.createBooking({
        property_id: propertyId,
        viewing_slot_id: selectedSlot.id,
        tenant_id: user.id,
        booking_date: selectedSlot.date,
        booking_time: selectedSlot.start_time,
        status: 'pending'
      });
      
      if (result.success) {
        alert('Viewing appointment booked successfully!');
        if (onBookingSuccess) onBookingSuccess();
        if (onClose) onClose();
      } else {
        alert(`Failed to book appointment: ${result.error}`);
      }
    } catch (error) {
      console.error('Error booking appointment:', error);
      alert('An error occurred while booking the appointment.');
    } finally {
      setBooking(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500"></div>
      </div>
    );
  }

  const groupedSlots = groupSlotsByDate();
  const next14Days = getNext14Days();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">Select Viewing Time</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {availableSlots.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-500 mb-4">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <p className="text-gray-600 text-lg">No viewing slots available</p>
          <p className="text-gray-500 text-sm mt-2">Please contact the landlord to schedule a viewing</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Available Dates */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {next14Days.map((date, index) => {
              const dateKey = formatDateKey(date);
              const slotsForDate = groupedSlots[dateKey] || [];
              
              if (slotsForDate.length === 0) return null;
              
              return (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className={`text-sm font-medium mb-3 ${
                    isToday(date) ? 'text-yellow-600' : 'text-gray-700'
                  }`}>
                    {formatDate(date)}
                    {isToday(date) && <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Today</span>}
                  </div>
                  
                  <div className="space-y-2">
                    {slotsForDate.map((slot) => (
                      <button
                        key={slot.id}
                        onClick={() => handleSlotSelect(slot)}
                        className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                          selectedSlot?.id === slot.id
                            ? 'bg-yellow-500 text-white'
                            : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                        }`}
                      >
                        {slot.start_time} - {slot.end_time}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Selected Slot Info */}
          {selectedSlot && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-medium text-yellow-800 mb-2">Selected Viewing Time</h4>
              <p className="text-yellow-700">
                <span className="font-medium">Date:</span> {new Date(selectedSlot.date).toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
              <p className="text-yellow-700">
                <span className="font-medium">Time:</span> {selectedSlot.start_time} - {selectedSlot.end_time}
              </p>
            </div>
          )}

          {/* Booking Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              {selectedSlot ? 'Ready to book your viewing appointment?' : 'Please select a time slot above'}
            </div>
            
            <div className="flex space-x-3">
              {onClose && (
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              )}
              
              <button
                onClick={handleBooking}
                disabled={!selectedSlot || booking}
                className={`px-6 py-2 rounded-md font-medium transition-colors ${
                  selectedSlot && !booking
                    ? 'bg-yellow-500 text-white hover:bg-yellow-600'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {booking ? 'Booking...' : 'Book Viewing'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TenantBookingCalendar;

