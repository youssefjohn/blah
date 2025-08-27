import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import BookingAPI from '../services/BookingAPI';
import PropertyAPI from '../services/PropertyAPI';
import ApplicationAPI from '../services/ApplicationAPI';
import TenancyAgreementAPI from '../services/TenancyAgreementAPI';
import DepositAPI from '../services/DepositAPI';
import { formatDate, formatTime } from '../utils/dateUtils';
import TenantBookingCalendar from '../components/TenantBookingCalendar';
import MessagingCenter from '../components/MessagingCenter';
import MessagingAPI from '../services/MessagingAPI';

const UserDashboard = ({ favorites, toggleFavorite }) => {
  const navigate = useNavigate();
  const { user, isAuthenticated, isTenant, updateProfile, refreshUser } = useAuth();
  const [conversations, setConversations] = useState([]);
  
  // Tab state management
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  
  const [bookings, setBookings] = useState([]);
  const [applications, setApplications] = useState([]);
  const [agreements, setAgreements] = useState([]);
  const [favoritedProperties, setFavoritedProperties] = useState([]);
  const [deposits, setDeposits] = useState([]);

  // State for profile editing
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    bio: '',
    occupation: '',
    company_name: '',
    profile_picture: null
  });
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef(null);

  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [rescheduleData, setRescheduleData] = useState({
    bookingId: null,
    newDate: '',
    newTime: ''
  });

  // State for slot selection modal
  const [showSlotSelectionModal, setShowSlotSelectionModal] = useState(false);
  const [selectedBookingForReschedule, setSelectedBookingForReschedule] = useState(null);

  // Populate profile form when user data is available
  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        bio: user.bio || '',
        occupation: user.occupation || '',
        company_name: user.company_name || '',
        profile_picture: user.profile_picture || null
      });
    }
  }, [user]);

  // Handler for text input changes
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
  };

  // Handler for image file selection
  const handlePictureChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file.');
        return;
      }
      if (file.size > 2 * 1024 * 1024) { // 2MB limit
        alert('File is too large. Please select an image under 2MB.');
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileData(prev => ({ ...prev, profile_picture: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  // Handler for saving the profile
  const handleProfileSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const result = await updateProfile(profileData);
      if (result.success) {
        alert('Profile updated successfully!');
        setIsEditing(false);
        await refreshUser();
      } else {
        alert(`Failed to update profile: ${result.error}`);
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('An unexpected error occurred.');
    } finally {
      setIsSaving(false);
    }
  };

  // Handler for canceling edits
  const handleCancelEdit = () => {
    setIsEditing(false);
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        bio: user.bio || '',
        occupation: user.occupation || '',
        company_name: user.company_name || '',
        profile_picture: user.profile_picture || null
      });
    }
  };

  const withdrawApplication = async (applicationId) => {
    if (window.confirm('Are you sure you want to withdraw this application? This action cannot be undone.')) {
      try {
        const result = await ApplicationAPI.withdrawApplication(applicationId);
        if (result.success) {
          alert('Application withdrawn successfully.');
          await loadApplications();
        } else {
          alert(`Failed to withdraw application: ${result.error}`);
        }
      } catch (error) {
        console.error('Error withdrawing application:', error);
        alert('An unexpected error occurred while withdrawing the application.');
      }
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
      return;
    }
    if (!isTenant()) {
      alert('Access denied. This dashboard is for tenants only.');
      navigate('/');
      return;
    }
  }, [isAuthenticated, isTenant, navigate]);

  const loadBookings = async () => {
    if (!isAuthenticated || !user) return;
    try {
      const result = await BookingAPI.getBookingsByUser(user.id);
      if (result.success) setBookings(result.bookings);
    } catch (error) {
      console.error('Error loading bookings:', error);
    }
  };

  const loadApplications = async () => {
    if (!isAuthenticated || !user) return;
    try {
      const result = await ApplicationAPI.getApplicationsByTenant();
      if (result.success) setApplications(result.applications);
    } catch (error) {
      console.error('Error loading applications:', error);
    }
  };

  const loadAgreements = async () => {
    if (!isAuthenticated || !user) return;
    try {
      const result = await TenancyAgreementAPI.getTenantAgreements();
      if (result.success) setAgreements(result.agreements);
    } catch (error) {
      console.error('Error loading agreements:', error);
    }
  };

  const loadDeposits = async () => {
    if (!isAuthenticated || !user) return;
    try {
      const result = await DepositAPI.getTenantDepositDashboard();
      if (result.success) {
        setDeposits(result.dashboard.active_agreements || []);
      }
    } catch (error) {
      console.error('Error loading deposits:', error);
    }
  };

  const loadDepositDetails = async (agreementId) => {
    try {
      // First get the agreement to check if tenancy is ending soon
      const agreement = agreements.find(a => a.id === agreementId);
      
      // If tenancy is ending soon and deposit is held in escrow, navigate to deposit management
      if (agreement?.deposit_transaction && 
          agreement.deposit_transaction.status === 'held_in_escrow' && 
          agreement.deposit_transaction.tenancy_ending_soon) {
        navigate(`/deposit/${agreement.deposit_transaction.id}/manage`);
        return;
      }
      
      // Otherwise, show the simple alert popup
      const result = await DepositAPI.getDepositForAgreement(agreementId);
      if (result.success && result.has_deposit) {
        alert(`Deposit Details:\n\nTotal Amount: ${DepositAPI.formatMYR(result.deposit.amount)}\nStatus: ${DepositAPI.getDepositStatusText(result.deposit.status)}\nCreated: ${new Date(result.deposit.created_at).toLocaleDateString()}`);
      } else {
        alert('Deposit information is being processed. Please check back in a few minutes.');
      }
    } catch (error) {
      console.error('Error loading deposit details:', error);
      alert('Unable to load deposit details at this time.');
    }
  };

  const handleDepositPayment = async (agreementId) => {
    try {
      // Navigate to deposit payment page
      navigate(`/deposit-payment/${agreementId}`);
    } catch (error) {
      console.error('Error initiating deposit payment:', error);
      alert('Unable to initiate deposit payment at this time.');
    }
  };

  const loadFavoritedProperties = async () => {
    if (!favorites || favorites.length === 0) {
      setFavoritedProperties([]);
      return;
    }
    try {
      const result = await PropertyAPI.getPropertiesForFavorites();
      if (result.success) {
        const userFavorites = result.properties.filter(p => favorites.includes(p.id));
        setFavoritedProperties(userFavorites);
      }
    } catch (error) {
      console.error('Error loading favorited properties:', error);
    }
  };

  useEffect(() => {
    if (isAuthenticated && user) {
        loadBookings();
        loadApplications();
        loadAgreements();
        loadDeposits();
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    loadFavoritedProperties();
  }, [favorites]);

  const cancelBooking = async (bookingId) => {
    if (window.confirm('Are you sure you want to cancel this viewing appointment?')) {
      try {
        const result = await BookingAPI.cancelBooking(bookingId);
        if (result.success) {
          await loadBookings();
          alert('Viewing appointment cancelled successfully.');
        } else {
          alert(`Failed to cancel appointment: ${result.error}`);
        }
      } catch (error) {
        console.error('Error cancelling booking:', error);
      }
    }
  };
  
  const handleBookingRowClick = (booking) => {
    const propertyId = booking.property_id || booking.propertyId;
    if (propertyId) navigate(`/property/${propertyId}`);
  };

  const handleTenantSign = async (agreementId) => {
    if (!window.confirm('Are you sure you want to sign this tenancy agreement? This action cannot be undone.')) {
      return;
    }

    try {
      const result = await TenancyAgreementAPI.signAgreement(agreementId);
      if (result.success) {
        alert('Agreement signed successfully! The landlord will be notified.');
        await loadAgreements(); // Refresh the agreements list
      } else {
        alert(`Failed to sign agreement: ${result.error}`);
      }
    } catch (error) {
      console.error('Error signing agreement:', error);
      alert('An error occurred while signing the agreement. Please try again.');
    }
  };

  const cancelRescheduleRequest = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this reschedule request?')) return;
    try {
      const result = await BookingAPI.cancelReschedule(bookingId);
      if (result.success) {
        await loadBookings();
        alert('Reschedule request has been cancelled.');
      } else {
        alert(`Failed to cancel reschedule request: ${result.error}`);
      }
    } catch (error) {
      console.error('Error cancelling reschedule request:', error);
    }
  };

  useEffect(() => {
  const loadConversations = async () => {
    try {
      const response = await MessagingAPI.getConversations();
      if (response.success) {
        setConversations(response.conversations);
      }
    } catch (error) {
      console.error("Failed to load conversations:", error);
    }
  };
  loadConversations();
}, []);

// Checks if any conversation has an unread_count greater than 0
const hasNewMessages = conversations.some(convo => convo.unread_count > 0);

  const getStatusInfo = (booking) => {
    const isRescheduleByLandlord = (booking.status === 'pending' || booking.status === 'Reschedule Requested') && (booking.reschedule_requested_by === 'landlord' || booking.rescheduleRequestedBy === 'landlord');
    const isRescheduleByTenant = (booking.status === 'pending' || booking.status === 'Reschedule Requested') && (booking.reschedule_requested_by === 'tenant' || booking.rescheduleRequestedBy === 'tenant');
    if (isRescheduleByLandlord) return { text: 'Reschedule Proposed', color: 'bg-orange-100 text-orange-800', description: 'Landlord has proposed a new date/time' };
    if (isRescheduleByTenant) return { text: 'Reschedule Requested', color: 'bg-blue-100 text-blue-800', description: 'Waiting for landlord response' };
    const statusMap = {
      pending: { text: 'Pending', color: 'bg-yellow-100 text-yellow-800', description: 'Awaiting confirmation' },
      confirmed: { text: 'Confirmed', color: 'bg-green-100 text-green-800', description: 'Appointment confirmed' },
      cancelled: { text: 'Cancelled', color: 'bg-red-100 text-red-800', description: 'Appointment cancelled' },
      completed: { text: 'Completed', color: 'bg-gray-100 text-gray-800', description: 'Viewing completed' }
    };
    return statusMap[booking.status] || { text: booking.status, color: 'bg-gray-100 text-gray-800', description: '' };
  };

  const handleConversationRead = async () => {
  try {
    const response = await MessagingAPI.getConversations();
    if (response.success) {
      setConversations(response.conversations);
    }
  } catch (error) {
    console.error("Failed to re-load conversations:", error);
  }
};

  const getApplicationStatusInfo = (status) => {
    const statusMap = {
      pending: { text: 'Pending', color: 'bg-yellow-100 text-yellow-800' },
      approved: { text: 'Approved', color: 'bg-green-100 text-green-800' },
      rejected: { text: 'Rejected', color: 'bg-red-100 text-red-800' },
    };
    return statusMap[status] || { text: status, color: 'bg-gray-100 text-gray-800' };
  };

  const openRescheduleModal = (bookingId) => {
    setRescheduleData({ bookingId, newDate: '', newTime: '' });
    setShowRescheduleModal(true);
  };

  // Function to open slot selection modal for landlord reschedule requests
  const openSlotSelectionModal = (booking) => {
    setSelectedBookingForReschedule(booking);
    setShowSlotSelectionModal(true);
  };

  // Function to handle slot selection for reschedule
  const handleSlotSelection = async (slotId) => {
    try {
      const result = await BookingAPI.selectRescheduleSlot(selectedBookingForReschedule.id, slotId);
      if (result.success) {
        alert('New viewing time selected successfully!');
        setShowSlotSelectionModal(false);
        setSelectedBookingForReschedule(null);
        loadBookings(); // Refresh bookings
      } else {
        alert(`Failed to select slot: ${result.error}`);
      }
    } catch (error) {
      console.error('Error selecting slot:', error);
      alert('An error occurred while selecting the slot.');
    }
  };

  const handleRescheduleSubmit = async (e) => {
    e.preventDefault();
    const { bookingId, newDate, newTime } = rescheduleData;
    if (!newDate || !newTime) {
      alert('Please select a new date and time.');
      return;
    }
    try {
      const result = await BookingAPI.rescheduleBooking(bookingId, { date: newDate, time: newTime, requested_by: 'tenant' });
      if (result.success) {
        await loadBookings();
        setShowRescheduleModal(false);
        alert('Reschedule request sent successfully!');
      } else {
        alert(`Failed to send reschedule request: ${result.error}`);
      }
    } catch (error) {
      console.error('Error sending reschedule request:', error);
    }
  };

  const requestReschedule = async (bookingId) => {
    const newDate = prompt('Enter new preferred date (YYYY-MM-DD):');
    if (!newDate) return;
    const newTime = prompt('Enter new preferred time (HH:MM):');
    if (!newTime) return;
    try {
      const result = await BookingAPI.rescheduleBooking(bookingId, { date: newDate, time: newTime, requested_by: 'tenant' });
      if (result.success) {
        await loadBookings();
        alert('Reschedule request sent successfully!');
      } else {
        alert(`Failed to send reschedule request: ${result.error}`);
      }
    } catch (error) {
      console.error('Error sending reschedule request:', error);
    }
  };

  const respondToReschedule = async (bookingId, response) => {
    try {
      if (response === 'approved') {
        const result = await BookingAPI.approveReschedule(bookingId);
        if (result.success) {
          await loadBookings();
          alert('Reschedule request has been accepted!');
        } else {
          alert(`Failed to approve reschedule: ${result.error}`);
        }
      } else { // This handles the 'declined' case
        // CORRECTED: Call the declineReschedule endpoint instead of cancelling
        const result = await BookingAPI.declineReschedule(bookingId);
        if (result.success) {
            await loadBookings();
            alert('Reschedule request has been declined.');
        } else {
            alert(`Failed to decline reschedule: ${result.error}`);
        }
      }
    } catch (error) {
      console.error('Error responding to reschedule request:', error);
      alert('An error occurred while responding to the reschedule request.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">My Dashboard</h1>
        
        {/* Tab Navigation */}
        <div className="bg-white shadow-sm rounded-lg mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'dashboard'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📊 Dashboard
              </button>
              <button
                  onClick={() => setActiveTab('messages')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === 'messages'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span>💬 Messages</span>
                  {hasNewMessages && (
                    <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-semibold bg-red-500 text-white">New</span>
                  )}
               </button>
               <button
                  onClick={() => setActiveTab('agreements')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'agreements'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  📄 Agreements
               </button>
            </nav>
          </div>
        </div>

        {/* Dashboard Tab Content */}
        {activeTab === 'dashboard' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-8">
            <div className="bg-white shadow-lg rounded-xl p-6">
              {/* ✅ FIX: Changed to a vertical, centered layout */}
              <div className="flex flex-col items-center text-center mb-6">
                <div className="relative mb-4">
                  <img 
                    src={user?.profile_picture || `https://ui-avatars.com/api/?name=${user?.full_name || user?.username}&background=fbbF24&color=fff`} 
                    alt="Profile" 
                    className="rounded-full w-24 h-24 object-cover border-4 border-white shadow-lg"
                  />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-800">{user?.full_name || user?.username || 'User'}</h2>
                  {/* ✅ FIX: Added break-all to prevent long emails from overflowing */}
                  <p className="text-gray-600 break-all">{user?.email || 'No email provided'}</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center"><span className="text-gray-600">Account Type:</span><span className="font-medium bg-gray-100 px-2 py-1 rounded">Tenant</span></div>
                <div className="flex justify-between items-center"><span className="text-gray-600">Member Since:</span><span className="font-medium">{formatDate(user?.created_at)}</span></div>
              </div>
            </div>

            <div className="bg-white shadow-lg rounded-xl p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-900">My Profile</h2>
                {!isEditing && <button onClick={() => setIsEditing(true)} className="text-blue-600 hover:text-blue-800 text-sm font-semibold">Edit</button>}
              </div>

              {isEditing ? (
                <form onSubmit={handleProfileSave} className="space-y-4">
                  <div className="flex flex-col items-center space-y-2">
                    <img 
                      src={profileData.profile_picture || `https://ui-avatars.com/api/?name=${user?.full_name || user?.username}&background=fbbF24&color=fff`} 
                      alt="Profile Preview" 
                      className="rounded-full w-24 h-24 object-cover border-4 border-gray-200"
                    />
                    <input type="file" ref={fileInputRef} onChange={handlePictureChange} accept="image/*" className="hidden" />
                    <button type="button" onClick={() => fileInputRef.current.click()} className="bg-gray-100 text-gray-700 py-2 px-4 rounded-lg text-sm font-semibold hover:bg-gray-200">Change Picture</button>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">First Name</label>
                    <input type="text" name="first_name" value={profileData.first_name} onChange={handleProfileChange} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"/>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Last Name</label>
                    <input type="text" name="last_name" value={profileData.last_name} onChange={handleProfileChange} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"/>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Phone Number</label>
                    <input type="tel" name="phone" value={profileData.phone} onChange={handleProfileChange} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"/>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Occupation</label>
                    <input type="text" name="occupation" value={profileData.occupation} onChange={handleProfileChange} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500" placeholder="e.g., Software Engineer"/>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Company Name</label>
                    <input type="text" name="company_name" value={profileData.company_name} onChange={handleProfileChange} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500" placeholder="e.g., Speedhome Inc."/>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">About Me / Bio</label>
                    <textarea name="bio" value={profileData.bio} onChange={handleProfileChange} rows="4" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500" placeholder="Introduce yourself to landlords..."></textarea>
                  </div>
                  <div className="flex gap-4 pt-2">
                    <button type="button" onClick={handleCancelEdit} className="w-full bg-gray-200 text-gray-800 py-2 px-4 rounded-lg hover:bg-gray-300 transition duration-200">Cancel</button>
                    <button type="submit" disabled={isSaving} className="w-full bg-yellow-500 text-white py-2 px-4 rounded-lg hover:bg-yellow-600 transition duration-200 disabled:bg-yellow-300">
                      {isSaving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-4 text-sm">
                  <div className="flex justify-between items-center"><span className="text-gray-600">Full Name:</span><span className="font-medium text-gray-800">{user?.full_name || 'Not set'}</span></div>
                  <div className="flex justify-between items-center"><span className="text-gray-600">Phone:</span><span className="font-medium text-gray-800">{user?.phone || 'Not set'}</span></div>
                  <div className="flex justify-between items-center"><span className="text-gray-600">Occupation:</span><span className="font-medium text-gray-800">{user?.occupation || 'Not set'}</span></div>
                  <div className="flex justify-between items-center"><span className="text-gray-600">Company:</span><span className="font-medium text-gray-800">{user?.company_name || 'Not set'}</span></div>
                  <div className="pt-2">
                    <span className="text-gray-600">About Me:</span>
                    <p className="font-medium text-gray-800 whitespace-pre-wrap mt-1">{user?.bio || 'Not set'}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-2 space-y-8">
            <div className="bg-white shadow-lg rounded-xl p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">My Rental Applications</h2>
              {applications.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-gray-400 text-6xl mb-4">📄</div>
                  <p className="text-gray-600 text-lg mb-4">No applications submitted yet</p>
                  <p className="text-gray-500">When you apply for a property, your application will appear here.</p>
                  <Link to="/" className="inline-block mt-4 bg-yellow-500 text-white px-6 py-2 rounded-lg hover:bg-yellow-600 transition duration-200 font-semibold">
                    Find a Property
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {applications.map((app) => {
                    const statusInfo = getApplicationStatusInfo(app.status);
                    return (
                      <div key={app.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow bg-white">
                        <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">{app.property?.title || 'Application'}</h3>
                            <div className="flex items-center flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500 mb-3">
                              <span>Applied: {formatDate(app.created_at)}</span>
                              <span className="hidden sm:inline">•</span>
                              <span>Application ID: #{app.id}</span>
                            </div>
                            {app.message && (
                               <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-md border border-gray-200">
                                  <strong className="text-gray-800">Your message:</strong> "{app.message}"
                               </p>
                            )}
                          </div>
                          <div className="flex flex-col items-start sm:items-end space-y-2 w-full sm:w-auto">
                            <span className={`px-3 py-1 text-xs font-bold rounded-full ${statusInfo.color}`}>{statusInfo.text}</span>
                          </div>
                        </div>
                         <div className="mt-4 pt-4 border-t border-gray-100 flex items-center gap-4">
                            <Link to={`/property/${app.property_id}`} className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                                View Property
                            </Link>
                            {app.status === 'pending' && (
                                <>
                                    <span className="text-gray-300">|</span>
                                    <button
                                        onClick={() => withdrawApplication(app.id)}
                                        className="text-red-600 hover:text-red-800 text-sm font-medium"
                                    >
                                        Withdraw Application
                                    </button>
                                </>
                            )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="bg-white shadow-lg rounded-xl p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">My Viewing Appointments</h2>
              {bookings.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-gray-400 text-6xl mb-4">📅</div>
                  <p className="text-gray-600 text-lg mb-4">No viewing appointments yet</p>
                  <p className="text-gray-500">Browse properties and schedule viewings to see them here.</p>
                  <Link to="/" className="inline-block mt-4 bg-yellow-500 text-white px-6 py-2 rounded-lg hover:bg-yellow-600 transition duration-200 font-semibold">
                    Browse Properties
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {bookings.map((booking) => {
                    const statusInfo = getStatusInfo(booking);
                    const isRescheduleByLandlord = (booking.status === 'pending' || booking.status === 'Reschedule Requested') && (booking.reschedule_requested_by === 'landlord' || booking.rescheduleRequestedBy === 'landlord');
                    const isRescheduleByTenant = (booking.status === 'pending' || booking.status === 'Reschedule Requested') && (booking.reschedule_requested_by === 'tenant' || booking.rescheduleRequestedBy === 'tenant');
                    const canRequestReschedule = booking.status === 'confirmed' || booking.status === 'pending';
                    const originalDate = booking.appointment_date;
                    const originalTime = booking.appointment_time;
                    const proposedDate = booking.proposed_date;
                    const proposedTime = booking.proposed_time;
                    const isRescheduleActive = proposedDate && proposedTime;

                    return (
                      <div key={booking.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer bg-white" onClick={() => handleBookingRowClick(booking)}>
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">{booking.propertyTitle || 'Property Viewing'}</h3>
                            <div className="mb-3">
                              {isRescheduleActive ? (
                                <div className="space-y-1">
                                  <div className="flex items-center text-gray-400 line-through"><svg className="w-4 h-4 mr-1.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg><span>Original: {formatDate(originalDate)} at {formatTime(originalTime)}</span></div>
                                  <div className="flex items-center font-semibold text-orange-600"><svg className="w-4 h-4 mr-1.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg><span>New: {formatDate(proposedDate)} at {formatTime(proposedTime)}</span></div>
                                </div>
                              ) : (
                                <div className="flex items-center flex-wrap gap-x-4 gap-y-1 text-gray-500 text-sm"><div className="flex items-center"><svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>{formatDate(originalDate)}</div><div className="flex items-center"><svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>{formatTime(originalTime)}</div></div>
                              )}
                            </div>
                            <div className="flex items-center gap-x-4 text-xs text-gray-500"><span>Booking ID: #{booking.id}</span></div>
                          </div>
                          <div className="flex flex-col items-start sm:items-end space-y-2 w-full sm:w-auto">
                            <span className={`px-3 py-1 text-xs font-bold rounded-full ${statusInfo.color}`}>{statusInfo.text}</span>
                            {statusInfo.description && <p className="text-xs text-gray-500 text-left sm:text-right max-w-xs">{statusInfo.description}</p>}
                          </div>
                        </div>
                        <div className="mt-4 pt-4 border-t border-gray-100 flex flex-wrap gap-x-4 gap-y-2">
                          {booking.status !== 'cancelled' && booking.status !== 'completed' && (<button onClick={(e) => { e.stopPropagation(); cancelBooking(booking.id); }} className="text-red-600 hover:text-red-800 text-sm font-medium">Cancel Appointment</button>)}
                          {canRequestReschedule && !isRescheduleByTenant && !isRescheduleByLandlord && (<button onClick={(e) => { e.stopPropagation(); openRescheduleModal(booking.id); }} className="text-blue-600 hover:text-blue-800 text-sm font-medium">Request Reschedule</button>)}
                          {/* Message Landlord button for pending and confirmed bookings */}
                          {(booking.status === 'pending' || booking.status === 'confirmed' || 
                            booking.status === 'Pending' || booking.status === 'Confirmed') && (
                            <button 
                              onClick={async (e) => { 
                                e.stopPropagation(); 
                                try {
                                  // Get or create conversation for this booking
                                  const response = await MessagingAPI.getOrCreateConversation(booking.id);
                                  if (response.success) {
                                    // Switch to Messages tab and select the conversation
                                    setActiveTab('messages');
                                    setSelectedConversationId(response.conversation.id);
                                  }
                                } catch (error) {
                                  console.error('Error opening conversation:', error);
                                  alert('Failed to open conversation');
                                }
                              }} 
                              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                            >
                              💬 Message Landlord
                            </button>
                          )}
                          {isRescheduleByLandlord && (
                            <div onClick={(e) => e.stopPropagation()} className="flex items-center gap-2">
                              <button 
                                onClick={() => openSlotSelectionModal(booking)} 
                                className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 font-semibold"
                              >
                                View Available Slots
                              </button>
                            </div>
                          )}
                          {isRescheduleByTenant && (<div onClick={(e) => e.stopPropagation()}><button onClick={() => cancelRescheduleRequest(booking.id)} className="px-3 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700 font-semibold">Cancel Request</button></div>)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="bg-white shadow-lg rounded-xl p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Favorite Properties</h2>
              {favoritedProperties.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-gray-400 text-6xl mb-4">❤️</div>
                  <p className="text-gray-600 text-lg mb-4">No favorite properties yet</p>
                  <p className="text-gray-500">Heart properties you like to save them here for easy access.</p>
                   <Link to="/" className="inline-block mt-4 bg-yellow-500 text-white px-6 py-2 rounded-lg hover:bg-yellow-600 transition duration-200 font-semibold">
                    Browse Properties
                  </Link>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {favoritedProperties.map((property) => (
                    <div key={property.id} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-xl transition-shadow bg-white">
                      <div className="relative">
                        <img src={property.image || 'https://placehold.co/600x400/e2e8f0/4a5568?text=No+Image'} alt={property.title} className="w-full h-48 object-cover" />
                        <button onClick={() => toggleFavorite(property.id)} className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:bg-gray-100 transition-colors">
                          <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" /></svg>
                        </button>
                        {property.status === 'Rented' && <div className="absolute top-2 left-2 bg-orange-500 text-white px-2 py-1 rounded text-xs font-bold">Rented</div>}
                      </div>
                      <div className="p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{property.title}</h3>
                        <p className="text-gray-600 text-sm mb-2">{property.location}</p>
                        <div className="flex justify-between items-center">
                          <span className="text-xl font-bold text-yellow-600">RM {property.price}/month</span>
                          <Link to={`/property/${property.id}`} className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                            View Details
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        )}

        {/* Messages Tab Content */}
        {activeTab === 'messages' && (
          <div className="bg-white shadow-lg rounded-lg h-[600px] flex">
            <MessagingCenter 
              user={user}
              onConversationRead={handleConversationRead}
              selectedConversationId={selectedConversationId}
              onConversationSelect={setSelectedConversationId}
            />
          </div>
        )}

        {/* Agreements Tab Content */}
        {activeTab === 'agreements' && (
          <div className="space-y-6">
            <div className="bg-white shadow-lg rounded-xl p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">My Tenancy Agreements</h2>
                <button 
                  onClick={loadAgreements}
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Refresh
                </button>
              </div>

              {agreements.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📄</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No Tenancy Agreements</h3>
                  <p className="text-gray-600 mb-6">You don't have any tenancy agreements yet. Once a landlord approves your application, an agreement will appear here.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {agreements.map((agreement) => (
                    <div key={agreement.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-1">
                            {agreement.property_address}
                          </h3>
                          <p className="text-gray-600">Monthly Rent: <span className="font-semibold text-green-600">RM {agreement.monthly_rent}</span></p>
                          <p className="text-gray-600">Lease Start: <span className="font-semibold">{formatDate(agreement.lease_start_date)}</span></p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          agreement.status === 'pending_signatures' ? 'bg-yellow-100 text-yellow-800' :
                          agreement.status === 'pending_payment' ? 'bg-blue-100 text-blue-800' :
                          agreement.status === 'active' ? 'bg-green-100 text-green-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {agreement.status === 'pending_signatures' ? 'Pending Signatures' :
                           agreement.status === 'pending_payment' ? 'Pending Payment' :
                           agreement.status === 'active' ? 'Active' :
                           agreement.status}
                        </span>
                      </div>

                      <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
                        <div className="text-center">
                          <div className="font-medium text-gray-700">Landlord Signed</div>
                          <div className={`mt-1 ${agreement.landlord_signed_at ? 'text-green-600' : 'text-yellow-600'}`}>
                            {agreement.landlord_signed_at ? '✓ Signed' : '⏳ Pending'}
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-700">Tenant Signed</div>
                          <div className={`mt-1 ${agreement.tenant_signed_at ? 'text-green-600' : 'text-yellow-600'}`}>
                            {agreement.tenant_signed_at ? '✓ Signed' : '⏳ Pending'}
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-700">Payment</div>
                          <div className={`mt-1 ${agreement.payment_completed_at ? 'text-green-600' : 'text-yellow-600'}`}>
                            {agreement.payment_completed_at ? '✓ Paid' : '⏳ Pending'}
                          </div>
                        </div>
                      </div>

                      {/* 🏠 DEPOSIT INFORMATION SECTION */}
                      {agreement.status === 'active' && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-blue-900">🏠 Security Deposit</h4>
                            <span className="text-sm text-blue-600">Malaysian Standard (2 months)</span>
                          </div>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <div className="text-gray-600">Security Deposit</div>
                              <div className="font-semibold text-blue-800">
                                {DepositAPI.formatMYR((agreement.monthly_rent || 0) * 2)}
                              </div>
                            </div>
                            <div>
                              <div className="text-gray-600">Utility Deposit</div>
                              <div className="font-semibold text-blue-800">
                                {DepositAPI.formatMYR((agreement.monthly_rent || 0) * 0.5)}
                              </div>
                            </div>
                          </div>
                          <div className="mt-3 pt-3 border-t border-blue-200">
                            <div className="flex justify-between items-center">
                              <span className="font-semibold text-blue-900">Total Deposit:</span>
                              <span className="font-bold text-lg text-blue-900">
                                {DepositAPI.formatMYR((agreement.monthly_rent || 0) * 2.5)}
                              </span>
                            </div>
                            <div className="mt-2">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                ✓ Held in Escrow
                              </span>
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="flex gap-3">
                        <Link 
                          to={`/agreement/${agreement.id}`}
                          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                        >
                          View Agreement
                        </Link>
                        
                        {agreement.status === 'pending_signatures' && !agreement.tenant_signed_at && (
                          <button 
                            onClick={() => handleTenantSign(agreement.id)}
                            className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors"
                          >
                            Sign Agreement
                          </button>
                        )}
                        
                        {agreement.status === 'pending_payment' && agreement.tenant_signed_at && agreement.landlord_signed_at && (
                          <Link 
                            to={`/payment/${agreement.id}`}
                            className="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors"
                          >
                            Pay Website Fee
                          </Link>
                        )}
                        
                        {agreement.status === 'website_fee_paid' && (
                          <div className="flex flex-col gap-2">
                            {/* Step 2: Pay Deposit - This activates the agreement */}
                            <button 
                              onClick={() => handleDepositPayment(agreement.id)}
                              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                            >
                              💰 Pay Security Deposit ({DepositAPI.formatMYR((agreement.monthly_rent || 0) * 2.5)})
                            </button>
                            <p className="text-sm text-gray-600">
                              ⚠️ Security deposit payment will activate your tenancy agreement
                            </p>
                          </div>
                        )}
                        
                        {/* Deposit Management Button - Show when deposit is ready to manage */}
                        {agreement.deposit_transaction && 
                         agreement.deposit_transaction.status === 'held_in_escrow' && 
                         agreement.deposit_transaction.tenancy_ending_soon && (
                          <Link
                            to={`/deposit/${agreement.deposit_transaction.id}/manage`}
                            className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition-colors"
                          >
                            {agreement.deposit_transaction.claims?.some(claim => claim.tenant_response_status === 'pending') 
                              ? 'Respond to Deposit Claim' 
                              : 'View Deposit Status'}
                          </Link>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {showRescheduleModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full shadow-2xl">
            <div id="rescheduleModal" className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Request Reschedule</h2>
                <button id="closeModal" onClick={() => setShowRescheduleModal(false)} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
              </div>
              <form onSubmit={handleRescheduleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="newDate" className="block text-sm font-medium text-gray-700 mb-1">New Preferred Date</label>
                  <input
                    type="date"
                    id="newDate"
                    value={rescheduleData.newDate}
                    onChange={(e) => setRescheduleData(prev => ({ ...prev, newDate: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="newTime" className="block text-sm font-medium text-gray-700 mb-1">New Preferred Time</label>
                  <input
                    type="time"
                    id="newTime"
                    value={rescheduleData.newTime}
                    onChange={(e) => setRescheduleData(prev => ({ ...prev, newTime: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    required
                  />
                </div>
                <div className="flex gap-3 pt-4">
                  <button id="cancelButton" type="button" onClick={() => setShowRescheduleModal(false)} className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">Cancel</button>
                  <button id="submitButton" type="submit" className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">Submit Request</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Slot Selection Modal for Landlord Reschedule Requests */}
      {showSlotSelectionModal && selectedBookingForReschedule && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Select New Viewing Time</h2>
                  <p className="text-gray-600 mt-1">
                    Choose a new time slot for your viewing of {selectedBookingForReschedule.propertyTitle}
                  </p>
                </div>
                <button 
                  onClick={() => {
                    setShowSlotSelectionModal(false);
                    setSelectedBookingForReschedule(null);
                  }} 
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
              
              <TenantBookingCalendar
                propertyId={selectedBookingForReschedule.property_id}
                onSlotSelect={handleSlotSelection}
                isReschedule={true}
              />
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default UserDashboard;
