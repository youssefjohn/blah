import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import MessagingAPI from '../services/MessagingAPI';
import BookingAPI from '../services/BookingAPI';
import ChatWindow from '../components/ChatWindow';
import { formatDate, formatTime } from '../utils/dateUtils';

const ChatPage = () => {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [conversation, setConversation] = useState(null);
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
      return;
    }
    loadBookingAndConversation();
  }, [bookingId, isAuthenticated]);

  const loadBookingAndConversation = async () => {
    try {
      setLoading(true);
      
      // Load booking details first
      const bookingResult = await BookingAPI.getBookingById(bookingId);
      if (!bookingResult.success) {
        setError('Booking not found or access denied');
        return;
      }
      
      const bookingData = bookingResult.booking;
      setBooking(bookingData);
      
      // Check if user has access to this booking
      const hasAccess = bookingData.tenant_id === user.id || bookingData.landlord_id === user.id;
      if (!hasAccess) {
        setError('You do not have access to this conversation');
        return;
      }
      
      // Check if booking status allows messaging
      const allowedStatuses = ['pending', 'confirmed', 'Pending', 'Confirmed'];
      if (!allowedStatuses.includes(bookingData.status)) {
        setError('Messaging is not available for this booking status');
        return;
      }
      
      // Load or create conversation
      const conversationResult = await MessagingAPI.getOrCreateConversation(bookingId);
      if (conversationResult.success) {
        setConversation(conversationResult.conversation);
      } else {
        setError('Failed to load conversation');
      }
      
    } catch (error) {
      console.error('Error loading chat:', error);
      setError('Failed to load chat');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (content) => {
    if (!conversation) return;
    
    try {
      const result = await MessagingAPI.sendMessage(conversation.id, content);
      if (result.success) {
        // Refresh conversation to get updated messages
        const updatedConversation = await MessagingAPI.getConversation(conversation.id);
        if (updatedConversation.success) {
          setConversation(updatedConversation.conversation);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading conversation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => navigate(-1)} 
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const otherParticipant = booking?.tenant_id === user.id 
    ? { name: booking.landlord_name, role: 'Landlord' }
    : { name: booking.tenant_name, role: 'Tenant' };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button 
                onClick={() => navigate(-1)} 
                className="text-gray-400 hover:text-gray-600 mr-4"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Chat with {otherParticipant.name}
                </h1>
                <p className="text-sm text-gray-500">
                  {booking?.propertyTitle} • {formatDate(booking?.appointment_date)} at {formatTime(booking?.appointment_time)}
                </p>
              </div>
            </div>
            <div className="flex items-center">
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                booking?.status === 'confirmed' || booking?.status === 'Confirmed' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {booking?.status}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Window */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-lg h-[600px]">
          {conversation && (
            <ChatWindow 
              conversation={conversation}
              currentUser={user}
              onSendMessage={handleSendMessage}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPage;

