import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoginModal from './LoginModal';
import RegisterModal from './RegisterModal';
import NotificationAPI from '../services/NotificationAPI';

const Header = ({ notifications, setNotifications }) => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const { user, isAuthenticated, logout, isLandlord, isTenant, getUserFullName } = useAuth();
  
  const [showAccountDropdown, setShowAccountDropdown] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);

  // --- NEW STATE FOR NOTIFICATIONS ---
  const [showNotificationDropdown, setShowNotificationDropdown] = useState(false);
  // This local state will hold the notifications to be displayed in the dropdown
  const [displayedNotifications, setDisplayedNotifications] = useState([]);

  // This effect closes dropdowns if the user clicks outside of them
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.dropdown-container')) {
        setShowAccountDropdown(false);
        setShowNotificationDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  // --- CORRECTED NOTIFICATION LOGIC ---
  const handleNotificationClick = async () => {
    // When opening the dropdown for the first time
    if (!showNotificationDropdown) {
      // If there are new, unread notifications from the server...
      if (notifications && notifications.length > 0) {
        // ...copy them to our local display state so they don't disappear.
        setDisplayedNotifications(notifications);
        
        const idsToMarkAsRead = notifications.map(n => n.id);
        try {
          // Tell the backend to mark them as read
          await NotificationAPI.markAsRead(idsToMarkAsRead);
          // Clear the main notifications array to remove the badge immediately
          setNotifications([]); 
        } catch (error) {
          console.error("Failed to mark notifications as read:", error);
        }
      } else {
        // If there are no new notifications, make sure the display is empty.
        setDisplayedNotifications([]);
      }
    }
    // Toggle the dropdown's visibility
    setShowNotificationDropdown(prev => !prev);
  };

  const handleNotificationItemClick = (link) => {
    setShowNotificationDropdown(false);
    if (link) {
        navigate(link);
    }
  };
  
  const handleLandlordClick = () => {
    if (isAuthenticated && isLandlord()) {
      navigate('/landlord');
    } else if (isAuthenticated && isTenant()) {
      alert('You need a landlord account to access the landlord dashboard. Please contact support to upgrade your account.');
    } else {
      setShowLoginModal(true);
    }
  };
  
  const handleTenantClick = () => {
    if (isAuthenticated && isTenant()) {
      navigate('/dashboard');
    } else if (isAuthenticated && isLandlord()) {
      alert('You are logged in as a landlord. Please use the Landlord dashboard or logout to access tenant features.');
    } else {
      setShowLoginModal(true);
    }
  };
  
  const handleAccountClick = () => {
    setShowAccountDropdown(!showAccountDropdown);
  };
  
  const handleLoginClick = () => {
    setShowLoginModal(true);
    setShowAccountDropdown(false);
  };
  
  const handleRegisterClick = () => {
    setShowRegisterModal(true);
    setShowAccountDropdown(false);
  };
  
  const handleDashboardClick = () => {
    if (isLandlord()) {
      navigate('/landlord');
    } else {
      navigate('/dashboard');
    }
    setShowAccountDropdown(false);
  };
  
  const handleLogoutClick = async () => {
    await logout();
    setShowAccountDropdown(false);
  };
  
  const handleAuthSuccess = async (userData) => {
    setShowLoginModal(false);
    setShowRegisterModal(false);
    setShowAccountDropdown(false);
    
    setTimeout(() => {
      if (userData.role === 'landlord') {
        navigate('/landlord');
      } else {
        navigate('/dashboard');
      }
    }, 100);
  };
  
  const switchToRegister = () => {
    setShowLoginModal(false);
    setShowRegisterModal(true);
  };
  
  const switchToLogin = () => {
    setShowRegisterModal(false);
    setShowLoginModal(true);
  };

  return (
    <header className="bg-white shadow-sm border-b sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-center h-auto sm:h-16 py-2 sm:py-0">
          <div className="flex items-center cursor-pointer mb-2 sm:mb-0">
            <Link to="/" className="flex items-center">
              <div className="w-6 h-6 sm:w-8 sm:h-8 bg-green-600 rounded-full flex items-center justify-center mr-1 sm:mr-2">
                <span className="text-white font-bold text-xs sm:text-sm">S</span>
              </div>
              <span className="text-lg sm:text-xl font-bold text-gray-900">SPEEDHOME</span>
            </Link>
          </div>
          <div className="flex flex-col sm:flex-row items-center w-full sm:w-auto">
            <div className="flex items-center space-x-2 sm:space-x-4 mb-2 sm:mb-0 w-full sm:w-auto justify-center">
              <button 
                onClick={handleLandlordClick} 
                className="bg-green-100 text-green-700 px-2 py-1 sm:px-4 sm:py-2 rounded-lg border border-green-300 text-xs sm:text-sm cursor-pointer hover:bg-green-200"
              >
                Landlord
              </button>
              <button 
                onClick={handleTenantClick} 
                className="bg-blue-600 text-white px-2 py-1 sm:px-4 sm:py-2 rounded-lg text-xs sm:text-sm cursor-pointer hover:bg-blue-700"
              >
                Tenant
              </button>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-2 w-full sm:w-auto">
              {location.pathname === '/' && (
                <input
                  type="text"
                  placeholder="Search by area/property name"
                  className="px-2 py-1 sm:px-4 sm:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full sm:w-64 text-sm sm:text-base"
                />
              )}
              {isAuthenticated && (
                <div className="relative dropdown-container">
                  <button onClick={handleNotificationClick} className="p-2 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-100 relative">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
                    {notifications && notifications.length > 0 && (
                      <span className="absolute top-1 right-1 block h-3 w-3 rounded-full bg-red-500 ring-2 ring-white text-white flex items-center justify-center text-xs">
                        {notifications.length}
                      </span>
                    )}
                  </button>
                  {showNotificationDropdown && (
                    <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg border z-50">
                      <div className="p-3 font-bold text-gray-800 border-b">Notifications</div>
                      <div className="max-h-96 overflow-y-auto">
                        {displayedNotifications.length > 0 ? (
                          displayedNotifications.map(notification => (
                            <div 
                              key={notification.id} 
                              onClick={() => handleNotificationItemClick(notification.link)}
                              className="p-3 border-b hover:bg-gray-50 cursor-pointer"
                            >
                              <p className="text-sm text-gray-700">{notification.message}</p>
                              <p className="text-xs text-gray-400 mt-1">{new Date(notification.created_at).toLocaleString()}</p>
                            </div>
                          ))
                        ) : (
                          <p className="p-4 text-sm text-gray-500">You have no new notifications.</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
              <div className="relative dropdown-container">
                <button 
                  onClick={handleAccountClick}
                  className="p-1 sm:p-2 text-gray-600 hover:text-gray-900 cursor-pointer"
                >
                  👤
                </button>
                {showAccountDropdown && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                    {isAuthenticated ? (
                      <>
                        <div className="px-4 py-2 text-sm text-gray-500 border-b">
                          Welcome, {getUserFullName()}
                        </div>
                        <button 
                          onClick={handleDashboardClick}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          My Dashboard
                        </button>
                        <button 
                          onClick={handleLogoutClick}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Logout
                        </button>
                      </>
                    ) : (
                      <>
                        <button 
                          onClick={handleLoginClick}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Login
                        </button>
                        <button 
                          onClick={handleRegisterClick}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Sign Up
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
              <div className="relative group">
                <button className="p-1 sm:p-2 text-gray-600 hover:text-gray-900 cursor-pointer">
                  🌐
                </button>
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 hidden group-hover:block">
                  <Link to="/about-us" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">About Us</Link>
                  <Link to="/faq" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">FAQ</Link>
                  <Link to="/contact-us" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Contact Us</Link>
                  <Link to="/terms-conditions" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Terms & Conditions</Link>
                  <Link to="/privacy-policy" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Privacy Policy</Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {showLoginModal && (
        <LoginModal
          isOpen={showLoginModal}
          onClose={() => setShowLoginModal(false)}
          onSuccess={handleAuthSuccess}
          onSwitchToRegister={switchToRegister}
        />
      )}
      
      {showRegisterModal && (
        <RegisterModal
          isOpen={showRegisterModal}
          onClose={() => setShowRegisterModal(false)}
          onSuccess={handleAuthSuccess}
          onSwitchToLogin={switchToLogin}
        />
      )}
    </header>
  );
};

export default Header;
