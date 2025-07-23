from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Import db from user model to ensure single instance
from .user import db

from .booking import Booking

class Property(db.Model):
    __tablename__ = 'properties'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic property information
    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    area = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    sqft = db.Column(db.Integer, nullable=True)
    bedrooms = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Integer, nullable=True)
    parking = db.Column(db.Integer, nullable=True)
    
    # Property details
    property_type = db.Column(db.String(50), nullable=False, default='Apartment')
    furnished = db.Column(db.String(50), nullable=False, default='Unfurnished')
    description = db.Column(db.Text, nullable=True)
    
    # Property status and metrics
    status = db.Column(db.String(50), nullable=False, default='Active')
    views = db.Column(db.Integer, nullable=False, default=0)
    inquiries = db.Column(db.Integer, nullable=False, default=0)
    
    # Location coordinates
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Move-in information
    move_in = db.Column(db.String(100), nullable=True, default='Move-in Now')
    
    # Media fields (stored as JSON strings)
    images = db.Column(db.Text, nullable=True)  # JSON array of image URLs
    gallery_images = db.Column(db.Text, nullable=True)  # JSON array of gallery image URLs
    main_image = db.Column(db.String(500), nullable=True)  # Main image URL
    image = db.Column(db.String(500), nullable=True)  # Primary image URL
    video_url = db.Column(db.String(500), nullable=True)  # Video URL
    video_links = db.Column(db.Text, nullable=True)  # Additional video links
    floor_plan = db.Column(db.String(500), nullable=True)  # Floor plan URL
    
    # Special features
    zero_deposit = db.Column(db.Boolean, nullable=False, default=False)
    cooking_ready = db.Column(db.Boolean, nullable=False, default=False)
    hot_property = db.Column(db.Boolean, nullable=False, default=False)
    
    # Amenities and tags (stored as JSON strings)
    amenities = db.Column(db.Text, nullable=True)  # JSON array of amenities
    tags = db.Column(db.Text, nullable=True)  # JSON array of tags
    
    # Ownership and timestamps
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to User
    landlord_id = db.Column(db.String(100), nullable=True)  # Legacy field for backward compatibility
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='property', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Property {self.title}>'
    
    def to_dict(self):
        """Convert property to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'location': self.location,
            'area': self.area,
            'price': self.price,
            'sqft': self.sqft,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'parking': self.parking,
            'propertyType': self.property_type,
            'furnished': self.furnished,
            'description': self.description,
            'status': self.status,
            'views': self.views,
            'inquiries': self.inquiries,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'moveIn': self.move_in,
            'images': json.loads(self.images) if self.images else [],
            'gallery_images': json.loads(self.gallery_images) if self.gallery_images else [],
            'main_image': self.main_image,
            'image': self.image,
            'video_url': self.video_url,
            'videoLinks': self.video_links,
            'floor_plan': self.floor_plan,
            'floorPlan': self.floor_plan,
            'zeroDeposit': self.zero_deposit,
            'cookingReady': self.cooking_ready,
            'hotProperty': self.hot_property,
            'amenities': json.loads(self.amenities) if self.amenities else [],
            'tags': json.loads(self.tags) if self.tags else [],
            'owner_id': self.owner_id,
            'landlordId': self.landlord_id,
            'dateAdded': self.date_added.isoformat() if self.date_added else None,
            'dateUpdated': self.date_updated.isoformat() if self.date_updated else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create property from dictionary data"""
        property_obj = cls()
        
        # Basic fields
        property_obj.title = data.get('title', '')
        property_obj.location = data.get('location', '')
        property_obj.area = data.get('area')
        property_obj.price = int(data.get('price', 0))
        property_obj.sqft = int(data.get('sqft', 0)) if data.get('sqft') else None
        property_obj.bedrooms = int(data.get('bedrooms', 0)) if data.get('bedrooms') else None
        property_obj.bathrooms = int(data.get('bathrooms', 0)) if data.get('bathrooms') else None
        property_obj.parking = int(data.get('parking', 0)) if data.get('parking') else None
        
        # Property details
        property_obj.property_type = data.get('propertyType', 'Apartment')
        property_obj.furnished = data.get('furnished', 'Unfurnished')
        property_obj.description = data.get('description', '')
        
        # Status and metrics
        property_obj.status = data.get('status', 'Active')
        property_obj.views = int(data.get('views', 0))
        property_obj.inquiries = int(data.get('inquiries', 0))
        
        # Location
        property_obj.latitude = float(data.get('latitude', 0)) if data.get('latitude') else None
        property_obj.longitude = float(data.get('longitude', 0)) if data.get('longitude') else None
        property_obj.move_in = data.get('moveIn', 'Move-in Now')
        
        # Media fields
        property_obj.images = json.dumps(data.get('images', [])) if data.get('images') else None
        property_obj.gallery_images = json.dumps(data.get('gallery_images', [])) if data.get('gallery_images') else None
        property_obj.main_image = data.get('main_image')
        property_obj.image = data.get('image')
        property_obj.video_url = data.get('video_url')
        property_obj.video_links = data.get('videoLinks')
        property_obj.floor_plan = data.get('floor_plan') or data.get('floorPlan')
        
        # Special features
        property_obj.zero_deposit = bool(data.get('zeroDeposit', False))
        property_obj.cooking_ready = bool(data.get('cookingReady', False))
        property_obj.hot_property = bool(data.get('hotProperty', False))
        
        # Amenities and tags
        property_obj.amenities = json.dumps(data.get('amenities', [])) if data.get('amenities') else None
        property_obj.tags = json.dumps(data.get('tags', [])) if data.get('tags') else None
        
        # Ownership
        property_obj.owner_id = data.get('owner_id')  # Set the owner_id from the data
        property_obj.landlord_id = data.get('landlordId', 'current_user')
        
        return property_obj
    
    def update_from_dict(self, data):
        """Update property from dictionary data"""
        # Basic fields
        if 'title' in data:
            self.title = data['title']
        if 'location' in data:
            self.location = data['location']
        if 'area' in data:
            self.area = data['area']
        if 'price' in data:
            self.price = int(data['price'])
        if 'sqft' in data:
            self.sqft = int(data['sqft']) if data['sqft'] else None
        if 'bedrooms' in data:
            self.bedrooms = int(data['bedrooms']) if data['bedrooms'] else None
        if 'bathrooms' in data:
            self.bathrooms = int(data['bathrooms']) if data['bathrooms'] else None
        if 'parking' in data:
            self.parking = int(data['parking']) if data['parking'] else None
        
        # Property details
        if 'propertyType' in data:
            self.property_type = data['propertyType']
        if 'furnished' in data:
            self.furnished = data['furnished']
        if 'description' in data:
            self.description = data['description']
        
        # Status and metrics
        if 'status' in data:
            self.status = data['status']
        if 'views' in data:
            self.views = int(data['views'])
        if 'inquiries' in data:
            self.inquiries = int(data['inquiries'])
        
        # Location
        if 'latitude' in data:
            self.latitude = float(data['latitude']) if data['latitude'] else None
        if 'longitude' in data:
            self.longitude = float(data['longitude']) if data['longitude'] else None
        if 'moveIn' in data:
            self.move_in = data['moveIn']
        
        # Media fields
        if 'images' in data:
            self.images = json.dumps(data['images']) if data['images'] else None
        if 'gallery_images' in data:
            self.gallery_images = json.dumps(data['gallery_images']) if data['gallery_images'] else None
        if 'main_image' in data:
            self.main_image = data['main_image']
        if 'image' in data:
            self.image = data['image']
        if 'video_url' in data:
            self.video_url = data['video_url']
        if 'videoLinks' in data:
            self.video_links = data['videoLinks']
        if 'floor_plan' in data or 'floorPlan' in data:
            self.floor_plan = data.get('floor_plan') or data.get('floorPlan')
        
        # Special features
        if 'zeroDeposit' in data:
            self.zero_deposit = bool(data['zeroDeposit'])
        if 'cookingReady' in data:
            self.cooking_ready = bool(data['cookingReady'])
        if 'hotProperty' in data:
            self.hot_property = bool(data['hotProperty'])
        
        # Amenities and tags
        if 'amenities' in data:
            self.amenities = json.dumps(data['amenities']) if data['amenities'] else None
        if 'tags' in data:
            self.tags = json.dumps(data['tags']) if data['tags'] else None
        
        # Update timestamp
        self.date_updated = datetime.utcnow()



