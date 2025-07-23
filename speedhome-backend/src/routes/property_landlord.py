from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta

from ..models.booking import Booking
from ..models.viewing_slot import ViewingSlot
from ..models.property import Property
from ..models.user import db

landlord_bp = Blueprint('landlord', __name__)


@landlord_bp.route('/landlord/<int:landlord_id>/recurring-availability', methods=['POST'])
def add_landlord_recurring_availability(landlord_id):
    """Add recurring availability for a landlord, with conflict detection."""
    try:
        # --- Authentication and Data Validation (same as your original code) ---
        if 'user_id' not in session or session.get('user_id') != landlord_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        required_fields = ['start_date', 'end_date', 'schedule']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        schedule = data.get('schedule', {})

        if end_date <= start_date:
            return jsonify({'success': False, 'error': 'End date must be after start date'}), 400

        if not isinstance(schedule, dict):
            return jsonify({'success': False, 'error': 'Schedule must be a valid object'}), 400

        day_mapping = {
            'sunday': 6, 'monday': 0, 'tuesday': 1, 'wednesday': 2,
            'thursday': 3, 'friday': 4, 'saturday': 5
        }

        # --- NEW: CONFLICT DETECTION LOGIC ---
        print("--- Checking for conflicts with confirmed bookings... ---")
        conflicting_bookings = []

        # 1. Find all properties owned by this landlord
        landlord_properties = Property.query.filter_by(owner_id=landlord_id).all()
        landlord_property_ids = [p.id for p in landlord_properties]

        # 2. Find all confirmed bookings for those properties within the date range.
        all_bookings_in_range = Booking.query.filter(
            Booking.property_id.in_(landlord_property_ids),
            Booking.status == 'confirmed',
            Booking.appointment_date.between(start_date, end_date)
        ).all()

        # 3. Check each booking against the NEW proposed schedule.
        for booking in all_bookings_in_range:
            booking_weekday = booking.appointment_date.weekday()
            is_now_unavailable = True

            for day_name, day_config in schedule.items():
                if day_mapping.get(day_name.lower()) == booking_weekday:
                    # The day is still in the schedule, now check the time.
                    try:
                        from_time = datetime.strptime(day_config['from'], '%H:%M').time()
                        to_time = datetime.strptime(day_config['to'], '%H:%M').time()
                        if from_time <= booking.appointment_time < to_time:
                            # The booking is still valid within the new time slot.
                            is_now_unavailable = False
                            break
                    except (ValueError, KeyError):
                        continue

            if is_now_unavailable:
                # This booking is no longer valid under the new schedule
                conflicting_bookings.append(booking.to_dict())

        # 4. If any conflicts were found, stop and return them to the frontend.
        if conflicting_bookings:
            print(f"--- CONFLICT DETECTED: {len(conflicting_bookings)} bookings are affected. ---")
            return jsonify({
                'success': False,
                'error': 'New availability conflicts with existing confirmed bookings.',
                'conflicts': conflicting_bookings
            }), 409  # 409 is the HTTP status code for "Conflict"

        # --- END OF CONFLICT DETECTION ---

        # --- MODIFIED: Only delete UNBOOKED slots ---
        print(f"Clearing existing UNBOOKED slots for landlord {landlord_id} from {start_date} to {end_date}")
        ViewingSlot.query.filter(
            ViewingSlot.landlord_id == landlord_id,
            ViewingSlot.date >= start_date,
            ViewingSlot.date <= end_date,
            ViewingSlot.is_available == True  # This is the crucial change
        ).delete()

        # --- Slot Creation Logic (same as your original code) ---
        slots_created = 0
        current_date = start_date
        while current_date <= end_date:
            weekday = current_date.weekday()
            for day_name, day_config in schedule.items():
                if day_mapping.get(day_name.lower()) == weekday:
                    try:
                        from_time = datetime.strptime(day_config['from'], '%H:%M').time()
                        to_time = datetime.strptime(day_config['to'], '%H:%M').time()

                        if to_time <= from_time: continue

                        start_datetime = datetime.combine(current_date, from_time)
                        end_datetime = datetime.combine(current_date, to_time)

                        current_slot_start = start_datetime
                        while current_slot_start < end_datetime:
                            current_slot_end = current_slot_start + timedelta(minutes=30)
                            if current_slot_end > end_datetime: break

                            new_slot = ViewingSlot(
                                landlord_id=landlord_id,
                                date=current_slot_start.date(),
                                start_time=current_slot_start.time(),
                                end_time=current_slot_end.time(),
                                is_available=True
                            )
                            db.session.add(new_slot)
                            slots_created += 1
                            current_slot_start = current_slot_end
                    except (ValueError, KeyError):
                        continue
            current_date += timedelta(days=1)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Successfully created {slots_created} new viewing slots.',
            'slots_created': slots_created
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500


@landlord_bp.route('/landlord/<int:landlord_id>/viewing-slots', methods=['GET'])
def get_landlord_viewing_slots(landlord_id):
    """Get all viewing slots for a landlord with correct booking status filtering"""
    try:
        # Get session data
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
        
        # Verify the landlord_id matches the session user_id
        if user_id != landlord_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized: Can only view your own slots'
            }), 403
        
        # Get all viewing slots for this landlord
        slots = ViewingSlot.query.filter(
            ViewingSlot.landlord_id == landlord_id
        ).order_by(ViewingSlot.date, ViewingSlot.start_time).all()
        
        # ✅ FIX: Update slot availability based on CONFIRMED bookings only
        for slot in slots:
            # Check if there's a CONFIRMED booking for this slot
            confirmed_booking = Booking.query.filter(
                Booking.viewing_slot_id == slot.id,
                Booking.status == 'confirmed'  # Only consider confirmed bookings
            ).first()
            
            if confirmed_booking:
                # Slot is booked by a confirmed booking
                slot.is_available = False
                slot.booked_by_user_id = confirmed_booking.user_id
            else:
                # No confirmed booking - slot should be available
                slot.is_available = True
                slot.booked_by_user_id = None
        
        # Convert to dictionary format
        slots_data = [slot.to_dict() for slot in slots]
        
        return jsonify({
            'success': True,
            'slots': slots_data,
            'total_slots': len(slots_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

