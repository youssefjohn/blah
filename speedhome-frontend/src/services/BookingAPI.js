class BookingAPI {
  static async createBooking(bookingData) {
    try {
      const response = await fetch('/api/bookings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(bookingData)
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to create booking');
      }

      return data;
    } catch (error) {
      console.error('Error creating booking:', error);
      throw error;
    }
  }

  static async getBookingsByUser(userId) {
    try {
      const response = await fetch(`/api/bookings/user/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch user bookings');
      }

      return data;
    } catch (error) {
      console.error('Error fetching user bookings:', error);
      throw error;
    }
  }

  static async getBookingsByLandlord(landlordId) {
    try {
      const response = await fetch(`/api/bookings/landlord/${landlordId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch landlord bookings');
      }

      return data;
    } catch (error) {
      console.error('Error fetching landlord bookings:', error);
      throw error;
    }
  }

  static async updateBookingStatus(bookingId, status) {
    try {
      const response = await fetch(`/api/bookings/${bookingId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to update booking status');
      }

      return data;
    } catch (error) {
      console.error('Error updating booking status:', error);
      throw error;
    }
  }

  static async getBooking(bookingId) {
    try {
      const response = await fetch(`/api/bookings/${bookingId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch booking');
      }

      return data;
    } catch (error) {
      console.error('Error fetching booking:', error);
      throw error;
    }
  }

  static async rescheduleBooking(bookingId, rescheduleData) {
    try {
      const response = await fetch(`/api/bookings/${bookingId}/reschedule`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(rescheduleData)
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to reschedule booking');
      }

      return data;
    } catch (error) {
      console.error('Error rescheduling booking:', error);
      throw error;
    }
  }

  static async approveReschedule(bookingId) {
    try {
      const response = await fetch(`/api/bookings/${bookingId}/approve-reschedule`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to approve reschedule');
      }

      return data;
    } catch (error) {
      console.error('Error approving reschedule:', error);
      throw error;
    }
  }
  static async cancelReschedule(bookingId) {
    try {
      const response = await fetch(`/api/bookings/${bookingId}/cancel-reschedule`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to cancel reschedule request');
      }

      return data;
    } catch (error) {
      console.error('Error cancelling reschedule request:', error);
      throw error;
    }
  }

  static async cancelBooking(bookingId) {
    try {
      const response = await fetch(`/api/bookings/${bookingId}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to cancel booking');
      }

      return data;
    } catch (error) {
      console.error('Error cancelling booking:', error);
      throw error;
    }
  }

  static async hasScheduled(propertyId) {
    try {
      // ✅ CORRECTED THE URL TO MATCH THE BACKEND ROUTE
      const response = await fetch(`/api/bookings/has-scheduled/${propertyId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to check booking status');
      }
      return data;
    } catch (error) {
      console.error('Error checking booking status:', error);
      // Return a default "not scheduled" state on error to prevent crashes
      return { success: false, has_scheduled: false };
    }
  }

  static async markAsSeen(bookingId) {
    try {
      const response = await fetch(`/api/bookings/${bookingId}/mark-as-seen`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to mark booking as seen');
      }
      return data;
    } catch (error) {
      console.error('Error marking booking as seen:', error);
      return { success: false };
    }
  }

  static async declineReschedule(bookingId) {
    try {
      const response = await fetch(`/api/bookings/${bookingId}/decline-reschedule`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to decline reschedule');
      }
      return data;
    } catch (error) {
      console.error('Error declining reschedule:', error);
      throw error;
    }
  }

}

export default BookingAPI;
