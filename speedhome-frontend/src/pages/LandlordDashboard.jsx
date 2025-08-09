import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import PropertyAPI from '../services/PropertyAPI';
import ApplicationAPI from '../services/ApplicationAPI';
import BookingAPI from '../services/BookingAPI';
import ProfileAPI from '../services/ProfileAPI';
import MessagingAPI from '../services/MessagingAPI';
import TenancyAgreementAPI from '../services/TenancyAgreementAPI';
import RecurringAvailabilityManager from '../components/RecurringAvailabilityManager';
import UnifiedCalendar from '../components/UnifiedCalendar';
import MessagingCenter from '../components/MessagingCenter';
import ApplicationDetailsModal from '../components/ApplicationDetailsModal';
import PropertyStatusBadge from '../components/PropertyStatusBadge';
import PropertyStatusControls from '../components/PropertyStatusControls';
import { useNavigate } from 'react-router-dom';
import { formatDate, formatTime, formatDateTime } from '../utils/dateUtils';


const LandlordDashboard = ({ onAddProperty }) => {
  const navigate = useNavigate();
  const { user, isAuthenticated, isLandlord } = useAuth();
  const [activeTab, setActiveTab] = useState('properties');
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [showAddPropertyModal, setShowAddPropertyModal] = useState(false);
  const [showEditPropertyModal, setShowEditPropertyModal] = useState(false);
  const [editingProperty, setEditingProperty] = useState(null);
  const [expandedRequestId, setExpandedRequestId] = useState(null);
  const [conversations, setConversations] = useState([]);
  // Add this line near your other state declarations
  const hasNewMessages = conversations.some(convo => convo.unread_count > 0);

  // State for tenancy agreements
  const [tenancyAgreements, setTenancyAgreements] = useState([]);
  const [agreementsLoading, setAgreementsLoading] = useState(false);


  // --- NEW: State for the Reschedule Modal ---
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [rescheduleData, setRescheduleData] = useState({
    bookingId: null,
    newDate: '',
    newTime: ''
  });

  // --- NEW: State for the Availability Manager Modal ---
  const [showAvailabilityModal, setShowAvailabilityModal] = useState(false);
  const [selectedPropertyForAvailability, setSelectedPropertyForAvailability] = useState(null);

  // START REPLACING HERE
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
  });

  useEffect(() => {
    const fetchProfileData = async () => {
      if (user) {
        const result = await ProfileAPI.getProfile();
        if (result.success) {
          setProfileData(result.profile);
        } else {
          console.error("Failed to load profile data:", result.error);
        }
      }
    };
    fetchProfileData();
  }, [user]);

  // Add this useEffect hook to load conversations when the component mounts
    useEffect(() => {
      const loadConversations = async () => {
        if (user) {
          try {
            const response = await MessagingAPI.getConversations();
            if (response.success) {
              setConversations(response.conversations);
            }
          } catch (error) {
            console.error("Failed to load conversations:", error);
          }
        }
      };

      loadConversations();
    }, [user]); // This runs once when the user is loaded

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleProfileSave = async (e) => {
    e.preventDefault();
    try {
      const result = await ProfileAPI.updateProfile(profileData);
      if (result.success) {
        alert('Profile updated successfully!');
        // Optionally re-fetch data to confirm
        setProfileData(result.profile);
      } else {
        alert(`Failed to update profile: ${result.error}`);
      }
    } catch (error) {
      alert('An error occurred while saving your profile.');
    }
  };

  const handleMarkAsSeen = async (bookingId) => {
    try {
      await BookingAPI.markAsSeen(bookingId);
      setViewingRequests(prevRequests =>
        prevRequests.map(req =>
          req.id === bookingId ? { ...req, is_seen_by_landlord: true } : req
        )
      );
    } catch (error) {
      console.error("Failed to mark booking as seen:", error);
    }
  };


  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
      return;
    }

    if (!isLandlord()) {
      alert('Access denied. This page is for landlords only.');
      navigate('/dashboard');
      return;
    }
  }, [isAuthenticated, isLandlord, navigate]);

  // Initialize properties with user-owned properties from API
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load user's properties from API
  const loadProperties = async () => {
    if (!isAuthenticated || !user) return;

    try {
      setLoading(true);
      const result = await PropertyAPI.getPropertiesByOwner(user.id);

      if (result.success) {
        setProperties(result.properties);
      } else {
        console.error('Failed to load properties:', result.error);
        // Set empty array if API fails - no localStorage fallback
        setProperties([]);
      }
    } catch (error) {
      console.error('Error loading properties:', error);
      // Set empty array on error - no localStorage fallback
      setProperties([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProperties();
  }, [isAuthenticated, user]);

  // Load tenancy agreements
  const loadAgreements = async () => {
    if (!isAuthenticated || !user) return;

    try {
      setAgreementsLoading(true);
      const result = await TenancyAgreementAPI.getAll();

      if (result.success) {
        setTenancyAgreements(result.agreements);
      } else {
        console.error('Failed to load agreements:', result.error);
        setTenancyAgreements([]);
      }
    } catch (error) {
      console.error('Error loading agreements:', error);
      setTenancyAgreements([]);
    } finally {
      setAgreementsLoading(false);
    }
  };

  useEffect(() => {
    loadAgreements();
  }, [isAuthenticated, user]);

  // State for viewing requests - load from localStorage
  const [viewingRequests, setViewingRequests] = useState([]);

  // Load viewing requests from database API instead of localStorage
  useEffect(() => {
    const loadViewingRequests = async () => {
      if (!isAuthenticated || !user) return;

      try {
        const result = await BookingAPI.getBookingsByLandlord(user.id);

        if (result.success) {
          setViewingRequests(result.bookings);
        } else {
          console.error('Failed to load viewing requests:', result.error);
          setViewingRequests([]);
        }
      } catch (error) {
        console.error('Error loading viewing requests:', error);
        setViewingRequests([]);
      }
    };

    loadViewingRequests();

    // Set up an interval to check for new bookings every 5 seconds
    const interval = setInterval(loadViewingRequests, 5000);

    return () => clearInterval(interval);
  }, [isAuthenticated, user]);

  // Listen for property updates (add/edit/delete) and refresh properties
  useEffect(() => {
    const handlePropertyUpdate = () => {
      // Reload properties from database when properties are updated
      loadProperties();
    };

    // Listen for property update events
    window.addEventListener('propertyUpdated', handlePropertyUpdate);

    return () => {
      window.removeEventListener('propertyUpdated', handlePropertyUpdate);
    };
  }, []);

  // Form state for adding new property
  const [newProperty, setNewProperty] = useState({
    title: '',
    location: '',
    price: '',
    sqft: '',
    bedrooms: '',
    bathrooms: '',
    parking: '',
    propertyType: 'Apartment',
    furnished: 'Unfurnished',
    description: '',
    amenities: [],
    tags: [],
    pictures: [],
    videoLinks: '',
    floorPlan: '',
    zeroDeposit: false,
    cookingReady: false,
    hotProperty: false,
  });

  const hasNewViewingRequests = viewingRequests.some(req => !req.is_seen_by_landlord);

  // State for tenant applications
  const [tenantApplications, setTenantApplications] = useState([]);

  const hasNewApplications = tenantApplications.some(app => !app.is_seen_by_landlord);
  // State for application details modal
  const [showApplicationDetails, setShowApplicationDetails] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState(null);

  const loadApplications = async () => {
    if (!isAuthenticated || !user) return;
    try {
      const result = await ApplicationAPI.getApplicationsByLandlord();
      if (result.success) {
        setTenantApplications(result.applications);
      } else {
        console.error('Failed to load applications:', result.error);
      }
    } catch (error) {
      console.error('Error loading applications:', error);
    }
  };

  // Call this new function inside a useEffect
  useEffect(() => {
    loadApplications();
  }, [isAuthenticated, user]);

  // Mock data for earnings
  const earningsData = {
    totalEarnings: 'RM 0',
    pendingPayments: 'RM 0',
    thisMonth: 'RM 0',
    lastMonth: 'RM 0',
    transactions: [],
  };


  // Handle viewing request response
  const handleViewingResponse = (requestId, response) => {
    // Update the viewing request status
    setViewingRequests((prevRequests) =>
      prevRequests.map((request) =>
        request.id === requestId
          ? {
            ...request,
            status:
              response === 'confirmed'
                ? 'Confirmed'
                : response === 'declined'
                  ? 'Declined'
                  : 'Rescheduled',
          }
          : request
      )
    );

    // Show success message
    const actionText =
      response === 'confirmed'
        ? 'confirmed'
        : response === 'declined'
          ? 'declined'
          : 'rescheduled';
    alert(`Viewing request has been ${actionText} successfully!`);

    // In a real app, this would also:
    // 1. Send notification to the tenant
    // 2. Update the database
    // 3. Send confirmation email
    console.log(`Viewing request ${requestId} ${actionText}`);
  };

  // Handle tenant application response
  // Handle viewing request response
  const handleViewingRequestResponse = async (bookingId, response) => {
    try {
      // Map response to API status
      const status = response === 'approved' ? 'confirmed' : 'cancelled';

      const result = await BookingAPI.updateBookingStatus(bookingId, status);

      if (result.success) {
        // Update the booking status in state
        const updatedBookings = viewingRequests.map((booking) =>
          booking.id === bookingId ? { ...booking, status: status } : booking
        );
        setViewingRequests(updatedBookings);

        const actionText = response === 'approved' ? 'confirmed' : 'declined';
        alert(`Viewing request has been ${actionText} successfully!`);
      } else {
        alert(
          `Failed to ${response === 'approved' ? 'approve' : 'decline'
          } viewing request: ${result.error}`
        );
      }
    } catch (error) {
      console.error('Error updating viewing request:', error);
      alert('An error occurred while updating the viewing request');
    }
  };

  // --- NEW: Function to open the reschedule modal ---
  const openRescheduleModal = (bookingId) => {
    setRescheduleData({ bookingId, newDate: '', newTime: '' });
    setShowRescheduleModal(true);
  };

  // --- NEW: Handler for submitting the reschedule request from the modal ---
  const handleRescheduleSubmit = async (e) => {
    e.preventDefault();
    const { bookingId, newDate, newTime } = rescheduleData;
    if (!newDate || !newTime) {
      alert('Please select a new date and time.');
      return;
    }
    try {
      const result = await BookingAPI.rescheduleBooking(bookingId, {
        date: newDate,
        time: newTime,
        requested_by: 'landlord',
      });
      if (result.success) {
        // CORRECT ORDER: Close modal first, then alert, then refresh data.
        setShowRescheduleModal(false);
        alert('Reschedule request sent successfully!');
        await loadViewingRequests();
      } else {
        alert(`Failed to send reschedule request: ${result.error}`);
      }
    } catch (error) {
      console.error('Error sending reschedule request:', error);
    }
  };

  // Handle reschedule request
  const handleRescheduleRequest = async (bookingId) => {
    const booking = viewingRequests.find((req) => req.id === bookingId);
    if (!booking) return;

    const newDate = prompt(
      'Enter new date (YYYY-MM-DD):',
      booking.appointment_date
    );
    if (!newDate) return;

    const newTime = prompt(
      'Enter new time (HH:MM):',
      booking.appointment_time
    );
    if (!newTime) return;

    try {
      const result = await BookingAPI.rescheduleBooking(bookingId, {
        date: newDate,
        time: newTime,
        requested_by: 'landlord',
      });

      if (result.success) {
        const updatedResult = await BookingAPI.getBookingsByLandlord(user.id);
        if (updatedResult.success) {
          setViewingRequests(updatedResult.bookings);
        }

        alert(
          `Reschedule request sent! Proposed new date: ${formatDate(
            newDate
          )} at ${formatTime(newTime)}`
        );
      } else {
        alert(`Failed to send reschedule request: ${result.error}`);
      }
    } catch (error) {
      console.error('Error sending reschedule request:', error);
      alert('An error occurred while sending the reschedule request');
    }
  };

  const toggleRequestDetails = (requestId) => {
    setExpandedRequestId(expandedRequestId === requestId ? null : requestId);
  };


  // Handle reschedule response
  const handleRescheduleResponse = async (bookingId, response) => {
    try {
      let result;
      if (response === 'approved') {
        result = await BookingAPI.approveReschedule(bookingId);
        if (result.success) {
          alert('Reschedule request has been accepted!');
        } else {
          alert(`Failed to approve reschedule: ${result.error}`);
          return; // Stop if it failed
        }
      } else if (response === 'declined') {
        // This now calls your existing, correct BookingAPI function
        result = await BookingAPI.declineReschedule(bookingId);
        if (result.success) {
          alert('Reschedule request has been declined!');
        } else {
          alert(`Failed to decline reschedule: ${result.error}`);
          return; // Stop if it failed
        }
      }

      // If either action was successful, refresh the data
      const updatedResult = await BookingAPI.getBookingsByLandlord(user.id);
      if (updatedResult.success) {
        setViewingRequests(updatedResult.bookings);
      }

    } catch (error) {
      console.error('Error responding to reschedule request:', error);
      alert('An error occurred while responding to the reschedule request');
    }
  };

  const handleMarkApplicationAsSeen = async (applicationId) => {
  try {
    // This is a new API endpoint you'll need to create
    await ApplicationAPI.markAsSeen(applicationId);
    setTenantApplications(prevApps =>
      prevApps.map(app =>
        app.id === applicationId ? { ...app, is_seen_by_landlord: true } : app
      )
    );
  } catch (error) {
    console.error("Failed to mark application as seen:", error);
  }
};



  // Handle cancel reschedule request
  const handleCancelReschedule = async (bookingId) => {
    if (!confirm('Are you sure you want to cancel this reschedule request? The original date and time will be restored.')) {
      return;
    }

    try {
      const result = await BookingAPI.cancelReschedule(bookingId);

      if (result.success) {
        const updatedResult = await BookingAPI.getBookingsByLandlord(user.id);
        if (updatedResult.success) {
          setViewingRequests(updatedResult.bookings);
        }

        alert('Reschedule request has been cancelled. Original date and time restored.');
      } else {
        alert(`Failed to cancel reschedule request: ${result.error}`);
      }
    } catch (error) {
      console.error('Error cancelling reschedule request:', error);
      alert('An error occurred while cancelling the reschedule request');
    }
  };

  // Handle tenant application response
  const handleApplicationResponse = async (applicationId, response) => {
  const application = tenantApplications.find(app => app.id === applicationId);
  if (application && !application.is_seen_by_landlord) {
    handleMarkApplicationAsSeen(applicationId);
  }

  const newStatus = response === 'approved' ? 'approved' : 'rejected';

  try {
    // This single call tells the backend to approve the application.
    // The backend will now automatically create the tenancy agreement.
    const result = await ApplicationAPI.updateApplicationStatus(applicationId, newStatus);

    if (result.success) {
      alert(`Tenant application has been ${newStatus} successfully!`);

      // Refresh both lists to show the updated state
      await loadApplications();
      await loadAgreements();
    } else {
      alert(`Failed to update application: ${result.error}`);
    }
  } catch (error) {
    console.error('Error updating application status:', error);
    alert('An error occurred while updating the application.');
  }
};



  // Handle viewing application details
  const handleViewApplicationDetails = (application) => {
  if (!application.is_seen_by_landlord) {
    handleMarkApplicationAsSeen(application.id);
  }
  setSelectedApplication(application);
  setShowApplicationDetails(true);
};

  // Handle closing application details modal
  const handleCloseApplicationDetails = () => {
    setShowApplicationDetails(false);
    setSelectedApplication(null);
  };

  // Handle property row click to navigate to property listing
  const handlePropertyRowClick = (propertyId) => {
    navigate(`/property/${propertyId}`);
  };

  // Handle adding new property
  const handleAddProperty = async (e) => {
    e.preventDefault();

    // Validate required fields
    if (!newProperty.title || !newProperty.location || !newProperty.price) {
      alert('Please fill in all required fields (Title, Location, Price)');
      return;
    }

    try {
      // Prepare property data for API
      const propertyData = {
        title: newProperty.title,
        location: newProperty.location,
        price: parseInt(newProperty.price),
        sqft: parseInt(newProperty.sqft) || 0,
        bedrooms: parseInt(newProperty.bedrooms) || 0,
        bathrooms: parseInt(newProperty.bathrooms) || 0,
        parking: parseInt(newProperty.parking) || 0,
        propertyType: newProperty.propertyType || 'Apartment',
        furnished: newProperty.furnished || 'Unfurnished',
        description: newProperty.description || '',
        amenities: newProperty.amenities || [],
        zeroDeposit: newProperty.zeroDeposit || false,
        cookingReady: newProperty.cookingReady || false,
        hotProperty: newProperty.hotProperty || false,
        videoLinks: newProperty.videoLinks || '',
        ownerId: user.id, // Use the authenticated user's ID
      };

      // Add property via API
      const result = await PropertyAPI.createProperty(propertyData);

      if (result.success) {
        // Property added successfully
        alert('Property added successfully!');

        // Refresh properties from database
        await loadProperties();

        // Dispatch custom event to notify other components (like homepage)
        window.dispatchEvent(new CustomEvent('propertyUpdated'));

        // Close modal and reset form
        setShowAddPropertyModal(false);
        setNewProperty({
          title: '',
          location: '',
          price: '',
          sqft: '',
          bedrooms: '',
          bathrooms: '',
          parking: '',
          propertyType: 'Apartment',
          furnished: 'Unfurnished',
          description: '',
          amenities: [],
          tags: [],
          pictures: [],
          videoLinks: '',
          floorPlan: null,
          zeroDeposit: false,
          cookingReady: false,
          hotProperty: false,
        });
      } else {
        alert('Failed to add property: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error adding property:', error);
      alert('Failed to add property. Please try again.');
    }
  };

  // Handle editing property
  const handleEditProperty = (property) => {
    try {
      // Validate property data before proceeding
      if (!property || !property.id) {
        console.error('Invalid property data:', property);
        alert('Error: Invalid property data. Cannot edit this property.');
        return;
      }

      setEditingProperty(property);
      setNewProperty({
        title: property.title || '',
        location: property.location || '',
        price: (property.price || '').toString(),
        sqft: (property.sqft || '').toString(),
        bedrooms: (property.bedrooms || '').toString(),
        bathrooms: (property.bathrooms || '').toString(),
        parking: (property.parking || '').toString(),
        propertyType: property.propertyType || 'Apartment',
        furnished: property.furnished || 'Unfurnished',
        description: property.description || '',
        amenities: property.amenities || [],
        tags: property.tags || [],
        pictures: property.pictures || [],
        videoLinks: property.videoLinks || '',
        floorPlan: property.floorPlan || null,
        // Special features with proper fallbacks
        zeroDeposit: property.zeroDeposit || false,
        cookingReady: property.cookingReady || false,
        hotProperty: property.hotProperty || false,
      });
      setShowEditPropertyModal(true);
    } catch (error) {
      console.error('Error in handleEditProperty:', error);
      alert('Error: Unable to edit this property. Please try again.');
    }
  };

  // Handle updating property
  // Handle updating property
  const handleUpdateProperty = async (e) => {
    e.preventDefault();

    if (!newProperty.title || !newProperty.location || !newProperty.price) {
      alert('Please fill in all required fields (Title, Location, Price)');
      return;
    }

    try {
      const updatedPropertyData = {
        title: newProperty.title,
        location: newProperty.location,
        price: parseInt(newProperty.price),
        sqft: parseInt(newProperty.sqft) || 0,
        bedrooms: parseInt(newProperty.bedrooms) || 0,
        bathrooms: parseInt(newProperty.bathrooms) || 0,
        parking: parseInt(newProperty.parking) || 0,
        propertyType: newProperty.propertyType || 'Apartment',
        furnished: newProperty.furnished || 'Unfurnished',
        description: newProperty.description || '',
        amenities: newProperty.amenities || [],
        zeroDeposit: newProperty.zeroDeposit || false,
        cookingReady: newProperty.cookingReady || false,
        hotProperty: newProperty.hotProperty || false,
        videoLinks: newProperty.videoLinks || '',
      };

      // Call API to update property in database
      const result = await PropertyAPI.updateProperty(editingProperty.id, updatedPropertyData);

      if (result.success) {
        // Refresh properties from database
        await loadProperties();

        // Dispatch custom event to notify other components
        window.dispatchEvent(new CustomEvent('propertyUpdated'));

        setShowEditPropertyModal(false);
        setEditingProperty(null);

        // Reset form
        setNewProperty({
          title: '',
          location: '',
          price: '',
          sqft: '',
          bedrooms: '',
          bathrooms: '',
          parking: '',
          propertyType: 'Apartment',
          furnished: 'Unfurnished',
          description: '',
          amenities: [],
          tags: [],
          pictures: [],
          videoLinks: '',
          floorPlan: '',
          zeroDeposit: false,
          cookingReady: false,
          hotProperty: false,
        });

        alert('Property updated successfully!');
      } else {
        alert(`Failed to update property: ${result.error}`);
      }
    } catch (error) {
      console.error('Error updating property:', error);
      alert('An error occurred while updating the property');
    }
  };

    const handleConversationRead = async () => {
  // Re-fetch conversations to get the latest unread counts
  try {
    const response = await MessagingAPI.getConversations();
    if (response.success) {
      setConversations(response.conversations);
    }
  } catch (error) {
    console.error("Failed to re-load conversations:", error);
  }
};

  // Handle deleting property
  const handleDeleteProperty = async (propertyId) => {
    // Keep the confirmation dialog as a safety measure
    if (
      window.confirm(
        'Are you sure you want to delete this property? This action cannot be undone.'
      )
    ) {
      try {
        // Call the API to delete the property from the database
        const result = await PropertyAPI.deleteProperty(propertyId);

        if (result.success) {
          alert('Property deleted successfully!');

          // Refresh the property list from the server to update the UI
          await loadProperties();

          // Notify other parts of the app (like the homepage) that a property has changed
          window.dispatchEvent(new CustomEvent('propertyUpdated'));

        } else {
          alert(`Failed to delete property: ${result.error}`);
        }
      } catch (error) {
        console.error('Error deleting property:', error);
        alert('An error occurred while deleting the property. Please try again.');
      }
    }
  };

  // Handle opening availability manager modal
  const handleManageAvailability = (property) => {
    setSelectedPropertyForAvailability(property);
    setShowAvailabilityModal(true);
  };

  // Handle closing availability manager modal
  const handleCloseAvailabilityModal = () => {
    setShowAvailabilityModal(false);
    setSelectedPropertyForAvailability(null);
  };

  // Handle successful availability setting
  const handleAvailabilitySuccess = (result) => {
    alert(`Availability set successfully! Created ${result.slots_created || 0} viewing slots.`);
    // Optionally refresh properties or show success message
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewProperty((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // ============================================================================
  // PROPERTY STATUS MANAGEMENT HANDLERS
  // ============================================================================

  // Handle property status change
  const handlePropertyStatusChange = async (propertyId, newStatus) => {
    try {
      let result;
      
      switch (newStatus) {
        case 'Active':
          result = await PropertyAPI.reactivateProperty(propertyId);
          break;
        case 'Inactive':
          result = await PropertyAPI.deactivateProperty(propertyId);
          break;
        default:
          result = await PropertyAPI.updatePropertyStatus(propertyId, newStatus);
          break;
      }

      if (result.success) {
        // Refresh properties to show updated status
        await loadProperties();
        
        // Notify other parts of the app (like the homepage) that a property has changed
        window.dispatchEvent(new CustomEvent('propertyUpdated'));
        
        alert(result.message || `Property status updated to ${newStatus}`);
      } else {
        alert(`Failed to update property status: ${result.error}`);
      }
    } catch (error) {
      console.error('Error updating property status:', error);
      alert(`Error updating property status: ${error.message}`);
    }
  };

  // Handle property re-listing for future availability
  const handlePropertyRelist = async (propertyId, availableFromDate) => {
    try {
      const result = await PropertyAPI.relistProperty(propertyId, availableFromDate);
      
      if (result.success) {
        // Refresh properties to show updated status
        await loadProperties();
        
        // Notify other parts of the app (like the homepage) that a property has changed
        window.dispatchEvent(new CustomEvent('propertyUpdated'));
        
        alert(result.message || 'Property re-listed successfully');
      } else {
        alert(`Failed to re-list property: ${result.error}`);
      }
    } catch (error) {
      console.error('Error re-listing property:', error);
      alert(`Error re-listing property: ${error.message}`);
    }
  };
  const renderActiveTab = () => {
    switch (activeTab) {
      case 'properties':
        return (
          <div>
            <div className="flex flex-col">
              <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                  <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        {/* Table Headers */}
                        <tr>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Property</th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Views</th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Inquiries</th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {properties.map((property) => (
                          <tr key={property.id} onClick={() => navigate(`/property/${property.id}`)} className="hover:bg-gray-50 cursor-pointer">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <div className="flex-shrink-0 h-10 w-10">
                                  <img className="h-10 w-10 rounded-md object-cover" src={property.image} alt={property.title} />
                                </div>
                                <div className="ml-4">
                                  <div className="text-sm font-medium text-gray-900">{property.title}</div>
                                  <div className="text-sm text-gray-500">{property.location}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <PropertyStatusBadge 
                                status={property.status} 
                                availableFromDate={property.available_from_date}
                                size="sm"
                              />
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{property.views}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{property.inquiries}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">RM {property.price.toLocaleString()}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex flex-col space-y-2" onClick={(e) => e.stopPropagation()}>
                                <div className="flex space-x-2">
                                  <button onClick={() => handleEditProperty(property)} className="text-blue-600 hover:text-blue-900">Edit</button>
                                  <button onClick={() => handleDeleteProperty(property.id)} className="text-red-600 hover:text-red-900">Delete</button>
                                </div>
                                <PropertyStatusControls
                                  property={property}
                                  onStatusChange={handlePropertyStatusChange}
                                  onRelistProperty={handlePropertyRelist}
                                />
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'viewings':
        return (
          <div>
                <div className="flex flex-col">
                  <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                    <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                      <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Property
                              </th>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Tenant
                              </th>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Date & Time
                              </th>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Status
                              </th>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Actions
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {viewingRequests.length === 0 ? (
                              <tr>
                                <td colSpan="5" className="px-6 py-8 text-center">
                                  <div className="text-gray-500">
                                    <svg
                                      className="mx-auto h-12 w-12 text-gray-400"
                                      fill="none"
                                      viewBox="0 0 24 24"
                                      stroke="currentColor"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                                      />
                                    </svg>
                                    <h3 className="mt-2 text-sm font-medium text-gray-900">
                                      No viewing requests
                                    </h3>
                                    <p className="mt-1 text-sm text-gray-500">
                                      When tenants schedule property viewings,
                                      they will appear here.
                                    </p>
                                  </div>
                                </td>
                              </tr>
                            ) : (
                              viewingRequests.map((request) => {
                                // Get the property ID from the request object
                                const propertyId = request.propertyId || request.property_id || request.propertyID;

                                // Use the ID to find the matching property in your `properties` state array
                                const property = properties.find(p => p.id == propertyId);
                                const isNew = !request.is_seen_by_landlord;

                                return (
                                  <React.Fragment key={request.id}>
                                    <tr
                                      // The key={request.id} is removed from here
                                      className={`transition-colors duration-300 ${isNew ? 'bg-red-50 hover:bg-red-100' : 'hover:bg-gray-50'}`}
                                      onClick={() => {
                                        if (isNew) {
                                          handleMarkAsSeen(request.id);
                                        }
                                        toggleRequestDetails(request.id);
                                      }}
                                    >
                                      <td className="px-6 py-4 whitespace-nowrap">
                                        {/* Line 1: The Property Title */}
                                        <div className="text-sm font-medium text-gray-900">
                                          {property ? property.title : 'Title Unavailable'}
                                        </div>
                                        {/* Line 2: The Property Address/Location */}
                                        <div className="text-sm text-gray-500">
                                          {property ? property.location : 'Address Unavailable'}
                                        </div>
                                      </td>
                                      <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">
                                          {request.name}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                          {request.phone}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                          {request.email}
                                        </div>
                                      </td>
                                      <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">
                                          {formatDate(request.appointment_date)}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                          {formatTime(request.appointment_time)}
                                        </div>
                                      </td>
                                      <td className="px-6 py-4 whitespace-nowrap">
                                        <span
                                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${request.status === 'Confirmed'
                                              ? 'bg-green-100 text-green-800'
                                              : request.status === 'Pending'
                                                ? 'bg-yellow-100 text-yellow-800'
                                                : 'bg-red-100 text-red-800'
                                            }`}
                                        >
                                          {request.status}
                                        </span>
                                      </td>
                                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            toggleRequestDetails(request.id);
                                          }}
                                          className="text-blue-600 hover:text-blue-900 text-xs mr-2 mb-1 block"
                                        >
                                          {expandedRequestId === request.id ? '▲ Hide Details' : '▼ View Details'}
                                        </button>
                                        {(request.status === 'Pending' ||
                                          request.status === 'pending') &&
                                          !request.reschedule_requested_by && (
                                            <div className="flex space-x-2 mb-2">
                                              <button
                                                onClick={(e) => {
                                                  e.stopPropagation();
                                                  handleViewingRequestResponse(
                                                    request.id,
                                                    'approved'
                                                  );
                                                }}
                                                id="confirmButton"
                                                className="bg-green-500 hover:bg-green-600 text-white px-2 py-1 rounded-md text-xs"
                                              >
                                                Confirm
                                              </button>
                                              <button
                                                onClick={(e) => {
                                                  e.stopPropagation();
                                                  handleViewingRequestResponse(
                                                    request.id,
                                                    'declined'
                                                  );
                                                }}
                                                id="declineButton"
                                                className="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded-md text-xs"
                                              >
                                                Decline
                                              </button>
                                            </div>
                                          )}
                                        {/* Message Tenant button for pending and confirmed bookings */}
                                        {(request.status === 'Pending' || request.status === 'pending' ||
                                          request.status === 'Confirmed' || request.status === 'confirmed') && (
                                            <button
                                              onClick={async (e) => {
                                                e.stopPropagation();
                                                try {
                                                  // Get or create conversation for this booking
                                                  const response = await MessagingAPI.getOrCreateConversation(request.id);
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
                                              className="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded-md text-xs mb-2"
                                            >
                                              💬 Message Tenant
                                            </button>
                                          )}
                                        {/* This is the section that has been changed */}
                                        {(request.status === 'Confirmed' ||
                                          request.status === 'confirmed') && (
                                            <div className="flex space-x-2">
                                              {/* The "Confirmed" text span has been removed */}
                                              <button
                                                onClick={(e) => {
                                                  e.stopPropagation();
                                                  openRescheduleModal(request.id);
                                                }}
                                                id="rescheduleButton"
                                                className="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded-md text-xs"
                                              >
                                                Reschedule
                                              </button>
                                            </div>
                                          )}
                                        {/* Reschedule Status Display */}
                                        {(request.status === 'pending' || request.status === 'Reschedule Requested') &&
                                          (request.reschedule_requested_by ||
                                            request.rescheduleRequestedBy) && (
                                            <div className="flex flex-col space-y-1">
                                              <span className="text-orange-600 text-xs font-medium">
                                                Reschedule Requested
                                              </span>
                                              <div className="text-xs text-gray-500">
                                                {request.proposed_date && request.proposed_time ? (
                                                  <>
                                                    New:{' '}
                                                    {formatDate(request.proposed_date)}{' '}
                                                    at{' '}
                                                    {formatTime(request.proposed_time)}
                                                  </>
                                                ) : (
                                                  request.reschedule_requested_by === 'landlord' ?
                                                    'Waiting for tenant response' :
                                                    'Tenant will choose new time'
                                                )}
                                              </div>

                                              {/* Show Accept/Decline buttons ONLY if tenant requested reschedule */}
                                              {request.reschedule_requested_by ===
                                                'tenant' ||
                                                request.rescheduleRequestedBy ===
                                                'tenant' ? (
                                                <div className="flex space-x-1">
                                                  <button
                                                    onClick={(e) => {
                                                      e.stopPropagation();
                                                      handleRescheduleResponse(
                                                        request.id,
                                                        'approved'
                                                      );
                                                    }}
                                                    id="acceptButton"
                                                    className="bg-green-500 hover:bg-green-600 text-white px-2 py-1 rounded-md text-xs"
                                                  >
                                                    Accept
                                                  </button>
                                                  <button
                                                    onClick={(e) => {
                                                      e.stopPropagation();
                                                      handleRescheduleResponse(
                                                        request.id,
                                                        'declined'
                                                      );
                                                    }}
                                                    id="declineButton"
                                                    className="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded-md text-xs"
                                                  >
                                                    Decline
                                                  </button>
                                                </div>
                                              ) : (
                                                /* Show waiting message and cancel button for landlord-initiated reschedules */
                                                <div className="flex flex-col space-y-1">
                                                  <span className="text-xs text-blue-600">
                                                    Waiting for tenant response
                                                  </span>
                                                  <button
                                                    onClick={(e) => {
                                                      e.stopPropagation();
                                                      handleCancelReschedule(request.id);
                                                    }}
                                                    className="bg-gray-500 hover:bg-gray-600 text-white px-2 py-1 rounded-md text-xs"
                                                  >
                                                    Cancel Request
                                                  </button>
                                                </div>
                                              )}
                                            </div>
                                          )}
                                        {(request.status === 'Declined' ||
                                          request.status === 'declined' ||
                                          request.status === 'cancelled') && (
                                            <span className="text-red-600 text-xs font-medium">
                                              Declined
                                            </span>
                                          )}
                                      </td>
                                    </tr>
                                    {expandedRequestId === request.id && (
                                      <tr className="bg-gray-50">
                                        <td colSpan="5" className="px-6 py-4">
                                          <div className="bg-white rounded-lg border border-gray-200 p-4">
                                            <h4 className="text-lg font-semibold text-gray-900 mb-3">
                                              Tenant Details
                                            </h4>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                              <div>
                                                <h5 className="font-medium text-gray-700 mb-2">Contact Information</h5>
                                                <div className="space-y-1 text-sm">
                                                  <div><span className="font-medium">Name:</span> {request.name}</div>
                                                  <div><span className="font-medium">Email:</span> {request.email}</div>
                                                  <div><span className="font-medium">Phone:</span> {request.phone}</div>
                                                </div>
                                              </div>
                                              <div>
                                                <h5 className="font-medium text-gray-700 mb-2">Appointment Details</h5>
                                                <div className="space-y-1 text-sm">
                                                  <div><span className="font-medium">Date:</span> {formatDate(request.appointment_date)}</div>
                                                  <div><span className="font-medium">Time:</span> {formatTime(request.appointment_time)}</div>
                                                  <div><span className="font-medium">Status:</span>
                                                    <span className={`ml-1 px-2 py-1 text-xs rounded-full ${request.status === 'Confirmed' ? 'bg-green-100 text-green-800' :
                                                        request.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                                                          'bg-red-100 text-red-800'
                                                      }`}>
                                                      {request.status}
                                                    </span>
                                                  </div>
                                                </div>
                                              </div>
                                              <div className="md:col-span-2 border-t pt-4">
                                                <h5 className="font-medium text-gray-700 mb-2">Employment & Occupancy</h5>
                                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                                  <div>
                                                    <span className="font-medium">Occupation:</span> {request.occupation || 'N/A'}
                                                  </div>
                                                  <div>
                                                    <span className="font-medium">Monthly Income:</span> {request.monthly_income ? `RM ${request.monthly_income.toLocaleString()}` : 'N/A'}
                                                  </div>
                                                  <div>
                                                    <span className="font-medium">Occupants:</span> {request.number_of_occupants || 'N/A'}
                                                  </div>
                                                </div>
                                              </div>
                                            </div>
                                            {request.message && (
                                              <div className="mt-4">
                                                <h5 className="font-medium text-gray-700 mb-2">Additional Message</h5>
                                                <div className="bg-gray-50 rounded-md p-3 text-sm text-gray-700">
                                                  {request.message}
                                                </div>
                                              </div>
                                            )}
                                            <div className="mt-4 pt-3 border-t border-gray-200">
                                              <div className="text-xs text-gray-500">
                                                Request submitted: {formatDateTime(request.created_at)}
                                              </div>
                                            </div>
                                          </div>
                                        </td>
                                      </tr>
                                    )}
                                  </React.Fragment>
                                );
                              })
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
        );
      case 'applications':
        return (
          <div>
                <div className="flex flex-col">
                  <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                    <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                      <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Property
                              </th>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Tenant
                              </th>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Details
                              </th>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Status
                              </th>
                              <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                Actions
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {tenantApplications.map((application) => {
  // Checks if the application has been seen
  const isNew = !application.is_seen_by_landlord;

  return (
    // Applies a blue background if 'isNew' is true
    <tr key={application.id} className={isNew ? 'bg-blue-50' : ''}>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="text-sm font-medium text-gray-900">
          {application.property?.title || 'N/A'}
        </div>
        <div className="text-sm text-gray-500">
          {application.property?.location || 'N/A'}
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="text-sm font-medium text-gray-900">
          {application.tenant?.full_name || 'N/A'}
        </div>
        <div className="text-sm text-gray-500">
          {application.tenant?.phone_number || 'N/A'}
        </div>
        <div className="text-sm text-gray-500">
          {application.tenant?.email || 'N/A'}
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="text-sm text-gray-900">
          Applied: {formatDate(application.created_at)}
        </div>
        <div className="text-sm text-gray-500">
          Move-in: {application.moveInDate || 'N/A'}
        </div>
        <div className="text-sm text-gray-500">
          Income: {application.monthlyIncome ? `RM ${application.monthlyIncome}` : 'N/A'}
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <span
          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${application.status === 'approved'
              ? 'bg-green-100 text-green-800'
              : application.status === 'pending'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}
        >
          {application.status}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
        {application.status === 'pending' && (
          <div className="flex space-x-2">
            <button
              onClick={() =>
                handleApplicationResponse(
                  application.id,
                  'approved'
                )
              }
              id="approveButton"
              className="bg-green-500 hover:bg-green-600 text-white px-2 py-1 rounded-md text-xs"
            >
              Approve
            </button>
            <button
              onClick={() =>
                handleApplicationResponse(
                  application.id,
                  'rejected'
                )
              }
              id="rejectButton"
              className="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded-md text-xs"
            >
              Reject
            </button>
          </div>
        )}
        <button
          onClick={() =>
            handleViewApplicationDetails(application)
          }
          className="text-blue-600 hover:text-blue-900 text-xs mt-1"
        >
          View Details
        </button>
      </td>
    </tr>
  );
})}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
        );
      case 'earnings':
        return (
          <div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-white rounded-lg shadow p-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      Total Earnings
                    </h3>
                    <p className="text-2xl font-bold text-green-600 mt-2">
                      {earningsData.totalEarnings}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      This Month
                    </h3>
                    <p className="text-2xl font-bold text-blue-600 mt-2">
                      {earningsData.thisMonth}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      Pending Payments
                    </h3>
                    <p className="text-2xl font-bold text-yellow-600 mt-2">
                      {earningsData.pendingPayments}
                    </p>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <div className="px-4 py-5 sm:px-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Transaction History
                    </h3>
                  </div>
                  <div className="border-t border-gray-200">
                    <div className="flex flex-col">
                      <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                        <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th
                                  scope="col"
                                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                >
                                  Property
                                </th>
                                <th
                                  scope="col"
                                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                >
                                  Tenant
                                </th>
                                <th
                                  scope="col"
                                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                >
                                  Date
                                </th>
                                <th
                                  scope="col"
                                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                >
                                  Amount
                                </th>
                                <th
                                  scope="col"
                                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                >
                                  Status
                                </th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {earningsData.transactions.map((transaction) => (
                                <tr key={transaction.id}>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm font-medium text-gray-900">
                                      {transaction.propertyTitle}
                                    </div>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                      {transaction.tenantName}
                                    </div>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                      {transaction.date}
                                    </div>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm font-medium text-gray-900">
                                      {transaction.amount}
                                    </div>
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap">
                                    <span
                                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${transaction.status === 'Received'
                                          ? 'bg-green-100 text-green-800'
                                          : 'bg-yellow-100 text-yellow-800'
                                        }`}
                                    >
                                      {transaction.status}
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
        );
      case 'calendar':
        return (
          <div>
            <UnifiedCalendar />
          </div>
        );
      case 'messages':
  return (
    <div className="bg-white rounded-lg shadow max-h-[600px] overflow-hidden">
      <div className="h-[600px] flex">
        <MessagingCenter
          user={user}
          selectedConversationId={selectedConversationId}
          onConversationSelect={setSelectedConversationId}
          onConversationRead={handleConversationRead}
        />
      </div>
    </div>
  );
      case 'profile':
        return (
          <div>
                <h2 className="text-xl font-bold text-gray-800 mb-4">Edit Your Profile</h2>
                <form onSubmit={handleProfileSave} className="space-y-6 max-w-lg">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">First Name</label>
                      <input
                        type="text"
                        name="first_name"
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
                        value={profileData.first_name || ''}
                        onChange={handleProfileChange}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Last Name</label>
                      <input
                        type="text"
                        name="last_name"
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
                        value={profileData.last_name || ''}
                        onChange={handleProfileChange}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Phone Number</label>
                    <input
                      type="text"
                      name="phone"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
                      value={profileData.phone || ''}
                      onChange={handleProfileChange}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Email Address</label>
                    <input
                      type="email"
                      name="email"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm bg-gray-100 cursor-not-allowed"
                      value={profileData.email || ''}
                      disabled
                    />
                    <p className="mt-1 text-xs text-gray-500">Email cannot be changed.</p>
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-yellow-400 hover:bg-yellow-500"
                    >
                      Save Changes
                    </button>
                  </div>
                </form>
              </div>
        );
      case 'agreements':
        return (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Tenancy Agreements</h2>
              <button
                onClick={loadAgreements}
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm"
              >
                Refresh
              </button>
            </div>

            {agreementsLoading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <p className="mt-2 text-gray-600">Loading agreements...</p>
              </div>
            ) : tenancyAgreements.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-400 text-6xl mb-4">📄</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Tenancy Agreements</h3>
                <p className="text-gray-600">Agreements will appear here when you approve tenant applications.</p>
              </div>
            ) : (
              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                  {tenancyAgreements.map((agreement) => (
                    <li key={agreement.id} className="px-6 py-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h3 className="text-lg font-medium text-gray-900">
                              {agreement.property_address}
                            </h3>
                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${TenancyAgreementAPI.getStatusColor(agreement.status)}`}>
                              {TenancyAgreementAPI.formatStatus(agreement.status)}
                            </span>
                          </div>
                          <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                            <div>
                              <span className="font-medium">Tenant:</span> {agreement.tenant_full_name}
                            </div>
                            <div>
                              <span className="font-medium">Monthly Rent:</span> RM {agreement.monthly_rent}
                            </div>
                            <div>
                              <span className="font-medium">Lease Start:</span> {new Date(agreement.lease_start_date).toLocaleDateString()}
                            </div>
                          </div>
                          <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                            <div>
                              <span className="font-medium">Landlord Signed:</span> 
                              {agreement.landlord_signed_at ? (
                                <span className="text-green-600 ml-1">✓ {new Date(agreement.landlord_signed_at).toLocaleDateString()}</span>
                              ) : (
                                <span className="text-yellow-600 ml-1">⏳ Pending</span>
                              )}
                            </div>
                            <div>
                              <span className="font-medium">Tenant Signed:</span>
                              {agreement.tenant_signed_at ? (
                                <span className="text-green-600 ml-1">✓ {new Date(agreement.tenant_signed_at).toLocaleDateString()}</span>
                              ) : (
                                <span className="text-yellow-600 ml-1">⏳ Pending</span>
                              )}
                            </div>
                            <div>
                              <span className="font-medium">Payment:</span>
                              {agreement.payment_completed_at ? (
                                <span className="text-green-600 ml-1">✓ Completed</span>
                              ) : (
                                <span className="text-yellow-600 ml-1">⏳ Pending</span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="ml-4 flex space-x-2">
                          <Link
                            to={`/agreement/${agreement.id}`}
                            className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm inline-block"
                          >
                            View Agreement
                          </Link>
                          {agreement.status === 'pending_signatures' && !agreement.landlord_signed_at && (
                            <Link
                              to={`/agreement/${agreement.id}`}
                              className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm inline-block"
                            >
                              Sign Agreement
                            </Link>
                          )}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
      default:
        return null; // Or return the default tab content, e.g., properties
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
              Landlord Dashboard
            </h1>
            <p className="text-gray-600 mt-1">
              Manage your properties, tenants, and earnings
            </p>
          </div>
          <div className="mt-4 md:mt-0">
            <button
              onClick={() => setShowAddPropertyModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-yellow-400 hover:bg-yellow-500"
            >
              + Add New Property
            </button>
          </div>
        </div>

        {/* Dashboard Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-4 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                <svg
                  className="h-6 w-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                  />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Properties
                  </dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {properties.length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                <svg
                  className="h-6 w-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Monthly Earnings
                  </dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {earningsData.thisMonth}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                <svg
                  className="h-6 w-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Views
                  </dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {properties.reduce((sum, prop) => sum + prop.views, 0)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                <svg
                  className="h-6 w-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Pending Viewings
                  </dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {
                      viewingRequests.filter((req) => req.status === 'Pending')
                        .length
                    }
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Tabs */}
        <div className="relative z-10 bg-white shadow rounded-lg overflow-hidden mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex">
              <button
                onClick={() => setActiveTab('properties')}
                className={`${activeTab === 'properties'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
              >
                My Properties
              </button>
              <button
                onClick={() => setActiveTab('viewings')}
                className={`${activeTab === 'viewings'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } relative whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm flex items-center`}
              >
                <span>Viewing Requests</span>
                {hasNewViewingRequests && (
                  <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-semibold bg-red-500 text-white">New</span>
                )}
              </button>
              <button
  onClick={() => setActiveTab('applications')}
  className={`${activeTab === 'applications'
      ? 'border-blue-500 text-blue-600'
      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
    } relative whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm flex items-center`}
>
  <span>Tenant Applications</span>
  {hasNewApplications && (
    <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-semibold bg-red-500 text-white">New</span>
  )}
</button>
              <button
                onClick={() => setActiveTab('earnings')}
                className={`${activeTab === 'earnings'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
              >
                Earnings
              </button>
              <button
                onClick={() => setActiveTab('calendar')}
                className={`${activeTab === 'calendar'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
              >
                📅 My Calendar
              </button>
              <button
                  onClick={() => setActiveTab('messages')}
                  className={`${activeTab === 'messages'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } relative whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm flex items-center`}
                >
                  <span>💬 Messages</span>
                  {hasNewMessages && (
                    <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-semibold bg-red-500 text-white">New</span>
                  )}
            </button>

              <button
                onClick={() => setActiveTab('agreements')}
                className={`${activeTab === 'agreements'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
              >
                📄 Agreements
              </button>

              <button
                onClick={() => setActiveTab('profile')}
                className={`${activeTab === 'profile'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
              >
                My Profile
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-4 sm:p-6">
            {renderActiveTab()}
          </div>
        </div>

        {/* Add Property Modal */}
        {showAddPropertyModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Add New Property
                  </h3>
                  <button
                    onClick={() => setShowAddPropertyModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <span className="sr-only">Close</span>
                    <svg
                      className="h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>

                <form onSubmit={handleAddProperty} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Property Title *
                      </label>
                      <input
                        type="text"
                        name="title"
                        value={newProperty.title}
                        onChange={handleInputChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Location *
                      </label>
                      <input
                        type="text"
                        name="location"
                        value={newProperty.location}
                        onChange={handleInputChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Monthly Rent (RM) *
                      </label>
                      <input
                        type="number"
                        name="price"
                        value={newProperty.price}
                        onChange={handleInputChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Size (sqft)
                      </label>
                      <input
                        type="number"
                        name="sqft"
                        value={newProperty.sqft}
                        onChange={handleInputChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Bedrooms
                      </label>
                      <input
                        type="number"
                        name="bedrooms"
                        value={newProperty.bedrooms}
                        onChange={handleInputChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Bathrooms
                      </label>
                      <input
                        type="number"
                        name="bathrooms"
                        value={newProperty.bathrooms}
                        onChange={handleInputChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Parking Spaces
                      </label>
                      <input
                        type="number"
                        name="parking"
                        value={newProperty.parking}
                        onChange={handleInputChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Property Type
                      </label>
                      <select
                        name="propertyType"
                        value={newProperty.propertyType}
                        onChange={handleInputChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                      >
                        <option value="Apartment">Apartment</option>
                        <option value="Condominium">Condominium</option>
                        <option value="Studio">Studio</option>
                        <option value="Penthouse">Penthouse</option>
                        <option value="House">House</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Furnishing
                      </label>
                      <select
                        name="furnished"
                        value={newProperty.furnished}
                        onChange={handleInputChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                      >
                        <option value="Unfurnished">Unfurnished</option>
                        <option value="Partially Furnished">
                          Partially Furnished
                        </option>
                        <option value="Fully Furnished">
                          Fully Furnished
                        </option>
                      </select>
                    </div>
                  </div>

                  {/* Media and Special Features Section */}
                  <div className="border-t pt-4 mt-4">
                    <h4 className="text-md font-medium text-gray-900 mb-4">
                      Media & Special Features
                    </h4>

                    {/* Enhanced Image Upload Section */}
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Property Pictures
                      </label>

                      {/* Drag & Drop Upload Area */}
                      <div
                        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-yellow-400 transition-colors cursor-pointer"
                        onDragOver={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.add(
                            'border-yellow-400',
                            'bg-yellow-50'
                          );
                        }}
                        onDragLeave={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.remove(
                            'border-yellow-400',
                            'bg-yellow-50'
                          );
                        }}
                        onDrop={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.remove(
                            'border-yellow-400',
                            'bg-yellow-50'
                          );
                          const files = Array.from(
                            e.dataTransfer.files
                          ).filter((file) => file.type.startsWith('image/'));
                          if (files.length > 0) {
                            const currentPictures =
                              newProperty.pictures || [];
                            const newFiles = [
                              ...currentPictures,
                              ...files,
                            ].slice(0, 10); // Limit to 10 images
                            setNewProperty((prev) => ({
                              ...prev,
                              pictures: newFiles,
                            }));
                          }
                        }}
                        onClick={() =>
                          document
                            .getElementById('property-images-input')
                            .click()
                        }
                      >
                        <div className="space-y-2">
                          <svg
                            className="mx-auto h-12 w-12 text-gray-400"
                            stroke="currentColor"
                            fill="none"
                            viewBox="0 0 48 48"
                          >
                            <path
                              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                              strokeWidth={2}
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                          <div className="text-sm text-gray-600">
                            <span className="font-medium text-yellow-600">
                              Click to upload
                            </span>{' '}
                            or drag and drop
                          </div>
                          <p className="text-xs text-gray-500">
                            PNG, JPG, GIF up to 5MB each (max 10 images)
                          </p>
                        </div>
                      </div>

                      {/* Hidden File Input */}
                      <input
                        id="property-images-input"
                        type="file"
                        multiple
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => {
                          const files = Array.from(e.target.files);
                          const currentPictures = newProperty.pictures || [];
                          const newFiles = [
                            ...currentPictures,
                            ...files,
                          ].slice(0, 10); // Limit to 10 images
                          setNewProperty((prev) => ({
                            ...prev,
                            pictures: newFiles,
                          }));
                        }}
                      />

                      {/* Image Preview Grid */}
                      {newProperty.pictures &&
                        newProperty.pictures.length > 0 && (
                          <div className="mt-4">
                            <h5 className="text-sm font-medium text-gray-700 mb-2">
                              Uploaded Images ({newProperty.pictures.length}
                              /10)
                            </h5>
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                              {newProperty.pictures.map((file, index) => (
                                <div key={index} className="relative group">
                                  <img
                                    src={URL.createObjectURL(file)}
                                    alt={`Property image ${index + 1}`}
                                    className="w-full h-20 object-cover rounded-lg border border-gray-200"
                                  />
                                  {/* Remove Button */}
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const newPictures =
                                        newProperty.pictures.filter(
                                          (_, i) => i !== index
                                        );
                                      setNewProperty((prev) => ({
                                        ...prev,
                                        pictures: newPictures,
                                      }));
                                    }}
                                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 transition-colors opacity-0 group-hover:opacity-100"
                                  >
                                    ×
                                  </button>
                                  {/* Main Image Badge */}
                                  {index === 0 && (
                                    <div className="absolute bottom-1 left-1 bg-yellow-500 text-white text-xs px-2 py-1 rounded">
                                      Main
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                            <p className="text-xs text-gray-500 mt-2">
                              First image will be used as the main property
                              photo. Drag to reorder.
                            </p>
                          </div>
                        )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Video Links
                        </label>
                        <input
                          type="url"
                          name="videoLinks"
                          value={newProperty.videoLinks}
                          onChange={handleInputChange}
                          placeholder="https://youtube.com/watch?v=..."
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          YouTube, Vimeo, or other video platform links
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Floor Plan
                        </label>
                        <input
                          type="file"
                          name="floorPlan"
                          accept="image/*,.pdf"
                          onChange={(e) => {
                            const file = e.target.files[0];
                            setNewProperty((prev) => ({
                              ...prev,
                              floorPlan: file,
                            }));
                          }}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Upload floor plan (Image or PDF)
                        </p>
                      </div>
                    </div>

                    {/* Special Features Checkboxes */}
                    <div className="mt-4">
                      <h5 className="text-sm font-medium text-gray-700 mb-3">
                        Special Features
                      </h5>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            name="zeroDeposit"
                            checked={newProperty.zeroDeposit}
                            onChange={(e) => {
                              setNewProperty((prev) => ({
                                ...prev,
                                zeroDeposit: e.target.checked,
                              }));
                            }}
                            className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
                          />
                          <label className="ml-2 block text-sm text-gray-900">
                            Zero Deposit
                            <span className="block text-xs text-gray-500">
                              No security deposit required
                            </span>
                          </label>
                        </div>

                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            name="cookingReady"
                            checked={newProperty.cookingReady}
                            onChange={(e) => {
                              setNewProperty((prev) => ({
                                ...prev,
                                cookingReady: e.target.checked,
                              }));
                            }}
                            className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
                          />
                          <label className="ml-2 block text-sm text-gray-900">
                            Cooking Ready
                            <span className="block text-xs text-gray-500">
                              Fully equipped kitchen with appliances
                            </span>
                          </label>
                        </div>

                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            name="hotProperty"
                            checked={newProperty.hotProperty}
                            onChange={(e) => {
                              setNewProperty((prev) => ({
                                ...prev,
                                hotProperty: e.target.checked,
                              }));
                            }}
                            className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
                          />
                          <label className="ml-2 block text-sm text-gray-900">
                            Hot Property
                            <span className="block text-xs text-gray-500">
                              High demand, premium location
                            </span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Amenities Section */}
                  <div className="border-t pt-4 mt-4">
                    <h4 className="text-md font-medium text-gray-900 mb-4">
                      Amenities
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                      {[
                        'Swimming Pool',
                        'Gym',
                        'Security',
                        'Parking',
                        'Playground',
                        'BBQ Area',
                        'Laundry',
                        'Concierge',
                        'Private Lift',
                        'Cooking Allowed',
                        'Air Conditioning',
                        'Balcony',
                        'Water Heater',
                        'Internet',
                      ].map((amenity) => (
                        <div key={amenity} className="flex items-center">
                          <input
                            type="checkbox"
                            id={`amenity-${amenity}`}
                            checked={
                              newProperty.amenities?.includes(amenity) || false
                            }
                            onChange={(e) => {
                              const isChecked = e.target.checked;
                              setNewProperty((prev) => ({
                                ...prev,
                                amenities: isChecked
                                  ? [...(prev.amenities || []), amenity]
                                  : (prev.amenities || []).filter(
                                    (a) => a !== amenity
                                  ),
                              }));
                            }}
                            className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
                          />
                          <label
                            htmlFor={`amenity-${amenity}`}
                            className="ml-2 block text-sm text-gray-900"
                          >
                            {amenity}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Description
                    </label>
                    <textarea
                      name="description"
                      value={newProperty.description}
                      onChange={handleInputChange}
                      rows={3}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                      placeholder="Describe your property..."
                    />
                  </div>

                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowAddPropertyModal(false)}
                      className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-yellow-400 hover:bg-yellow-500"
                    >
                      Add Property
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Edit Property Modal */}
        {showEditPropertyModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-2/3 xl:w-1/2 shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto">
              <div className="mt-3">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Edit Property
                  </h3>
                  <button
                    onClick={() => setShowEditPropertyModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <span className="sr-only">Close</span>
                    <svg
                      className="h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>

                <form onSubmit={handleUpdateProperty} className="space-y-6">
                  {/* Basic Property Information */}
                  <div>
                    <h4 className="text-md font-medium text-gray-900 mb-4">
                      Basic Information
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Property Title *
                        </label>
                        <input
                          type="text"
                          name="title"
                          value={newProperty.title}
                          onChange={handleInputChange}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Location *
                        </label>
                        <input
                          type="text"
                          name="location"
                          value={newProperty.location}
                          onChange={handleInputChange}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Monthly Rent (RM) *
                        </label>
                        <input
                          type="number"
                          name="price"
                          value={newProperty.price}
                          onChange={handleInputChange}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Size (sqft)
                        </label>
                        <input
                          type="number"
                          name="sqft"
                          value={newProperty.sqft}
                          onChange={handleInputChange}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Bedrooms
                        </label>
                        <input
                          type="number"
                          name="bedrooms"
                          value={newProperty.bedrooms}
                          onChange={handleInputChange}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Bathrooms
                        </label>
                        <input
                          type="number"
                          name="bathrooms"
                          value={newProperty.bathrooms}
                          onChange={handleInputChange}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Parking Spaces
                        </label>
                        <input
                          type="number"
                          name="parking"
                          value={newProperty.parking}
                          onChange={handleInputChange}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Property Type
                        </label>
                        <select
                          name="propertyType"
                          value={newProperty.propertyType}
                          onChange={handleInputChange}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        >
                          <option value="Apartment">Apartment</option>
                          <option value="Condominium">Condominium</option>
                          <option value="Studio">Studio</option>
                          <option value="Penthouse">Penthouse</option>
                          <option value="House">House</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Furnishing
                        </label>
                        <select
                          name="furnished"
                          value={newProperty.furnished}
                          onChange={handleInputChange}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        >
                          <option value="Unfurnished">Unfurnished</option>
                          <option value="Partially Furnished">
                            Partially Furnished
                          </option>
                          <option value="Fully Furnished">
                            Fully Furnished
                          </option>
                        </select>
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700">
                        Description
                      </label>
                      <textarea
                        name="description"
                        value={newProperty.description}
                        onChange={handleInputChange}
                        rows={3}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        placeholder="Describe your property..."
                      />
                    </div>
                  </div>

                  {/* Media and Special Features Section */}
                  <div className="border-t pt-4 mt-4">
                    <h4 className="text-md font-medium text-gray-900 mb-4">
                      Media & Special Features
                    </h4>

                    {/* Enhanced Image Upload Section */}
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Property Pictures
                      </label>

                      {/* Drag & Drop Upload Area */}
                      <div
                        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-yellow-400 transition-colors cursor-pointer"
                        onDragOver={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.add(
                            'border-yellow-400',
                            'bg-yellow-50'
                          );
                        }}
                        onDragLeave={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.remove(
                            'border-yellow-400',
                            'bg-yellow-50'
                          );
                        }}
                        onDrop={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.remove(
                            'border-yellow-400',
                            'bg-yellow-50'
                          );
                          const files = Array.from(
                            e.dataTransfer.files
                          ).filter((file) => file.type.startsWith('image/'));
                          if (files.length > 0) {
                            const currentPictures = newProperty.pictures || [];
                            const newFiles = [
                              ...currentPictures,
                              ...files,
                            ].slice(0, 10); // Limit to 10 images
                            setNewProperty((prev) => ({
                              ...prev,
                              pictures: newFiles,
                            }));
                          }
                        }}
                        onClick={() =>
                          document
                            .getElementById('edit-property-images-input')
                            .click()
                        }
                      >
                        <div className="space-y-2">
                          <svg
                            className="mx-auto h-12 w-12 text-gray-400"
                            stroke="currentColor"
                            fill="none"
                            viewBox="0 0 48 48"
                          >
                            <path
                              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                              strokeWidth={2}
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                          <div className="text-sm text-gray-600">
                            <span className="font-medium text-yellow-600">
                              Click to upload
                            </span>{' '}
                            or drag and drop
                          </div>
                          <p className="text-xs text-gray-500">
                            PNG, JPG, GIF up to 5MB each (max 10 images)
                          </p>
                        </div>
                      </div>

                      {/* Hidden File Input */}
                      <input
                        id="edit-property-images-input"
                        type="file"
                        multiple
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => {
                          const files = Array.from(e.target.files);
                          const currentPictures = newProperty.pictures || [];
                          const newFiles = [
                            ...currentPictures,
                            ...files,
                          ].slice(0, 10); // Limit to 10 images
                          setNewProperty((prev) => ({
                            ...prev,
                            pictures: newFiles,
                          }));
                        }}
                      />

                      {/* Image Preview Grid */}
                      {newProperty.pictures &&
                        newProperty.pictures.length > 0 && (
                          <div className="mt-4">
                            <h5 className="text-sm font-medium text-gray-700 mb-2">
                              Uploaded Images ({newProperty.pictures.length}
                              /10)
                            </h5>
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                              {newProperty.pictures.map((file, index) => (
                                <div key={index} className="relative group">
                                  <img
                                    src={
                                      typeof file === 'string'
                                        ? file
                                        : URL.createObjectURL(file)
                                    }
                                    alt={`Property image ${index + 1}`}
                                    className="w-full h-20 object-cover rounded-lg border border-gray-200"
                                  />
                                  {/* Remove Button */}
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const newPictures =
                                        newProperty.pictures.filter(
                                          (_, i) => i !== index
                                        );
                                      setNewProperty((prev) => ({
                                        ...prev,
                                        pictures: newPictures,
                                      }));
                                    }}
                                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 transition-colors opacity-0 group-hover:opacity-100"
                                  >
                                    ×
                                  </button>
                                  {/* Main Image Badge */}
                                  {index === 0 && (
                                    <div className="absolute bottom-1 left-1 bg-yellow-500 text-white text-xs px-2 py-1 rounded">
                                      Main
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                            <p className="text-xs text-gray-500 mt-2">
                              First image will be used as the main property
                              photo. Drag to reorder.
                            </p>
                          </div>
                        )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Video Links
                        </label>
                        <input
                          type="url"
                          name="videoLinks"
                          value={newProperty.videoLinks || ''}
                          onChange={handleInputChange}
                          placeholder="https://youtube.com/watch?v=..."
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          YouTube, Vimeo, or other video platform links
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Floor Plan
                        </label>
                        <input
                          type="file"
                          name="floorPlan"
                          accept="image/*,.pdf"
                          onChange={(e) => {
                            const file = e.target.files[0];
                            setNewProperty((prev) => ({
                              ...prev,
                              floorPlan: file,
                            }));
                          }}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-yellow-500 focus:border-yellow-500"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Upload floor plan (Image or PDF)
                        </p>
                      </div>
                    </div>

                    {/* Special Features Checkboxes */}
                    <div className="mt-4">
                      <h5 className="text-sm font-medium text-gray-700 mb-3">
                        Special Features
                      </h5>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            name="zeroDeposit"
                            checked={newProperty.zeroDeposit || false}
                            onChange={(e) => {
                              setNewProperty((prev) => ({
                                ...prev,
                                zeroDeposit: e.target.checked,
                              }));
                            }}
                            className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
                          />
                          <label className="ml-2 block text-sm text-gray-900">
                            Zero Deposit
                            <span className="block text-xs text-gray-500">
                              No security deposit required
                            </span>
                          </label>
                        </div>

                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            name="cookingReady"
                            checked={newProperty.cookingReady || false}
                            onChange={(e) => {
                              setNewProperty((prev) => ({
                                ...prev,
                                cookingReady: e.target.checked,
                              }));
                            }}
                            className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
                          />
                          <label className="ml-2 block text-sm text-gray-900">
                            Cooking Ready
                            <span className="block text-xs text-gray-500">
                              Fully equipped kitchen with appliances
                            </span>
                          </label>
                        </div>

                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            name="hotProperty"
                            checked={newProperty.hotProperty || false}
                            onChange={(e) => {
                              setNewProperty((prev) => ({
                                ...prev,
                                hotProperty: e.target.checked,
                              }));
                            }}
                            className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
                          />
                          <label className="ml-2 block text-sm text-gray-900">
                            Hot Property
                            <span className="block text-xs text-gray-500">
                              High demand, premium location
                            </span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Amenities Section */}
                  <div className="border-t pt-4 mt-4">
                    <h4 className="text-md font-medium text-gray-900 mb-4">
                      Amenities
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                      {[
                        'Swimming Pool',
                        'Gym',
                        'Security',
                        'Parking',
                        'Playground',
                        'BBQ Area',
                        'Laundry',
                        'Concierge',
                        'Private Lift',
                        'Cooking Allowed',
                        'Air Conditioning',
                        'Balcony',
                        'Water Heater',
                        'Internet',
                      ].map((amenity) => (
                        <div key={amenity} className="flex items-center">
                          <input
                            type="checkbox"
                            id={`edit-amenity-${amenity}`}
                            checked={
                              newProperty.amenities?.includes(amenity) || false
                            }
                            onChange={(e) => {
                              const isChecked = e.target.checked;
                              setNewProperty((prev) => ({
                                ...prev,
                                amenities: isChecked
                                  ? [...(prev.amenities || []), amenity]
                                  : (prev.amenities || []).filter(
                                    (a) => a !== amenity
                                  ),
                              }));
                            }}
                            className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
                          />
                          <label
                            htmlFor={`edit-amenity-${amenity}`}
                            className="ml-2 text-sm text-gray-700"
                          >
                            {amenity}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowEditPropertyModal(false)}
                      className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-yellow-400 hover:bg-yellow-500"
                    >
                      Update Property
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Application Details Modal */}
        {/* This is the NEW modal code */}
        {/* Enhanced Application Details Modal */}
        {showApplicationDetails && selectedApplication && (
          <ApplicationDetailsModal
            application={selectedApplication}
            onClose={handleCloseApplicationDetails}
            onApprove={(applicationId) => {
              handleApplicationResponse(applicationId, 'approved');
              handleCloseApplicationDetails();
            }}
            onReject={(applicationId) => {
              handleApplicationResponse(applicationId, 'rejected');
              handleCloseApplicationDetails();
            }}
          />
        )}

        {showRescheduleModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-md w-full shadow-2xl">
              <div id="rescheduleModal" className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Propose New Time</h2>
                  <button id="closeButton" onClick={() => setShowRescheduleModal(false)} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
                </div>
                <form onSubmit={handleRescheduleSubmit} className="space-y-4">
                  <div>
                    <label htmlFor="newDate" className="block text-sm font-medium text-gray-700 mb-1">New Proposed Date</label>
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
                    <label htmlFor="newTime" className="block text-sm font-medium text-gray-700 mb-1">New Proposed Time</label>
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
                    <button id="submitButton" type="submit" className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">Send Proposal</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Recurring Availability Manager Modal */}
        {showAvailabilityModal && selectedPropertyForAvailability && (
          <RecurringAvailabilityManager
            propertyId={selectedPropertyForAvailability.id}
            onClose={handleCloseAvailabilityModal}
            onSuccess={handleAvailabilitySuccess}
          />
        )}
      </div>
    </div>
  );
};

export default LandlordDashboard;
