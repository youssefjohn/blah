from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from ..models.viewing_slot import ViewingSlot
from ..models.property import Property
from ..models.user import db

landlord_bp = Blueprint('landlord', __name__)

@landlord_bp.route('/landlord/<int:landlord_id>/recurring-availability', methods=['POST'])
def add_landlord_recurring_availability(landlord_id):
    """Add recurring availability for a landlord (not property-specific)"""
    try:
        # Get session data
        session_data = session.copy()
        print(f"Session data: {session_data}")
        
        user_id = session.get('user_id')
        print(f"User ID in session: {user_id}")
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
        
        # Verify the landlord_id matches the session user_id
        if user_id != landlord_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized: Can only set availability for yourself'
            }), 403
        
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
            'sunday': 6,    # JS: 0 -> Python: 6
            'monday': 0,    # JS: 1 -> Python: 0
            'tuesday': 1,   # JS: 2 -> Python: 1
            'wednesday': 2, # JS: 3 -> Python: 2
            'thursday': 3,  # JS: 4 -> Python: 3
            'friday': 4,    # JS: 5 -> Python: 4
            'saturday': 5   # JS: 6 -> Python: 5
        }
        
        # Clear existing viewing slots for this landlord in the date range
        print(f"Clearing existing slots for landlord {landlord_id} from {start_date} to {end_date}")
        existing_slots = ViewingSlot.query.filter(
            ViewingSlot.landlord_id == landlord_id,
            ViewingSlot.date >= start_date,
            ViewingSlot.date <= end_date
        ).all()
        
        for slot in existing_slots:
            db.session.delete(slot)
        
        print(f"Deleted {len(existing_slots)} existing slots")
        
        slots_created = 0
        
        # Iterate through each date in the range
        current_date = start_date
        while current_date <= end_date:
            # Get the day of the week
            weekday = current_date.weekday()
            print(f"Checking {current_date} (Weekday is {weekday})")
            
            # Check if this day is in the schedule
            day_found = False
            for day_name, day_config in schedule.items():
                if day_name.lower() in day_mapping and day_mapping[day_name.lower()] == weekday:
                    day_found = True
                    print(f"Found schedule for {day_name} on {current_date}")
                    try:
                        from_time = datetime.strptime(day_config['from'], '%H:%M').time()
                        to_time = datetime.strptime(day_config['to'], '%H:%M').time()

                        if to_time <= from_time:
                            print(f"Invalid time range for {day_name}: {from_time} to {to_time}")
                            continue

                        start_datetime = datetime.combine(current_date, from_time)
                        end_datetime = datetime.combine(current_date, to_time)

                        current_slot_start = start_datetime
                        while current_slot_start < end_datetime:
                            current_slot_end = current_slot_start + timedelta(minutes=30)

                            if current_slot_end > end_datetime:
                                break

                            # Create the landlord-based slot
                            new_slot = ViewingSlot(
                                landlord_id=landlord_id,  # Changed from property_id to landlord_id
                                date=current_slot_start.date(),
                                start_time=current_slot_start.time(),
                                end_time=current_slot_end.time(),
                                is_available=True
                            )
                            db.session.add(new_slot)
                            slots_created += 1
                            print(f"Created slot: {current_slot_start.date()} ({current_slot_start.strftime('%A')}) {current_slot_start.time()} - {current_slot_end.time()}")

                            current_slot_start = current_slot_end

                    except (ValueError, KeyError) as e:
                        print(f"Error processing {day_name}: {e}")
                        continue
                    break  # Only process one matching day per date
            
            if not day_found:
                print(f"No schedule found for {current_date} (weekday {weekday})")
            
            # Move to next date
            current_date += timedelta(days=1)
        
        # Commit all the new slots
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully created {slots_created} viewing slots for landlord',
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

@landlord_bp.route('/landlord/<int:landlord_id>/viewing-slots', methods=['GET'])
def get_landlord_viewing_slots(landlord_id):
    """Get all viewing slots for a landlord"""
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

