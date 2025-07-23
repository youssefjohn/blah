from flask import Blueprint, request, jsonify, session
from datetime import datetime, date, time, timedelta

from sqlalchemy.orm import joinedload

# --- CORRECTED IMPORTS ---
# Use consistent relative imports from the parent 'src' directory
from ..models.viewing_slot import ViewingSlot
from ..models.booking import Booking
from ..models.property import Property
from ..models.user import User
from ..models.notification import Notification
from ..models.user import db

# -------------------------

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/bookings', methods=['POST'])
def create_booking():
    """Create a new viewing request/booking (Legacy)"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        data = request.get_json()
        property_id = data.get('property_id')

        property_obj = Property.query.get(property_id)
        if not property_obj:
            return jsonify({'success': False, 'error': 'Property not found'}), 404

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

        landlord_notification = Notification(
            recipient_id=property_obj.owner_id,
            message=f"New viewing request for '{property_obj.title}' from {data.get('name')}.",
            link="/landlord"
        )
        db.session.add(landlord_notification)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Viewing request created successfully',
            'booking': booking.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@booking_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking_by_tenant(booking_id):
    """Allows a tenant to cancel their own booking."""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        if booking.user_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

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
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        if session['user_id'] != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        bookings = Booking.query.options(
            joinedload(Booking.property)
        ).filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()

        booking_list = []
        for booking in bookings:
            booking_dict = booking.to_dict()

            if booking.property:
                booking_dict['propertyTitle'] = booking.property.title
                booking_dict['property_id'] = booking.property.id

            booking_list.append(booking_dict)

        return jsonify({
            'success': True,
            'bookings': booking_list,
            'count': len(booking_list)
        })

    except Exception as e:
        print(f"Error in get_bookings_by_user: {e}")
        return jsonify({'success': False, 'error': 'An internal error occurred'}), 500


@booking_bp.route('/bookings/landlord/<int:landlord_id>', methods=['GET'])
def get_bookings_by_landlord(landlord_id):
    """Get all bookings for properties owned by a specific landlord"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        if session['user_id'] != landlord_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        properties = Property.query.filter_by(owner_id=landlord_id).all()
        property_ids = [prop.id for prop in properties]

        if not property_ids:
            return jsonify({
                'success': True,
                'bookings': [],
                'count': 0
            })

        bookings = Booking.query.filter(Booking.property_id.in_(property_ids)).order_by(Booking.created_at.desc()).all()

        booking_list = []
        for booking in bookings:
            booking_dict = booking.to_dict()

            property_obj = Property.query.get(booking.property_id)
            if property_obj:
                booking_dict['property'] = {
                    'id': property_obj.id,
                    'title': property_obj.title,
                    'location': property_obj.location,
                    'price': property_obj.price
                }

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
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['confirmed', 'cancelled', 'completed']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

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
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        property_obj = Property.query.get(booking.property_id)
        if (booking.user_id != session['user_id'] and
                (not property_obj or property_obj.owner_id != session['user_id'])):
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        booking_dict = booking.to_dict()

        if property_obj:
            booking_dict['property'] = {
                'id': property_obj.id,
                'title': property_obj.title,
                'location': property_obj.location,
                'price': property_obj.price
            }

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
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        data = request.get_json()
        new_date = data.get('date')
        new_time = data.get('time')
        requested_by = data.get('requested_by')

        if not new_date or not new_time or not requested_by:
            return jsonify({'success': False, 'error': 'Date, time, and requested_by are required'}), 400

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        property_obj = Property.query.get(booking.property_id)
        user_id = session['user_id']

        if booking.user_id != user_id and property_obj.owner_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        try:
            from datetime import datetime
            new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
            new_time_obj = datetime.strptime(new_time, '%H:%M').time()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date or time format'}), 400

        if not booking.original_date:
            booking.original_date = booking.appointment_date
            booking.original_time = booking.appointment_time

        booking.proposed_date = new_date_obj
        booking.proposed_time = new_time_obj
        booking.reschedule_requested_by = requested_by
        booking.status = 'pending'
        booking.updated_at = datetime.utcnow()

        if requested_by == 'tenant':
            booking.is_seen_by_landlord = False
            tenant = User.query.get(booking.user_id)
            landlord_notification = Notification(
                recipient_id=property_obj.owner_id,
                message=f"{tenant.get_full_name()} requested to reschedule the viewing for '{property_obj.title}'.",
                link="/landlord"
            )
            db.session.add(landlord_notification)

        elif requested_by == 'landlord':
            tenant_notification = Notification(
                recipient_id=booking.user_id,
                message=f"The landlord has proposed a new viewing time for '{property_obj.title}'.",
                link="/dashboard"
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

        if property_obj.owner_id != user_id and booking.user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        if booking.original_date and booking.original_time:
            booking.appointment_date = booking.original_date
            booking.appointment_time = booking.original_time

        booking.proposed_date = None
        booking.proposed_time = None
        booking.reschedule_requested_by = None
        booking.original_date = None
        booking.original_time = None
        booking.status = 'confirmed'
        booking.updated_at = datetime.utcnow()

        if user_id == booking.user_id:
            recipient_id = property_obj.owner_id
            message = f"The tenant has declined your reschedule proposal for '{property_obj.title}'. The original appointment is still active."
        else:
            recipient_id = booking.user_id
            message = f"Your reschedule request for '{property_obj.title}' was declined. The original appointment is still active."

        notification = Notification(
            recipient_id=recipient_id,
            message=message,
            link="/dashboard"
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
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        property_obj = Property.query.get(booking.property_id)
        user_id = session['user_id']

        if booking.user_id != user_id and property_obj.owner_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        if not booking.proposed_date or not booking.proposed_time:
            return jsonify({'success': False, 'error': 'No reschedule request to approve'}), 400

        booking.appointment_date = booking.proposed_date
        booking.appointment_time = booking.proposed_time
        booking.status = 'confirmed'

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
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        property_obj = Property.query.get(booking.property_id)
        user_id = session['user_id']

        if booking.user_id != user_id and property_obj.owner_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        if not booking.reschedule_requested_by:
            return jsonify({'success': False, 'error': 'No active reschedule request to cancel'}), 400

        if ((booking.reschedule_requested_by == 'tenant' and booking.user_id != user_id) or
                (booking.reschedule_requested_by == 'landlord' and property_obj.owner_id != user_id)):
            return jsonify({'success': False, 'error': 'Only the reschedule initiator can cancel the request'}), 403

        if booking.original_date and booking.original_time:
            booking.appointment_date = booking.original_date
            booking.appointment_time = booking.original_time

        booking.proposed_date = None
        booking.proposed_time = None
        booking.reschedule_requested_by = None
        booking.original_date = None
        booking.original_time = None

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
    if 'user_id' not in session:
        return jsonify({'success': True, 'has_scheduled': False})

    user_id = session['user_id']

    active_booking = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.property_id == property_id,
        Booking.status.notin_(['cancelled', 'declined'])
    ).first()

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
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        slot_id = data.get('viewing_slot_id')
        property_id = data.get('property_id')

        if not slot_id or not property_id:
            return jsonify({'success': False, 'error': 'slot_id and property_id are required'}), 400

        slot = ViewingSlot.query.get(slot_id)
        if not slot or not slot.is_available:
            return jsonify({'success': False, 'error': 'Viewing slot not found or already booked'}), 404

        slot.is_available = False
        slot.booked_by_user_id = session['user_id']
        slot.booked_for_property_id = property_id

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


# --- NEW ROUTE TO BE ADDED ---
@booking_bp.route('/bookings/resolve-conflicts', methods=['POST'])
def resolve_availability_conflicts():
    """
    Resolves conflicts by either cancelling or requesting reschedule for bookings,
    then applies the new availability schedule for the landlord.
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        landlord_id = session['user_id']
        data = request.get_json()

        resolution = data.get('resolution')  # 'cancel' or 'reschedule'
        conflict_ids = data.get('conflict_ids', [])

        if not resolution or not conflict_ids:
            return jsonify({'success': False, 'error': 'Resolution and conflict_ids are required'}), 400

        # Find all conflicting bookings and verify they belong to the landlord
        bookings_to_resolve = Booking.query.join(Property).filter(
            Property.owner_id == landlord_id,
            Booking.id.in_(conflict_ids)
        ).all()

        for booking in bookings_to_resolve:
            if resolution == 'cancel':
                booking.status = 'cancelled'
                
                # ✅ CRITICAL FIX: Update the viewing slot to make it available again
                if booking.viewing_slot_id:
                    viewing_slot = ViewingSlot.query.get(booking.viewing_slot_id)
                    if viewing_slot:
                        viewing_slot.is_available = True
                        viewing_slot.booked_by_user_id = None
                        print(f"🔄 Freed up viewing slot {viewing_slot.id} for {viewing_slot.date} {viewing_slot.start_time}")
                
                notification = Notification(
                    recipient_id=booking.user_id,
                    message=f"Your viewing for '{booking.property.title}' has been cancelled by the landlord due to a schedule change.",
                    link="/dashboard"
                )
                db.session.add(notification)

            elif resolution == 'reschedule':
                booking.status = 'pending'
                booking.reschedule_requested_by = 'landlord'
                
                # ✅ FIX: Find a valid available slot within the new schedule
                # Store original date/time before proposing new one
                if not booking.original_date:
                    booking.original_date = booking.appointment_date
                    booking.original_time = booking.appointment_time
                
                # Clear proposed time - tenant will choose new slot
                booking.proposed_date = None
                booking.proposed_time = None
                
                print(f"🔄 Reschedule requested for booking {booking.id}: Tenant will choose from available slots")
                
                notification = Notification(
                    recipient_id=booking.user_id,
                    message=f"The landlord has updated their schedule for '{booking.property.title}'. Please select a new viewing time from available slots.",
                    link="/dashboard"
                )
                db.session.add(notification)

        # Re-run the availability logic
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        schedule = data.get('schedule', {})
        day_mapping = {
            'sunday': 6, 'monday': 0, 'tuesday': 1, 'wednesday': 2,
            'thursday': 3, 'friday': 4, 'saturday': 5
        }

        ViewingSlot.query.filter(
            ViewingSlot.landlord_id == landlord_id,
            ViewingSlot.date.between(start_date, end_date),
            ViewingSlot.is_available == True
        ).delete()

        slots_created = 0
        current_date = start_date
        while current_date <= end_date:
            weekday = current_date.weekday()
            for day_name, day_config in schedule.items():
                if day_mapping.get(day_name.lower()) == weekday:
                    from_time = datetime.strptime(day_config['from'], '%H:%M').time()
                    to_time = datetime.strptime(day_config['to'], '%H:%M').time()
                    if to_time <= from_time: continue

                    current_slot_start = datetime.combine(current_date, from_time)
                    end_datetime = datetime.combine(current_date, to_time)

                    while current_slot_start < end_datetime:
                        current_slot_end = current_slot_start + timedelta(minutes=30)
                        if current_slot_end > end_datetime: break

                        db.session.add(ViewingSlot(
                            landlord_id=landlord_id,
                            date=current_slot_start.date(),
                            start_time=current_slot_start.time(),
                            end_time=current_slot_end.time()
                        ))
                        slots_created += 1
                        current_slot_start = current_slot_end
            current_date += timedelta(days=1)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Conflicts resolved and {slots_created} new slots created.',
            'slots_created': slots_created
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500


@booking_bp.route('/bookings/<int:booking_id>/select-reschedule-slot', methods=['POST'])
def select_reschedule_slot(booking_id):
    """Allow tenant to select a new slot when landlord requests reschedule"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        data = request.get_json()
        viewing_slot_id = data.get('viewing_slot_id')

        if not viewing_slot_id:
            return jsonify({'success': False, 'error': 'viewing_slot_id is required'}), 400

        # Get the booking and verify tenant ownership
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        if booking.user_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

        # Verify this is a landlord reschedule request
        if booking.reschedule_requested_by != 'landlord':
            return jsonify({'success': False, 'error': 'No landlord reschedule request found'}), 400

        # Get the selected viewing slot
        viewing_slot = ViewingSlot.query.get(viewing_slot_id)
        if not viewing_slot:
            return jsonify({'success': False, 'error': 'Viewing slot not found'}), 404

        if not viewing_slot.is_available:
            return jsonify({'success': False, 'error': 'Selected slot is no longer available'}), 400

        # Store the old viewing slot ID before updating
        old_viewing_slot_id = booking.viewing_slot_id

        # Update the booking with the new slot
        booking.appointment_date = viewing_slot.date
        booking.appointment_time = viewing_slot.start_time
        booking.status = 'confirmed'
        booking.reschedule_requested_by = None
        booking.proposed_date = None
        booking.proposed_time = None
        booking.viewing_slot_id = viewing_slot.id

        # Mark the new viewing slot as booked
        viewing_slot.is_available = False
        viewing_slot.booked_by_user_id = session['user_id']

        # Free up the old viewing slot if it exists and is different
        if old_viewing_slot_id and old_viewing_slot_id != viewing_slot.id:
            old_slot = ViewingSlot.query.get(old_viewing_slot_id)
            if old_slot:
                old_slot.is_available = True
                old_slot.booked_by_user_id = None
                print(f"🔄 Freed up old viewing slot {old_viewing_slot_id}")

        print(f"✅ Updated booking {booking_id} to new slot {viewing_slot.id}")

        # Notify the landlord
        property_obj = Property.query.get(booking.property_id)
        tenant = User.query.get(booking.user_id)
        
        landlord_notification = Notification(
            recipient_id=property_obj.owner_id,
            message=f"{tenant.get_full_name()} has selected a new viewing time for '{property_obj.title}': {viewing_slot.date} at {viewing_slot.start_time}.",
            link="/landlord"
        )
        db.session.add(landlord_notification)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'New viewing time selected successfully',
            'booking': booking.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

