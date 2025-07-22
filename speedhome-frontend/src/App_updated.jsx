import React, { useState, useEffect, useRef } from 'react';
import { Routes, Route, useLocation, Link, useParams } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import AboutUs from './pages/AboutUs';
import FAQ from './pages/FAQ';
import TermsConditions from './pages/TermsConditions';
import PrivacyPolicy from './pages/PrivacyPolicy';
import ContactUs from './pages/ContactUs';
import UserDashboard from './pages/UserDashboard';
import LandlordDashboard from './pages/LandlordDashboard';
import BookingAPI from './services/BookingAPI';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ApplicationAPI from './services/ApplicationAPI';
import NotificationAPI from './services/NotificationAPI';
import Lightbox from "yet-another-react-lightbox";
import "yet-another-react-lightbox/styles.css";
import TenantBookingCalendar from './components/TenantBookingCalendar';

const PropertyDetailPage = ({ properties, isFavorite, toggleFavorite, setSelectedProperty, onApplyClick, onScheduleClick }) => {
  const { propertyId } = useParams();
  
  const [property, setProperty] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasApplied, setHasApplied] = useState(false);
  const [hasScheduledViewing, setHasScheduledViewing] = useState(false);
  const [mainImage, setMainImage] = useState(null);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  
  const { isTenant, user } = useAuth();

  useEffect(() => {
    if (property) {
      const initialImage = property.gallery_images?.[0] || property.image || null;
      setMainImage(initialImage);
    }
  }, [property]);

  useEffect(() => {
    const fetchPropertyAndStatus = async () => {
      if (!propertyId) return;
      setIsLoading(true);
      setHasApplied(false); 
      setHasScheduledViewing(false);

      try {
        const propResponse = await fetch(`http://localhost:5001/api/properties/${propertyId}?_t=${new Date().getTime()}`);
        
        if (propResponse.ok) {
          const propData = await propResponse.json();
          setProperty(propData.property);

          if (user && isTenant()) {
            const appStatus = await ApplicationAPI.hasApplied(propertyId);
            if (appStatus.success) setHasApplied(appStatus.has_applied);

            const bookingStatus = await BookingAPI.hasScheduled(propertyId);
            if (bookingStatus.success) setHasScheduledViewing(bookingStatus.has_scheduled);
          }
        } else {
          setProperty(null);
        }
      } catch (error) {
        console.error("Failed to fetch property details:", error);
        setProperty(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPropertyAndStatus();
  }, [propertyId, user]);

  useEffect(() => {
    if (property) {
      setSelectedProperty(property);
    }
  }, [property, setSelectedProperty]);

  const slides = property?.gallery_images?.map(src => ({ src })) || [];

  if (isLoading) {
    return <div className="text-center py-12 text-xl">Loading property...</div>;
  }

  if (!property) {
    return (
      <div className="text-center py-12 text-xl">
        Property not found. <Link to="/" className="text-yellow-500 hover:underline">Go back home</Link>
      </div>
    );
  }

  const isScheduleButtonDisabled = !isTenant() || hasScheduledViewing;
  const scheduleButtonText = hasScheduledViewing ? "✓ Viewing Requested" : "Schedule Viewing";
  
  return (
    <div className="bg-gray-100 min-h-screen">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <Link to="/" className="text-yellow-500 hover:text-yellow-600 mb-6 inline-block">
          ← Back to Properties
        </Link>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-white rounded-xl overflow-hidden shadow-lg">
              <div className="relative">
                <img 
                  src={mainImage || property.image || 'https://placehold.co/800x400/e2e8f0/4a5568?text=Property'} 
                  alt={property.title} 
                  className="w-full h-96 object-cover cursor-pointer"
                  onClick={() => setLightboxOpen(true)}
                />
                <button 
                  onClick={() => toggleFavorite(property.id)} 
                  className={`absolute top-4 right-4 p-2 rounded-full ${isFavorite(property.id) ? 'bg-red-500 text-white' : 'bg-white text-gray-600'} hover:scale-110 transition-transform`}
                >
                  ❤️
                </button>
              </div>
              
              {property.gallery_images && property.gallery_images.length > 1 && (
                <div className="p-4 border-t">
                  <div className="flex gap-2 overflow-x-auto">
                    {property.gallery_images.map((img, index) => (
                      <img 
                        key={index}
                        src={img} 
                        alt={`${property.title} ${index + 1}`}
                        className={`w-20 h-20 object-cover rounded-lg cursor-pointer flex-shrink-0 ${mainImage === img ? 'ring-2 ring-yellow-500' : ''}`}
                        onClick={() => setMainImage(img)}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl p-6 shadow-lg">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">{property.title}</h1>
                  <p className="text-gray-600 flex items-center gap-1">
                    📍 {property.location}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-yellow-500">RM {property.price}</div>
                  <div className="text-gray-600">/month</div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-1">🛏️</div>
                  <div className="text-sm text-gray-600">Bedrooms</div>
                  <div className="font-semibold">{property.bedrooms}</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-1">🚿</div>
                  <div className="text-sm text-gray-600">Bathrooms</div>
                  <div className="font-semibold">{property.bathrooms}</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-1">📐</div>
                  <div className="text-sm text-gray-600">Size</div>
                  <div className="font-semibold">{property.size} sqft</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-1">🏠</div>
                  <div className="text-sm text-gray-600">Type</div>
                  <div className="font-semibold">{property.property_type}</div>
                </div>
              </div>

              <div className="mb-6">
                <h2 className="text-xl font-bold text-gray-900 mb-3">Description</h2>
                <p className="text-gray-700 leading-relaxed">{property.description}</p>
              </div>

              {property.amenities && property.amenities.length > 0 && (
                <div className="mb-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-3">Amenities</h2>
                  <div className="flex flex-wrap gap-2">
                    {property.amenities.map((amenity, index) => (
                      <span key={index} className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                        {amenity}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Location</h2>
              <div className="bg-gray-200 h-64 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <p className="text-gray-600 mb-2">📍 {property.location}</p>
                  <p className="text-sm text-gray-500">Interactive map coming soon</p>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Similar Properties</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {properties.filter(p => p.id !== property.id && p.location === property.location).slice(0, 3).map((similarProperty) => (
                  <Link key={similarProperty.id} to={`/property/${similarProperty.id}`} className="block">
                    <div className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                      <img src={similarProperty.image || 'https://placehold.co/400x300/e2e8f0/4a5568?text=Similar'} alt={similarProperty.title} className="w-full h-32 object-cover"/>
                      <div className="p-3">
                        <h3 className="font-semibold text-gray-900 text-sm mb-1">{similarProperty.title}</h3>
                        <p className="text-yellow-500 font-bold text-sm">RM {property.price}/month</p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="sticky top-[72px]">
              <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-lg">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Property</h3>
                <div className="space-y-3">
                  <button onClick={() => alert('Chat modal coming soon!')} className="w-full bg-yellow-500 text-white px-6 py-3 rounded-lg hover:bg-yellow-600 transition-colors font-semibold flex items-center justify-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    Contact Landlord
                  </button>
                  <button onClick={onScheduleClick} disabled={isScheduleButtonDisabled} className={`w-full text-white px-6 py-3 rounded-lg transition-colors font-semibold flex items-center justify-center gap-2 ${ isScheduleButtonDisabled ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600' }`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {scheduleButtonText}
                  </button>
                  <button onClick={() => alert('Video modal coming soon!')} className="w-full bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors font-semibold flex items-center justify-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Virtual Tour
                  </button>
                  {isTenant() && property.status === 'Active' && !hasApplied && (
                    <button onClick={onApplyClick} className="w-full bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors font-semibold flex items-center justify-center gap-2">
                      Apply Now
                    </button>
                  )}
                  {isTenant() && hasApplied && (
                    <div className="text-center p-3 bg-green-100 text-green-800 rounded-lg font-semibold">
                      ✓ You have applied
                    </div>
                  )}
                </div>
                <div className="mt-6 pt-4 border-t border-gray-200">
                   <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-yellow-500 rounded-full flex items-center justify-center text-white font-semibold">L</div>
                      <div>
                         <div className="font-semibold text-gray-900">Property Owner</div>
                         <div className="text-sm text-gray-600">Verified Landlord</div>
                      </div>
                   </div>
                   <div className="grid grid-cols-2 gap-2">
                      <button className="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors text-sm font-medium">Message</button>
                      <button className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors text-sm font-medium">Call</button>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Lightbox
        open={lightboxOpen}
        close={() => setLightboxOpen(false)}
        slides={slides}
      />
    </div>
  );
};

// Continue with the rest of the App component...
// For brevity, I'll include just the key parts that need to be updated

const App = () => {
  // ... existing state and functions ...
  
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

const AppContent = () => {
  // ... existing state and functions ...
  
  return (
    <div className="App">
      <Header 
        searchInput={searchInput}
        handleSearchChange={handleSearchChange}
        filters={filters}
        handleFilterChange={handleFilterChange}
        locations={locations}
        setShowMoreFiltersModal={setShowMoreFiltersModal}
        onAddProperty={() => setShowAddPropertyModal(true)}
      />

      <Routes>
        {/* ... existing routes ... */}
      </Routes>

      <Footer />

      {/* Apply Modal */}
      {showApplyModal && selectedProperty && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full shadow-2xl">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Apply for Property</h2>
                <button onClick={() => setShowApplyModal(false)} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
              </div>
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-900">{selectedProperty.title}</h3>
                <p className="text-sm text-gray-600">{selectedProperty.location}</p>
              </div>
              <form onSubmit={handleApplicationSubmit} className="space-y-4">
                <div>
                  <label htmlFor="applicationMessage" className="block text-sm font-medium text-gray-700 mb-2">Your Message to the Landlord</label>
                  <textarea id="applicationMessage" value={applicationMessage} onChange={(e) => setApplicationMessage(e.target.value)} rows={4} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Introduce yourself, mention who will be living with you, your occupation, etc." />
                </div>
                <div className="flex gap-3 pt-4">
                  <button type="button" onClick={() => setShowApplyModal(false)} className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">Cancel</button>
                  <button type="submit" className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-semibold">Submit Application</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Schedule Viewing Modal - Updated */}
      {showScheduleModal && selectedProperty && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-4xl w-full shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Schedule a Viewing</h2>
                <button onClick={() => setShowScheduleModal(false)} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
              </div>
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-900">{selectedProperty.title}</h3>
                <p className="text-sm text-gray-600">{selectedProperty.location}</p>
              </div>
              
              <TenantBookingCalendar 
                propertyId={selectedProperty.id}
                onBookingSuccess={() => {
                  setShowScheduleModal(false);
                  setDetailPageVersion(v => v + 1);
                }}
                onClose={() => setShowScheduleModal(false)}
              />
            </div>
          </div>
        </div>
      )}

      {/* ... rest of modals ... */}
    </div>
  );
};

export default App;

