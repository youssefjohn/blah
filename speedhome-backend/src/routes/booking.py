from flask import Blueprint, request, jsonify, session
from datetime import datetime, date, time


from sqlalchemy.orm import joinedload

from ..models.viewing_slot import ViewingSlot
from ..models.booking import Booking
from ..models.property import Property
from ..models.user import User
from ..models.notification import Notification
from ..models.user import db



booking_bp = Blueprint('booking', __name__)

# In src/routes/booking.py

@booking_bp.route('/bookings', methods=['POST'])
def create_booking():
    """Create a new viewing request/booking"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        data = request.get_json()
        property_id = data.get('property_id')
        
        print(f"--- Received booking request for property_id: {property_id} ---")

        property_obj = Property.query.get(property_id)
        if not property_obj:
            print(f"--- ERROR: Property with id {property_id} not found. ---")
            return jsonify({'success': False, 'error': 'Property not found'}), 404

        # ... (rest of your validation and booking creation logic) ...
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()

        booking = Booking(
            user_id=session['user_id'],
            property_id=data['property_id'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            message=data.get('message', ''),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='pending',
            occupation=data.get('occupation'),
            monthly_income=data.get('monthly_income'),
            number_of_occupants=data.get('number_of_occupants'),
            is_seen_by_landlord=False
        )
        
        db.session.add(booking)
        
        # Create a notification for the landlord
        landlord_notification = Notification(
            recipient_id=property_obj.owner_id,
            message=f"New viewing request for '{property_obj.title}' from {data.get('name')}.",
            link="/landlord"
        )
        db.session.add(landlord_notification)
        
        print(f"--- Notification created for recipient_id: {landlord_notification.recipient_id} ---")

        db.session.commit()
        
        print("--- Booking and Notification committed successfully. ---")
        
        return jsonify({
            'success': True,
            'message': 'Viewing request created successfully',
            'booking': booking.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"---!!! AN ERROR OCCURRED: {str(e)} !!!---")
        return jsonify({'success': False, 'error': str(e)}), 500

# --- NEW ROUTE FOR TENANT CANCELLATION ---
@booking_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking_by_tenant(booking_id):
    """Allows a tenant to cancel their own booking."""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        # Security check: Ensure the person cancelling is the person who made the booking.
        if booking.user_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        # Prevent cancelling already completed or cancelled bookings
        if booking.status in ['completed', 'cancelled']:
            return jsonify({'success': False, 'error': f'Booking is already {booking.status}'}), 400

        booking.status = 'cancelled'
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Booking cancelled successfully',
            'booking': booking.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@booking_bp.route('/bookings/user/<int:user_id>', methods=['GET'])
def get_bookings_by_user(user_id):
    """Get all bookings for a specific user, including property details."""
    try:
        # Check if user is authenticated and authorized
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        if session['user_id'] != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # This new query is more efficient. 
        # It uses a JOIN to get the booking and its related property in one go.
        bookings = Booking.query.options(
            joinedload(Booking.property)
        ).filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
        
        booking_list = []
        for booking in bookings:
            booking_dict = booking.to_dict()
            
            # Since we used a join, the property data is already loaded.
            if booking.property:
                # Add the property title and ID directly to the booking object
                # This matches what your frontend code is expecting.
                booking_dict['propertyTitle'] = booking.property.title
                booking_dict['property_id'] = booking.property.id

            booking_list.append(booking_dict)
        
        return jsonify({
            'success': True,
            'bookings': booking_list,
            'count': len(booking_list)
        })
        
    except Exception as e:
        # It's helpful to log the actual error on the server for debugging
        print(f"Error in get_bookings_by_user: {e}") 
        return jsonify({'success': False, 'error': 'An internal error occurred'}), 500


@booking_bp.route('/bookings/landlord/<int:landlord_id>', methods=['GET'])
def get_bookings_by_landlord(landlord_id):
    """Get all bookings for properties owned by a specific landlord"""
    try:
        # Check if user is authenticated and authorized
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        if session['user_id'] != landlord_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Get all properties owned by the landlord
        properties = Property.query.filter_by(owner_id=landlord_id).all()
        property_ids = [prop.id for prop in properties]
        
        if not property_ids:
            return jsonify({
                'success': True,
                'bookings': [],
                'count': 0
            })
        
        # Get all bookings for these properties
        bookings = Booking.query.filter(Booking.property_id.in_(property_ids)).order_by(Booking.created_at.desc()).all()
        
        # Include property and tenant details in the response
        booking_list = []
        for booking in bookings:
            booking_dict = booking.to_dict()
            
            # Add property details
            property_obj = Property.query.get(booking.property_id)
            if property_obj:
                booking_dict['property'] = {
                    'id': property_obj.id,
                    'title': property_obj.title,
                    'location': property_obj.location,
                    'price': property_obj.price
                }
            
            # Add tenant details
            tenant = User.query.get(booking.user_id)
            if tenant:
                booking_dict['tenant'] = {
                    'id': tenant.id,
                    'username': tenant.username,
                    'email': tenant.email
                }
            
            booking_list.append(booking_dict)
        
        return jsonify({
            'success': True,
            'bookings': booking_list,
            'count': len(booking_list)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
def update_booking_status(booking_id):
    """Update the status of a booking (approve/decline)"""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['confirmed', 'cancelled', 'completed']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Verify the user is the property owner
        property_obj = Property.query.get(booking.property_id)
        if not property_obj or property_obj.owner_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        booking.status = new_status
        booking.updated_at = datetime.utcnow()

        tenant_notification = Notification(
            recipient_id=booking.user_id,
            message=f"Your viewing for '{property_obj.title}' has been {new_status}.",
            link="/dashboard"
        )
        db.session.add(tenant_notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Booking status updated to {new_status}',
            'booking': booking.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_bp.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get a specific booking by ID"""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Check if user is authorized (either the tenant or the property owner)
        property_obj = Property.query.get(booking.property_id)
        if (booking.user_id != session['user_id'] and 
            (not property_obj or property_obj.owner_id != session['user_id'])):
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        booking_dict = booking.to_dict()
        
        # Add property details
        if property_obj:
            booking_dict['property'] = {
                'id': property_obj.id,
                'title': property_obj.title,
                'location': property_obj.location,
                'price': property_obj.price
            }
        
        # Add tenant details if user is the landlord
        if property_obj and property_obj.owner_id == session['user_id']:
            tenant = User.query.get(booking.user_id)
            if tenant:
                booking_dict['tenant'] = {
                    'id': tenant.id,
                    'username': tenant.username,
                    'email': tenant.email
                }
        
        return jsonify({
            'success': True,
            'booking': booking_dict
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@booking_bp.route('/bookings/<int:booking_id>/reschedule', methods=['PUT'])
def reschedule_booking(booking_id):
    """Request to reschedule a booking"""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        data = request.get_json()
        new_date = data.get('date')
        new_time = data.get('time')
        requested_by = data.get('requested_by')  # 'tenant' or 'landlord'
        
        if not new_date or not new_time or not requested_by:
            return jsonify({'success': False, 'error': 'Date, time, and requested_by are required'}), 400
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Verify the user has permission to reschedule
        property_obj = Property.query.get(booking.property_id)
        user_id = session['user_id']
        
        # Check if user is either the tenant (booking owner) or landlord (property owner)
        if booking.user_id != user_id and property_obj.owner_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Parse the new date and time
        try:
            from datetime import datetime
            new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
            new_time_obj = datetime.strptime(new_time, '%H:%M').time()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date or time format'}), 400
        
        # Store original date/time if not already stored
        if not booking.original_date:
            booking.original_date = booking.appointment_date
            booking.original_time = booking.appointment_time
        
        # Update booking with reschedule information
        booking.proposed_date = new_date_obj
        booking.proposed_time = new_time_obj
        booking.reschedule_requested_by = requested_by
        booking.status = 'pending'  # Reset to pending for approval
        booking.updated_at = datetime.utcnow()

        # --- THIS IS THE MODIFIED LOGIC ---
        if requested_by == 'tenant':
            # Notify the LANDLORD about the tenant's request
            booking.is_seen_by_landlord = False
            tenant = User.query.get(booking.user_id)
            landlord_notification = Notification(
                recipient_id=property_obj.owner_id,
                message=f"{tenant.get_full_name()} requested to reschedule the viewing for '{property_obj.title}'.",
                link="/landlord"
            )
            db.session.add(landlord_notification)
        
        elif requested_by == 'landlord':
            # Notify the TENANT about the landlord's request
            tenant_notification = Notification(
                recipient_id=booking.user_id,
                message=f"The landlord has proposed a new viewing time for '{property_obj.title}'.",
                link="/dashboard" # Link to tenant dashboard
            )
            db.session.add(tenant_notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reschedule request submitted successfully',
            'booking': booking.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@booking_bp.route('/bookings/<int:booking_id>/decline-reschedule', methods=['POST'])
def decline_reschedule(booking_id):
    """Decline a reschedule request and revert to original date/time"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        property_obj = Property.query.get(booking.property_id)
        user_id = session['user_id']

        # --- THIS IS THE CORRECTED LOGIC ---
        # The user is authorized if they are EITHER the property owner (landlord)
        # OR the user who made the booking (tenant).
        if property_obj.owner_id != user_id and booking.user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        # Revert to original date/time if available
        if booking.original_date and booking.original_time:
            booking.appointment_date = booking.original_date
            booking.appointment_time = booking.original_time

        # Clear reschedule fields and set status back to confirmed
        booking.proposed_date = None
        booking.proposed_time = None
        booking.reschedule_requested_by = None
        booking.original_date = None
        booking.original_time = None
        booking.status = 'confirmed'
        booking.updated_at = datetime.utcnow()

        # Notify the other party that their request was declined
        # If the tenant declined, notify the landlord.
        if user_id == booking.user_id:
            recipient_id = property_obj.owner_id
            message = f"The tenant has declined your reschedule proposal for '{property_obj.title}'. The original appointment is still active."
        # If the landlord declined, notify the tenant.
        else:
            recipient_id = booking.user_id
            message = f"Your reschedule request for '{property_obj.title}' was declined. The original appointment is still active."

        notification = Notification(
            recipient_id=recipient_id,
            message=message,
            link="/dashboard"  # or /landlord depending on recipient
        )
        db.session.add(notification)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Reschedule request declined successfully',
            'booking': booking.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@booking_bp.route('/bookings/<int:booking_id>/approve-reschedule', methods=['PUT'])
def approve_reschedule(booking_id):
    """Approve a reschedule request"""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Verify the user has permission to approve
        property_obj = Property.query.get(booking.property_id)
        user_id = session['user_id']
        
        # Check if user is either the tenant (booking owner) or landlord (property owner)
        if booking.user_id != user_id and property_obj.owner_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Make sure there's a reschedule request to approve
        if not booking.proposed_date or not booking.proposed_time:
            return jsonify({'success': False, 'error': 'No reschedule request to approve'}), 400
        
        # Apply the proposed changes
        booking.appointment_date = booking.proposed_date
        booking.appointment_time = booking.proposed_time
        booking.status = 'confirmed'
        
        # Clear reschedule fields
        booking.proposed_date = None
        booking.proposed_time = None
        booking.reschedule_requested_by = None
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reschedule request approved successfully',
            'booking': booking.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@booking_bp.route('/bookings/<int:booking_id>/cancel-reschedule', methods=['POST'])
def cancel_reschedule(booking_id):
    """Cancel a reschedule request and revert to original date/time"""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Verify the user has permission to cancel the reschedule
        property_obj = Property.query.get(booking.property_id)
        user_id = session['user_id']
        
        # Check if user is either the tenant (booking owner) or landlord (property owner)
        if booking.user_id != user_id and property_obj.owner_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Verify there's an active reschedule request
        if not booking.reschedule_requested_by:
            return jsonify({'success': False, 'error': 'No active reschedule request to cancel'}), 400
        
        # Verify the user is the one who requested the reschedule
        if ((booking.reschedule_requested_by == 'tenant' and booking.user_id != user_id) or
            (booking.reschedule_requested_by == 'landlord' and property_obj.owner_id != user_id)):
            return jsonify({'success': False, 'error': 'Only the reschedule initiator can cancel the request'}), 403
        
        # Revert to original date/time if available, otherwise keep current
        if booking.original_date and booking.original_time:
            booking.appointment_date = booking.original_date
            booking.appointment_time = booking.original_time
        
        # Clear reschedule fields
        booking.proposed_date = None
        booking.proposed_time = None
        booking.reschedule_requested_by = None
        booking.original_date = None
        booking.original_time = None
        
        # Set status back to confirmed (assuming it was confirmed before reschedule)
        booking.status = 'confirmed'
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reschedule request cancelled successfully',
            'booking': booking.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    

@booking_bp.route('/bookings/has-scheduled/<int:property_id>', methods=['GET'])
def has_scheduled_for_property(property_id):
    """
    Checks if the currently logged-in user has an active or pending booking
    for a specific property.
    """
    # If no user is logged in, they definitely haven't scheduled a viewing.
    if 'user_id' not in session:
        return jsonify({'success': True, 'has_scheduled': False})

    user_id = session['user_id']
    print(f"--- Checking booking status for user_id: {user_id} and property_id: {property_id} ---")
    
    
    # Query for a booking that belongs to the current user and property,
    # and is NOT cancelled or declined. This covers both 'pending' and 'confirmed'.
    active_booking = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.property_id == property_id,
        Booking.status.notin_(['cancelled', 'declined'])
    ).first()

    # If a booking is found (it's not None), then has_scheduled is true.
    if active_booking:
        return jsonify({'success': True, 'has_scheduled': True})
    else:
        return jsonify({'success': True, 'has_scheduled': False})
    
@booking_bp.route('/bookings/<int:booking_id>/mark-as-seen', methods=['POST'])
def mark_booking_as_seen(booking_id):
    """Marks a specific booking as seen by the landlord."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'}), 404

    # Security check: ensure the user is the landlord for this property
    prop = Property.query.get(booking.property_id)
    if not prop or prop.owner_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    booking.is_seen_by_landlord = True
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Booking marked as seen.'})


@booking_bp.route('/bookings/create-from-slot', methods=['POST'])
def create_booking_from_slot():
    """Create a new booking by consuming a viewing slot."""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        slot_id = data.get('viewing_slot_id')
        property_id = data.get('property_id')

        if not slot_id or not property_id:
            return jsonify({'success': False, 'error': 'slot_id and property_id are required'}), 400

        # Find the slot and verify it's available
        slot = ViewingSlot.query.get(slot_id)
        if not slot or not slot.is_available:
            return jsonify({'success': False, 'error': 'Viewing slot not found or already booked'}), 404

        # Mark the slot as booked and link it to the property
        slot.is_available = False
        slot.booked_by_user_id = session['user_id']
        slot.booked_for_property_id = property_id

        # Create the corresponding booking record
        new_booking = Booking(
            user_id=session['user_id'],
            property_id=property_id,
            name=data.get('name', 'N/A'),
            email=data.get('email', 'N/A'),
            phone=data.get('phone', 'N/A'),
            message=data.get('message'),
            appointment_date=slot.date,
            appointment_time=slot.start_time,
            occupation=data.get('occupation'),
            monthly_income=data.get('monthly_income'),
            number_of_occupants=data.get('number_of_occupants'),
            status='pending',
            viewing_slot_id=slot.id
        )

        db.session.add(new_booking)
        db.session.commit()

        return jsonify({
            'success': True,
            'booking': new_booking.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500
