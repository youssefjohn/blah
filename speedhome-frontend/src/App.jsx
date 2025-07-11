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
          ← Back to Search Results
        </Link>
        
        <div className="bg-white shadow-xl rounded-lg">
          
          {/* --- IMAGE GALLERY (Full width block) --- */}
          {/* FIX: Removed rounding and overflow from the grid container itself. */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-1">
            <div className="md:col-span-2 relative group aspect-video max-h-[450px]">
              <img 
                src={mainImage || 'https://placehold.co/800x600/e2e8f0/cccccc?text=Property+Image'} 
                alt={property.title}
                // FIX: Added 'rounded-tl-lg' to round the top-left corner of the main image.
                className="w-full h-full object-cover cursor-pointer rounded-tl-lg"
                onClick={() => setLightboxOpen(true)}
              />
              <div className="absolute top-4 right-4 z-10">
                <button 
                  onClick={(e) => toggleFavorite(property.id, e)} 
                  className={`p-2 rounded-full transition-colors ${
                    isFavorite(property.id) ? 'bg-red-500 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="hidden md:grid col-span-1 grid-rows-2 gap-1">
              {(property.gallery_images && property.gallery_images.length > 2) ? (
                property.gallery_images.slice(1, 3).map((img, index) => (
                  <div key={index} className="relative group cursor-pointer" onClick={() => { setMainImage(img); setLightboxOpen(true); }}>
                    {/* FIX: Conditionally adding 'rounded-tr-lg' to the first thumbnail image. */}
                    <img src={img} alt={`${property.title} thumbnail ${index + 1}`} className={`w-full h-full object-cover ${index === 0 ? 'rounded-tr-lg' : ''}`}/>
                    <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-all flex items-center justify-center">
                       {index === 1 && property.gallery_images.length > 3 && (<span className="text-white text-3xl font-bold">+{property.gallery_images.length - 3}</span>)}
                    </div>
                  </div>
                ))
              ) : (
                Array(2).fill(0).map((_, index) => (
                  // FIX: Conditionally adding 'rounded-tr-lg' to the placeholder div.
                  <div key={index} className={`bg-gray-200 w-full h-full ${index === 0 ? 'rounded-tr-lg' : ''}`}></div>
                ))
              )}
            </div>
          </div>

          {/* --- TWO-COLUMN LAYOUT (Starts below the gallery) --- */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 p-6">
            
            <div className="lg:col-span-2 space-y-8">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{property.title}</h1>
                <p className="text-lg text-gray-600 mb-2">{property.location}</p>
                <p className="text-3xl font-bold text-yellow-500 mb-4">RM {property.price}/month</p>
              </div>
              
              {(property.zeroDeposit || property.cookingReady || property.hotProperty) && (
                <div className="flex flex-wrap gap-2">
                  {property.zeroDeposit && <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">💰 Zero Deposit</span>}
                  {property.cookingReady && <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">🍳 Cooking Ready</span>}
                  {property.hotProperty && <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">🔥 Hot Property</span>}
                </div>
              )}
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg"><div className="text-2xl font-bold text-gray-900">{property.bedrooms}</div><div className="text-sm text-gray-600">Bedrooms</div></div>
                <div className="text-center p-4 bg-gray-50 rounded-lg"><div className="text-2xl font-bold text-gray-900">{property.bathrooms}</div><div className="text-sm text-gray-600">Bathrooms</div></div>
                <div className="text-center p-4 bg-gray-50 rounded-lg"><div className="text-2xl font-bold text-gray-900">{property.sqft}</div><div className="text-sm text-gray-600">Sq Ft</div></div>
                <div className="text-center p-4 bg-gray-50 rounded-lg"><div className="text-2xl font-bold text-gray-900">{property.parking}</div><div className="text-sm text-gray-600">Parking</div></div>
              </div>
            
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Description</h2>
                <p className="text-gray-600 leading-relaxed mb-6">
                  {property.description || "This beautiful property offers modern living with excellent amenities and convenient location. Perfect for families or professionals looking for a comfortable home."}
                </p>
                <h3 className="text-xl font-bold text-gray-900 mb-3">Property Features</h3>
                <div className="grid grid-cols-2 gap-2 mb-6">
                  <div className="flex items-center"><span className="text-green-500 mr-2">✓</span><span className="text-gray-600">{property.furnished || 'Fully Furnished'}</span></div>
                  <div className="flex items-center"><span className="text-green-500 mr-2">✓</span><span className="text-gray-600">{property.propertyType || 'Condominium'}</span></div>
                  <div className="flex items-center"><span className="text-green-500 mr-2">✓</span><span className="text-gray-600">Move-in: {property.moveIn || 'Immediate'}</span></div>
                  <div className="flex items-center"><span className="text-green-500 mr-2">✓</span><span className="text-gray-600">Built-up: {property.sqft} sq ft</span></div>
                </div>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Amenities</h2>
                <div className="grid grid-cols-2 gap-3">
                  {(property.amenities || ['Swimming Pool', 'Gym', 'Security', 'Parking', 'Playground', 'BBQ Area']).map((amenity, index) => (
                    <div key={index} className="flex items-center">
                      <span className="text-yellow-500 mr-2">★</span>
                      <span className="text-gray-600">{amenity}</span>
                    </div>
                  ))}
                </div>
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
                    <button onClick={() => alert('Chat modal coming soon!')} className="w-full bg-yellow-500 text-white px-6 py-3 rounded-lg hover:bg-yellow-600 transition-colors font-semibold flex items-center justify-center gap-2"><svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>Contact Landlord</button>
                    <button onClick={onScheduleClick} disabled={isScheduleButtonDisabled} className={`w-full text-white px-6 py-3 rounded-lg transition-colors font-semibold flex items-center justify-center gap-2 ${ isScheduleButtonDisabled ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600' }`}><svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>{scheduleButtonText}</button>
                    <button onClick={() => alert('Video modal coming soon!')} className="w-full bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors font-semibold flex items-center justify-center gap-2"><svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>Virtual Tour</button>
                    {isTenant() && property.status === 'Active' && !hasApplied && (<button onClick={onApplyClick} className="w-full bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors font-semibold flex items-center justify-center gap-2">Apply Now</button>)}
                    {isTenant() && hasApplied && (<div className="text-center p-3 bg-green-100 text-green-800 rounded-lg font-semibold">✓ You have applied</div>)}
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
      </div>
      <Lightbox
        open={lightboxOpen}
        close={() => setLightboxOpen(false)}
        slides={slides}
      />
    </div>
  );
};

const HomePage = ({
    searchInput,
    handleSearchChange,
    filters,
    handleFilterChange,
    locations,
    setShowMoreFiltersModal,
    filteredProperties,
    viewMode,
    setViewMode,
    isFavorite,
    toggleFavorite
}) => (
    <div className="bg-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">Find Your Perfect Rental</h1>
          <p className="mt-2 text-lg text-gray-600">Search thousands of properties across Malaysia</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 mb-8">
            <div className="flex flex-col sm:flex-row gap-2">
                <div className="flex-grow">
                    <input
                        type="text"
                        placeholder="Search by property name or location..."
                        value={searchInput}
                        onChange={(e) => handleSearchChange(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    />
                </div>
                <div className="flex items-center gap-2">
                    <select value={filters.price} onChange={(e) => handleFilterChange('price', e.target.value)} className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500">
                        <option value="all">Any Price</option>
                        <option value="under1000">Under RM 1,000</option>
                        <option value="1000-2000">RM 1,000 - RM 2,000</option>
                        <option value="2000-3000">RM 2,000 - RM 3,000</option>
                        <option value="3000-5000">RM 3,000 - RM 5,000</option>
                        <option value="above5000">Above RM 5,000</option>
                    </select>
                    <select value={filters.type} onChange={(e) => handleFilterChange('type', e.target.value)} className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500">
                        <option value="all">Any Type</option>
                        <option value="condominium">Condominium</option>
                        <option value="apartment">Apartment</option>
                        <option value="house">House</option>
                    </select>
                    <button onClick={() => setShowMoreFiltersModal(true)} className="px-4 py-2 border border-gray-300 rounded-lg flex items-center gap-2 hover:bg-gray-50">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 16v-2m8-6h2m-18 0H4m14.485-6.515l1.414-1.414M5.101 5.101L6.515 6.515m10.97 10.97l1.414 1.414M5.101 18.899l1.414-1.414M12 18a6 6 0 100-12 6 6 0 000 12z" /></svg>
                        More Filters
                    </button>
                </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-center flex-wrap gap-x-6 gap-y-2">
                    {locations.map(location => (
                        <button
                        key={location.name}
                        onClick={() => handleFilterChange('location', location.name)}
                        className={`text-gray-600 hover:text-yellow-600 transition-colors pb-1 ${
                            filters.location === location.name
                            ? 'font-bold text-yellow-600 border-b-2 border-yellow-600'
                            : 'font-medium'
                        }`}
                        >
                        {location.short || location.name}
                        </button>
                    ))}
                </div>
            </div>
        </div>

        <div className="flex justify-between items-center mb-4">
            <div className="text-sm text-gray-600">{filteredProperties.length} properties found</div>
            <div className="flex border border-gray-300 rounded-lg overflow-hidden">
              <button onClick={() => setViewMode('grid')} className={`px-4 py-2 text-sm ${viewMode === 'grid' ? 'bg-yellow-500 text-white' : 'bg-white text-gray-700'}`}>Grid</button>
              <button onClick={() => setViewMode('list')} className={`px-4 py-2 text-sm ${viewMode === 'list' ? 'bg-yellow-500 text-white' : 'bg-white text-gray-700'}`}>List</button>
            </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProperties.map((property) => (
            <Link key={property.id} to={`/property/${property.id}`} className="block">
              <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="relative">
                  <img src={property.image || 'https://placehold.co/600x400/e2e8f0/4a5568?text=Property'} alt={property.title} className="w-full h-48 object-cover"/>
                  <button onClick={(e) => toggleFavorite(property.id, e)} className={`absolute top-2 right-2 p-2 rounded-full ${isFavorite(property.id) ? 'bg-red-500 text-white' : 'bg-white text-gray-600'} hover:bg-red-500 hover:text-white transition-colors`}>
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" /></svg>
                  </button>
                </div>
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{property.title}</h3>
                  <p className="text-gray-600 mb-2">{property.location}</p>
                  <p className="text-2xl font-bold text-yellow-500 mb-2">RM {property.price}</p>
                  {(property.zeroDeposit || property.cookingReady || property.hotProperty) && (
                    <div className="flex gap-1 mb-2">
                      {property.zeroDeposit && (<span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">💰 Zero Deposit</span>)}
                      {property.cookingReady && (<span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">🍳 Cooking Ready</span>)}
                      {property.hotProperty && (<span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">🔥 Hot Property</span>)}
                    </div>
                  )}
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>{property.bedrooms} bed</span>
                    <span>{property.bathrooms} bath</span>
                    <span>{property.sqft} sqft</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {filteredProperties.length === 0 && (
          <div className="text-center py-12">
            <h3 className="mt-2 text-sm font-medium text-gray-900">No properties found</h3>
            <p className="mt-1 text-sm text-gray-500">Try adjusting your search criteria.</p>
          </div>
        )}
      </div>
    </div>
);

const TenantPage = () => (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Tenant Services</h1>
        <p className="text-gray-600">Tenant services page coming soon...</p>
      </div>
    </div>
);


function AppContent() {
  const [properties, setProperties] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [favorites, setFavorites] = useState([]);
  const [viewMode, setViewMode] = useState('grid');
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [applicationMessage, setApplicationMessage] = useState('');
  const [showImageLightbox, setShowImageLightbox] = useState(false);
  const [showChatModal, setShowChatModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showVideoModal, setShowVideoModal] = useState(false);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [showAddPropertyModal, setShowAddPropertyModal] = useState(false);
  const [detailPageVersion, setDetailPageVersion] = useState(0);

  const { user, isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);

  const initialFilters = {
    location: 'All Locations',
    price: 'all',
    type: 'all',
    furnishing: 'all',
    amenities: [],
    bedrooms: 0,
    bathrooms: 0,
    parking: 0,
    zeroDeposit: false,
    petFriendly: false,
    availableFrom: '',
  };
  const [filters, setFilters] = useState(initialFilters);
  const [showMoreFiltersModal, setShowMoreFiltersModal] = useState(false);

  const initialScheduleData = {
    name: '',
    email: '',
    phone: '',
    date: '',
    time: '',
    message: '',
    numberOfOccupants: 1,
    occupation: '',
    moveInDate: '',
    nationality: '',
    monthlyIncome: '',
  };
  const [scheduleData, setScheduleData] = useState(initialScheduleData);

  useEffect(() => {
    if (user) {
      setScheduleData(prev => ({
        ...prev,
        name: user.full_name || user.username || '',
        email: user.email || '',
      }));
    }
  }, [user, showScheduleModal]);

  useEffect(() => {
    if (!isAuthenticated) {
      setNotifications([]);
      return;
    }

    const fetchNotifications = async () => {
      const result = await NotificationAPI.getNotifications();
      if (result.success) {
        setNotifications(result.notifications);
      }
    };

    fetchNotifications();
    const intervalId = setInterval(fetchNotifications, 20000);
    return () => clearInterval(intervalId);
  }, [isAuthenticated, user]);


  const [rescheduleData, setRescheduleData] = useState({
    bookingId: null,
    currentDate: '',
    currentTime: '',
    newDate: '',
    newTime: ''
  });
  
  const [newPropertyData, setNewPropertyData] = useState({
    name: '',
    location: '',
    price: '',
    type: '',
    furnishing: '',
    bedrooms: '',
    bathrooms: '',
    size: '',
    description: '',
    amenities: []
  });
  
  const handleApplicationSubmit = async (e) => {
      e.preventDefault(); 
      if (!selectedProperty) return alert('An error occurred. No property selected.');
  
      try {
        const result = await ApplicationAPI.createApplication({
          propertyId: selectedProperty.id,
          message: applicationMessage,
        });
  
        if (result.success) {
          alert('Your application has been submitted successfully!');
          setShowApplyModal(false);
          setApplicationMessage('');
          setDetailPageVersion(v => v + 1);
        } else {
          alert(`Error: ${result.error}`);
        }
      } catch (error) {
        console.error('Failed to submit application:', error);
        alert('An unexpected error occurred. Please try again.');
      }
    };

  const handleScheduleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedProperty) return alert('An error occurred. No property selected.');
    if (!scheduleData.date || !scheduleData.time) return alert('Please select a date and time.');

    try {
        const bookingDetails = {
            property_id: selectedProperty.id,
            name: scheduleData.name,
            email: scheduleData.email,
            phone: scheduleData.phone,
            appointment_date: scheduleData.date,
            appointment_time: scheduleData.time,
            message: scheduleData.message,
            occupation: scheduleData.occupation,
            monthly_income: scheduleData.monthlyIncome,
            number_of_occupants: scheduleData.numberOfOccupants
        };

        const result = await BookingAPI.createBooking(bookingDetails);

        if (result.success) {
            alert('Your viewing request has been sent to the landlord!');
            setShowScheduleModal(false);
            setScheduleData(initialScheduleData);
            setDetailPageVersion(v => v + 1);
        } else {
            alert(`Error: ${result.error || 'Could not submit viewing request.'}`);
        }
    } catch (error) {
        console.error('Failed to submit viewing request:', error);
        alert('An unexpected server error occurred. Please try again later.');
    }
  };

  const handleScheduleChange = (field, value) => {
    setScheduleData(prev => ({ ...prev, [field]: value }));
  };

  const allAmenities = [
    'Swimming Pool', 'Gym', 'Security', 'Parking', 'Playground', 
    'BBQ Area', 'Laundry', 'Concierge', 'Private Lift', 'Cooking Allowed',
    'Air Conditioning', 'Balcony', 'Water Heater', 'Internet'
  ];

  const locations = [
    { name: 'All Locations', short: 'All' },
    { name: 'Kuala Lumpur', short: 'KL' },
    { name: 'Petaling Jaya', short: 'PJ' },
    { name: 'Cyberjaya' },
    { name: 'Puchong' },
    { name: 'Cheras' },
    { name: 'Bangsar' },
    { name: 'Kajang' },
    { name: 'Shah Alam' },
    { name: 'Subang Jaya' },
    { name: 'Ara Damansara' },
    { name: 'Kepong' },
    { name: 'Sentul' },
  ];

  useEffect(() => {
    const loadProperties = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/properties');
        if (response.ok) {
          const data = await response.json();
          setProperties(data.properties || []);
        } else {
          console.error('Failed to load properties from API');
          setProperties([]);
        }
      } catch (error) {
        console.error('Error loading properties:', error);
        setProperties([]);
      }
    };

    loadProperties();

    const handlePropertyUpdate = () => {
      loadProperties();
    };

    window.addEventListener('propertyUpdated', handlePropertyUpdate);

    const storedFavorites = localStorage.getItem('speedhomeFavorites');
    if (storedFavorites) {
      setFavorites(JSON.parse(storedFavorites));
    }

    return () => {
      window.removeEventListener('propertyUpdated', handlePropertyUpdate);
    };
  }, []);

  useEffect(() => {
    localStorage.setItem('speedhomeFavorites', JSON.stringify(favorites));
  }, [favorites]);

  const toggleFavorite = (propertyId, e) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    
    setFavorites(prev => {
      const newFavorites = prev.includes(propertyId) 
        ? prev.filter(id => id !== propertyId)
        : [...prev, propertyId];
      
      localStorage.setItem('speedhomeFavorites', JSON.stringify(newFavorites));
      return newFavorites;
    });
  };

  const isFavorite = (propertyId) => favorites.includes(propertyId);

  const filteredProperties = properties.filter(property => {
    const matchesSearch = property.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         property.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = filters.location === 'All Locations' || property.location === filters.location;
    
    let matchesPrice = true;
    if (filters.price !== 'all') {
      const price = property.price;
      switch (filters.price) {
        case 'under1000': matchesPrice = price < 1000; break;
        case '1000-2000': matchesPrice = price >= 1000 && price <= 2000; break;
        case '2000-3000': matchesPrice = price >= 2000 && price <= 3000; break;
        case '3000-5000': matchesPrice = price >= 3000 && price <= 5000; break;
        case 'above5000': matchesPrice = price > 5000; break;
        default: matchesPrice = true;
      }
    }
    
    const matchesFurnish = filters.furnishing === 'all' || 
                          (property.furnished && property.furnished.toLowerCase().includes(filters.furnishing.toLowerCase()));
    const matchesType = filters.type === 'all' || 
                       (property.propertyType && property.propertyType.toLowerCase().includes(filters.type.toLowerCase()));
    const matchesAmenities = filters.amenities.length === 0 || 
                            filters.amenities.every(amenity => 
                              property.amenities && property.amenities.includes(amenity));

    const matchesZeroDeposit = !filters.zeroDeposit || property.zeroDeposit === true;
    const matchesPetFriendly = !filters.petFriendly || property.petFriendly === true;
    const matchesBedrooms = filters.bedrooms === 0 || property.bedrooms >= filters.bedrooms;
    const matchesBathrooms = filters.bathrooms === 0 || property.bathrooms >= filters.bathrooms;
    const matchesParking = filters.parking === 0 || property.parking >= filters.parking;

    const matchesAvailability = (() => {
        if (!filters.availableFrom) return true;
        if (!property.moveIn || property.moveIn.toLowerCase() === 'immediate') return true;
        
        const availableDate = new Date(property.moveIn);
        const filterDate = new Date(filters.availableFrom);
        
        if (isNaN(availableDate.getTime()) || isNaN(filterDate.getTime())) {
            return true;
        }
        
        return availableDate >= filterDate;
    })();

    return matchesSearch && matchesLocation && matchesPrice && matchesFurnish && matchesType && matchesAmenities && matchesZeroDeposit && matchesPetFriendly && matchesAvailability && matchesBedrooms && matchesBathrooms && matchesParking;
  });

  const clearAllFilters = () => {
    setSearchTerm('');
    setSearchInput('');
    setFilters(initialFilters);
    setShowMoreFiltersModal(false);
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
  };

  const handleAmenityToggle = (amenity) => {
    setFilters(prev => {
        const newAmenities = prev.amenities.includes(amenity)
            ? prev.amenities.filter(a => a !== amenity)
            : [...prev.amenities, amenity];
        return { ...prev, amenities: newAmenities };
    });
  };

  const handleAddPropertySubmit = (e) => {
    e.preventDefault();
    // ... (rest of add property logic)
  };

  const handleNewPropertyAmenityToggle = (amenity) => {
    setNewPropertyData(prev => ({
      ...prev,
      amenities: prev.amenities.includes(amenity) 
        ? prev.filter(a => a !== amenity)
        : [...prev.amenities, amenity]
    }));
  };

  const handleRescheduleRequest = (bookingId, currentDate, currentTime) => {
    setRescheduleData({ bookingId, currentDate, currentTime, newDate: '', newTime: '' });
    setShowRescheduleModal(true);
  };

  useEffect(() => {
    window.appHandleRescheduleRequest = handleRescheduleRequest;
    return () => { delete window.appHandleRescheduleRequest; };
  }, []);

  const handleSearchChange = (value) => {
    const searchValue = typeof value === 'string' ? value : value.target.value;
    setSearchInput(searchValue);
    const timer = setTimeout(() => {
        setSearchTerm(searchValue);
    }, 300);
    return () => clearTimeout(timer);
  };

  return (
    <div className="App">
      <Header notifications={notifications} setNotifications={setNotifications} />
      <Routes>
        <Route path="/" element={
            <HomePage
                searchInput={searchInput}
                handleSearchChange={handleSearchChange}
                filters={filters}
                handleFilterChange={handleFilterChange}
                locations={locations}
                setShowMoreFiltersModal={setShowMoreFiltersModal}
                filteredProperties={filteredProperties}
                viewMode={viewMode}
                setViewMode={setViewMode}
                isFavorite={isFavorite}
                toggleFavorite={toggleFavorite}
            />
        } />
        <Route path="/property/:propertyId" element={<PropertyDetailPage key={detailPageVersion} properties={properties} isFavorite={isFavorite} toggleFavorite={toggleFavorite} setSelectedProperty={setSelectedProperty} onApplyClick={() => setShowApplyModal(true)} onScheduleClick={() => setShowScheduleModal(true)} />} />
        <Route path="/landlord" element={<LandlordDashboard onAddProperty={() => setShowAddPropertyModal(true)} />} />
        <Route path="/tenant" element={<TenantPage />} />
        <Route path="/about-us" element={<AboutUs />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/terms-conditions" element={<TermsConditions />} />
        <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        <Route path="/contact-us" element={<ContactUs />} />
        <Route path="/dashboard" element={<UserDashboard favorites={favorites} properties={properties} toggleFavorite={toggleFavorite} />} />
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

      {/* Schedule Viewing Modal */}
      {showScheduleModal && selectedProperty && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl max-w-lg w-full shadow-2xl">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Schedule a Viewing</h2>
                <button onClick={() => setShowScheduleModal(false)} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
              </div>
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-900">{selectedProperty.title}</h3>
                <p className="text-sm text-gray-600">{selectedProperty.location}</p>
              </div>
              <form onSubmit={handleScheduleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="schedule-name" className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                    <input type="text" id="schedule-name" value={scheduleData.name} onChange={(e) => handleScheduleChange('name', e.target.value)} required className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                  <div>
                    <label htmlFor="schedule-email" className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                    <input type="email" id="schedule-email" value={scheduleData.email} onChange={(e) => handleScheduleChange('email', e.target.value)} required className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                   <div>
                    <label htmlFor="schedule-phone" className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                    <input type="tel" id="schedule-phone" value={scheduleData.phone} onChange={(e) => handleScheduleChange('phone', e.target.value)} required className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                  <div>
                    <label htmlFor="schedule-nationality" className="block text-sm font-medium text-gray-700 mb-1">Nationality</label>
                    <input type="text" id="schedule-nationality" value={scheduleData.nationality} onChange={(e) => handleScheduleChange('nationality', e.target.value)} required className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                  <div>
                    <label htmlFor="schedule-occupation" className="block text-sm font-medium text-gray-700 mb-1">Occupation</label>
                    <input type="text" id="schedule-occupation" value={scheduleData.occupation} onChange={(e) => handleScheduleChange('occupation', e.target.value)} required className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                  <div>
                    <label htmlFor="schedule-income" className="block text-sm font-medium text-gray-700 mb-1">Gross Monthly Income (RM)</label>
                    <input type="number" id="schedule-income" value={scheduleData.monthlyIncome} onChange={(e) => handleScheduleChange('monthlyIncome', e.target.value)} required min="0" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                  <div>
                    <label htmlFor="schedule-occupants" className="block text-sm font-medium text-gray-700 mb-1">Number of Occupants</label>
                    <input type="number" id="schedule-occupants" value={scheduleData.numberOfOccupants} onChange={(e) => handleScheduleChange('numberOfOccupants', e.target.value)} required min="1" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                  <div>
                    <label htmlFor="schedule-move-in" className="block text-sm font-medium text-gray-700 mb-1">Preferred Move-in Date</label>
                    <input type="date" id="schedule-move-in" value={scheduleData.moveInDate} onChange={(e) => handleScheduleChange('moveInDate', e.target.value)} required className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                   <div>
                    <label htmlFor="schedule-date" className="block text-sm font-medium text-gray-700 mb-1">Preferred Viewing Date</label>
                    <input type="date" id="schedule-date" value={scheduleData.date} onChange={(e) => handleScheduleChange('date', e.target.value)} required className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                  <div>
                    <label htmlFor="schedule-time" className="block text-sm font-medium text-gray-700 mb-1">Preferred Viewing Time</label>
                    <input type="time" id="schedule-time" value={scheduleData.time} onChange={(e) => handleScheduleChange('time', e.target.value)} required className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                </div>
                <div>
                  <label htmlFor="schedule-message" className="block text-sm font-medium text-gray-700 mb-1">Message (Optional)</label>
                  <textarea id="schedule-message" value={scheduleData.message} onChange={(e) => handleScheduleChange('message', e.target.value)} rows="3" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Any specific questions or requests?"></textarea>
                </div>
                <div className="flex gap-3 pt-4">
                  <button type="button" onClick={() => setShowScheduleModal(false)} className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">Cancel</button>
                  <button type="submit" className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">Submit Request</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* More Filters Modal */}
      {showMoreFiltersModal && (
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl">
                <div className="p-6 border-b flex justify-between items-center">
                    <h2 className="text-2xl font-bold text-gray-900">All Filters</h2>
                    <button onClick={() => setShowMoreFiltersModal(false)} className="text-gray-400 hover:text-gray-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>
                <div className="p-6 space-y-6 overflow-y-auto">
                        {/* Bedrooms */}
                        <div>
                            <h3 className="font-semibold mb-2">Number of Bedrooms</h3>
                            <div className="flex gap-2">
                                {[0, 1, 2, 3, 4].map(num => (
                                    <button key={num} onClick={() => handleFilterChange('bedrooms', num)} className={`px-4 py-2 rounded-full border ${filters.bedrooms === num ? 'bg-yellow-500 text-white border-yellow-500' : 'bg-white hover:border-gray-400'}`}>
                                        {num === 0 ? 'Any' : `${num}+`}
                                    </button>
                                ))}
                            </div>
                        </div>
                        {/* Bathrooms */}
                        <div>
                            <h3 className="font-semibold mb-2">Number of Bathrooms</h3>
                            <div className="flex gap-2">
                                {[0, 1, 2, 3, 4].map(num => (
                                    <button key={num} onClick={() => handleFilterChange('bathrooms', num)} className={`px-4 py-2 rounded-full border ${filters.bathrooms === num ? 'bg-yellow-500 text-white border-yellow-500' : 'bg-white hover:border-gray-400'}`}>
                                        {num === 0 ? 'Any' : `${num}+`}
                                    </button>
                                ))}
                            </div>
                        </div>
                        {/* Parking */}
                        <div>
                            <h3 className="font-semibold mb-2">Number of Car Parks</h3>
                            <div className="flex gap-2">
                                {[0, 1, 2, 3].map(num => (
                                    <button key={num} onClick={() => handleFilterChange('parking', num)} className={`px-4 py-2 rounded-full border ${filters.parking === num ? 'bg-yellow-500 text-white border-yellow-500' : 'bg-white hover:border-gray-400'}`}>
                                        {num === 0 ? 'Any' : `${num}+`}
                                    </button>
                                ))}
                            </div>
                        </div>
                        {/* Extra Info */}
                        <div>
                            <h3 className="font-semibold mb-2">Extra Information</h3>
                            <div className="flex gap-2">
                                <button onClick={() => handleFilterChange('zeroDeposit', !filters.zeroDeposit)} className={`px-4 py-2 rounded-full border ${filters.zeroDeposit ? 'bg-yellow-500 text-white border-yellow-500' : 'bg-white hover:border-gray-400'}`}>Zero Deposit</button>
                                <button onClick={() => handleFilterChange('petFriendly', !filters.petFriendly)} className={`px-4 py-2 rounded-full border ${filters.petFriendly ? 'bg-yellow-500 text-white border-yellow-500' : 'bg-white hover:border-gray-400'}`}>Pet-Friendly</button>
                            </div>
                        </div>
                         {/* Amenities */}
                        <div>
                            <h3 className="font-semibold mb-2">Amenities</h3>
                            <div className="flex flex-wrap gap-2">
                                {allAmenities.map(amenity => (
                                    <button key={amenity} onClick={() => handleAmenityToggle(amenity)} className={`px-4 py-2 rounded-full border text-sm ${filters.amenities.includes(amenity) ? 'bg-yellow-500 text-white border-yellow-500' : 'bg-white hover:border-gray-400'}`}>
                                        {amenity}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                    <div className="p-6 border-t mt-auto flex justify-between items-center bg-gray-50 rounded-b-xl">
                    <button onClick={clearAllFilters} className="text-gray-600 hover:text-black font-semibold">Reset Filter</button>
                    <button onClick={() => setShowMoreFiltersModal(false)} className="px-6 py-3 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 font-semibold">
                        Filter ({filteredProperties.length})
                    </button>
                    </div>
                </div>
            </div>
        )}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App