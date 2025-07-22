from flask import Blueprint, request, jsonify, session
from src.models.property import db, Property
from src.models.viewing_slot import ViewingSlot
from datetime import datetime, date, time, timedelta
import json

property_bp = Blueprint('property', __name__)

@property_bp.route('/properties', methods=['GET'])
def get_properties():
    """Get all properties with optional filtering"""
    try:
        # Get query parameters for filtering
        location = request.args.get('location')
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        bedrooms = request.args.get('bedrooms', type=int)
        property_type = request.args.get('property_type')
        amenities = request.args.get('amenities')  # Comma-separated list
        
        # Start with base query - only show Active properties for public listing
        query = Property.query.filter(Property.status == 'Active')
        
        # Apply filters
        if location:
            query = query.filter(Property.location.ilike(f'%{location}%'))
        
        if min_price is not None:
            query = query.filter(Property.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Property.price <= max_price)
        
        if bedrooms is not None:
            query = query.filter(Property.bedrooms == bedrooms)
        
        if property_type:
            query = query.filter(Property.property_type == property_type)
        
        if amenities:
            amenity_list = [a.strip() for a in amenities.split(',')]
            for amenity in amenity_list:
                query = query.filter(Property.amenities.like(f'%{amenity}%'))
        
        # Execute query and get results
        properties = query.order_by(Property.date_added.desc()).all()
        
        # Convert to dictionary format
        properties_data = [prop.to_dict() for prop in properties]
        
        return jsonify({
            'success': True,
            'properties': properties_data,
            'count': len(properties_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@property_bp.route('/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    """Get a specific property by ID"""
    try:
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({
                'success': False,
                'error': 'Property not found'
            }), 404
        
        # Increment view count
        property_obj.views += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'property': property_obj.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@property_bp.route('/properties/owner/<int:owner_id>', methods=['GET'])
def get_properties_by_owner(owner_id):
    """Get all properties owned by a specific user"""
    try:
        # Query properties by owner_id
        properties = Property.query.filter_by(owner_id=owner_id).order_by(Property.date_added.desc()).all()
        
        # Convert to dictionary format
        properties_data = [prop.to_dict() for prop in properties]
        
        return jsonify({
            'success': True,
            'properties': properties_data,
            'count': len(properties_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@property_bp.route('/properties', methods=['POST'])
def create_property():
    """Create a new property"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Validate required fields
        required_fields = ['title', 'location', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Set the owner_id from the authenticated user
        data['owner_id'] = session['user_id']
        
        # Create new property from data
        property_obj = Property.from_dict(data)
        
        # Add to database
        db.session.add(property_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'property': property_obj.to_dict(),
            'message': 'Property created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@property_bp.route('/properties/<int:property_id>', methods=['PUT'])
def update_property(property_id):
    """Update an existing property"""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({
                'success': False,
                'error': 'Property not found'
            }), 404
        
        # Check if user owns this property
        if property_obj.owner_id != session['user_id']:
            return jsonify({
                'success': False,
                'error': 'Access denied. You can only edit your own properties.'
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update property with new data
        property_obj.update_from_dict(data)
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'property': property_obj.to_dict(),
            'message': 'Property updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@property_bp.route('/properties/<int:property_id>', methods=['DELETE'])
def delete_property(property_id):
    """Delete a property"""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({
                'success': False,
                'error': 'Property not found'
            }), 404
        
        # Check if user owns this property
        if property_obj.owner_id != session['user_id']:
            return jsonify({
                'success': False,
                'error': 'Access denied. You can only delete your own properties.'
            }), 403
        
        # Delete property
        db.session.delete(property_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Property deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@property_bp.route('/properties/<int:property_id>/inquire', methods=['POST'])
def inquire_property(property_id):
    """Increment inquiry count for a property"""
    try:
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({
                'success': False,
                'error': 'Property not found'
            }), 404
        
        # Increment inquiry count
        property_obj.inquiries += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'property': property_obj.to_dict(),
            'message': 'Inquiry recorded successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@property_bp.route('/properties/search', methods=['GET'])
def search_properties():
    """Advanced search for properties"""
    try:
        # Get search parameters
        query_text = request.args.get('q', '')
        location = request.args.get('location', '')
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        bedrooms = request.args.get('bedrooms', type=int)
        bathrooms = request.args.get('bathrooms', type=int)
        property_type = request.args.get('property_type', '')
        furnished = request.args.get('furnished', '')
        amenities = request.args.get('amenities', '')
        zero_deposit = request.args.get('zero_deposit', type=bool)
        cooking_ready = request.args.get('cooking_ready', type=bool)
        hot_property = request.args.get('hot_property', type=bool)
        
        # Start with base query - only show Active properties for public search
        query = Property.query.filter(Property.status == 'Active')
        
        # Text search in title and description
        if query_text:
            query = query.filter(
                db.or_(
                    Property.title.ilike(f'%{query_text}%'),
                    Property.description.ilike(f'%{query_text}%'),
                    Property.location.ilike(f'%{query_text}%')
                )
            )
        
        # Location filter
        if location:
            query = query.filter(Property.location.ilike(f'%{location}%'))
        
        # Price range filter
        if min_price is not None:
            query = query.filter(Property.price >= min_price)
        if max_price is not None:
            query = query.filter(Property.price <= max_price)
        
        # Room filters
        if bedrooms is not None:
            query = query.filter(Property.bedrooms == bedrooms)
        if bathrooms is not None:
            query = query.filter(Property.bathrooms == bathrooms)
        
        # Property type filter
        if property_type:
            query = query.filter(Property.property_type == property_type)
        
        # Furnished filter
        if furnished:
            query = query.filter(Property.furnished == furnished)
        
        # Special features filters
        if zero_deposit is not None:
            query = query.filter(Property.zero_deposit == zero_deposit)
        if cooking_ready is not None:
            query = query.filter(Property.cooking_ready == cooking_ready)
        if hot_property is not None:
            query = query.filter(Property.hot_property == hot_property)
        
        # Amenities filter
        if amenities:
            amenity_list = [a.strip() for a in amenities.split(',')]
            for amenity in amenity_list:
                query = query.filter(Property.amenities.like(f'%{amenity}%'))
        
        # Execute query
        properties = query.order_by(Property.date_added.desc()).all()
        
        # Convert to dictionary format
        properties_data = [prop.to_dict() for prop in properties]
        
        return jsonify({
            'success': True,
            'properties': properties_data,
            'count': len(properties_data),
            'search_params': {
                'query': query_text,
                'location': location,
                'min_price': min_price,
                'max_price': max_price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'property_type': property_type,
                'furnished': furnished,
                'amenities': amenities,
                'zero_deposit': zero_deposit,
                'cooking_ready': cooking_ready,
                'hot_property': hot_property
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@property_bp.route('/properties/stats', methods=['GET'])
def get_property_stats():
    """Get property statistics"""
    try:
        total_properties = Property.query.count()
        active_properties = Property.query.filter_by(status='Active').count()
        total_views = db.session.query(db.func.sum(Property.views)).scalar() or 0
        total_inquiries = db.session.query(db.func.sum(Property.inquiries)).scalar() or 0
        
        # Property type distribution
        property_types = db.session.query(
            Property.property_type,
            db.func.count(Property.id)
        ).group_by(Property.property_type).all()
        
        # Price range distribution
        price_ranges = {
            'under_1000': Property.query.filter(Property.price < 1000).count(),
            '1000_2000': Property.query.filter(Property.price.between(1000, 2000)).count(),
            '2000_3000': Property.query.filter(Property.price.between(2000, 3000)).count(),
            'over_3000': Property.query.filter(Property.price > 3000).count()
        }
        
        return jsonify({
            'success': True,
            'stats': {
                'total_properties': total_properties,
                'active_properties': active_properties,
                'total_views': total_views,
                'total_inquiries': total_inquiries,
                'property_types': dict(property_types),
                'price_ranges': price_ranges
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@property_bp.route('/properties/favorites', methods=['GET'])
def get_properties_for_favorites():
    """Get properties for tenant favorites - includes Active and Rented properties"""
    try:
        # Get query parameters for filtering
        location = request.args.get('location')
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        bedrooms = request.args.get('bedrooms', type=int)
        property_type = request.args.get('property_type')
        amenities = request.args.get('amenities')  # Comma-separated list
        
        # Start with base query - show Active and Rented properties (exclude only Inactive)
        query = Property.query.filter(Property.status.in_(['Active', 'Rented']))
        
        # Apply filters
        if location:
            query = query.filter(Property.location.ilike(f'%{location}%'))
        
        if min_price is not None:
            query = query.filter(Property.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Property.price <= max_price)
        
        if bedrooms is not None:
            query = query.filter(Property.bedrooms == bedrooms)
        
        if property_type:
            query = query.filter(Property.property_type == property_type)
        
        if amenities:
            amenity_list = [a.strip() for a in amenities.split(',')]
            for amenity in amenity_list:
                query = query.filter(Property.amenities.like(f'%{amenity}%'))
        
        # Execute query and get results
        properties = query.order_by(Property.date_added.desc()).all()
        
        # Convert to dictionary format
        properties_data = [prop.to_dict() for prop in properties]
        
        return jsonify({
            'success': True,
            'properties': properties_data,
            'count': len(properties_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@property_bp.route('/properties/<int:property_id>/recurring-availability', methods=['POST'])
def add_recurring_availability(property_id):
    """Add recurring availability for a property"""
    try:
        # Debug session information
        print(f"Session data: {dict(session)}")
        print(f"User ID in session: {session.get('user_id')}")
        
        # Check if user is logged in
        if 'user_id' not in session:
            print("Authentication failed: No user_id in session")
            return jsonify({
                'success': False,
                'error': 'Authentication required. Please log in first.'
            }), 401
        
        # Get the property and verify ownership
        property_obj = Property.query.get(property_id)
        if not property_obj:
            return jsonify({
                'success': False,
                'error': 'Property not found'
            }), 404
        
        # Verify the user owns this property
        if property_obj.owner_id != session['user_id']:
            return jsonify({
                'success': False,
                'error': 'You can only set availability for your own properties'
            }), 403
        
        # Get the request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['start_date', 'end_date', 'schedule']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Parse dates
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid date format: {str(e)}'
            }), 400
        
        # Validate date range
        if end_date <= start_date:
            return jsonify({
                'success': False,
                'error': 'End date must be after start date'
            }), 400
        
        # Validate schedule data
        schedule = data['schedule']
        if not isinstance(schedule, dict) or not schedule:
            return jsonify({
                'success': False,
                'error': 'Schedule must be a non-empty object'
            }), 400
        
        # Day name to weekday number mapping
        day_mapping = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6
        }
        
        slots_created = 0
        
        # Iterate through each date in the range
        current_date = start_date
        while current_date <= end_date:
            # Get the day of the week
            weekday = current_date.weekday()
            
            # Check if this day is in the schedule
            for day_name, day_config in schedule.items():
                if day_name.lower() in day_mapping and day_mapping[day_name.lower()] == weekday:
                    # Parse the time range
                    try:
                        from_time = datetime.strptime(day_config['from'], '%H:%M').time()
                        to_time = datetime.strptime(day_config['to'], '%H:%M').time()
                    except (ValueError, KeyError) as e:
                        return jsonify({
                            'success': False,
                            'error': f'Invalid time format for {day_name}: {str(e)}'
                        }), 400
                    
                    # Validate time range
                    if to_time <= from_time:
                        return jsonify({
                            'success': False,
                            'error': f'End time must be after start time for {day_name}'
                        }), 400
                    
                    # Create 30-minute slots for this day
                    current_time = from_time
                    while current_time < to_time:
                        # Calculate end time for this slot (30 minutes later)
                        end_slot_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=30)).time()
                        
                        # Don't create slot if it would exceed the day's end time
                        if end_slot_time > to_time:
                            break
                        
                        # Check if this slot already exists
                        existing_slot = ViewingSlot.query.filter_by(
                            property_id=property_id,
                            date=current_date,
                            start_time=current_time,
                            end_time=end_slot_time
                        ).first()
                        
                        # Only create if it doesn't exist
                        if not existing_slot:
                            new_slot = ViewingSlot(
                                property_id=property_id,
                                date=current_date,
                                start_time=current_time,
                                end_time=end_slot_time,
                                is_available=True
                            )
                            db.session.add(new_slot)
                            slots_created += 1
                        
                        # Move to next 30-minute slot
                        current_time = end_slot_time
            
            # Move to next date
            current_date += timedelta(days=1)
        
        # Commit all the new slots
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully created {slots_created} viewing slots',
            'slots_created': slots_created,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

