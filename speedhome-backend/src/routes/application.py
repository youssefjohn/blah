from flask import Blueprint, request, jsonify, session, current_app
from src.models.user import db, User
from src.models.property import Property
from src.models.application import Application
from src.models.notification import Notification
from src.services.pdf_service import pdf_service
from datetime import datetime, timedelta
from src.models.tenancy_agreement import TenancyAgreement

application_bp = Blueprint('application_bp', __name__, url_prefix='/api/applications')

def safe_date_parse(date_string):
    """Safely parse date string to date object."""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

def safe_numeric_parse(value, data_type=float):
    """Safely parse numeric values."""
    if not value or value == '':
        return None
    try:
        return data_type(value)
    except (ValueError, TypeError):
        return None

def safe_int_parse(value):
    """Safely parse integer values."""
    return safe_numeric_parse(value, int)

# Route for a tenant to submit an application
@application_bp.route('/', methods=['POST'])
def submit_application():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        data = request.get_json()
        property_id = data.get('propertyId')
        
        if not property_id:
            return jsonify({'success': False, 'error': 'Property ID is required'}), 400
            
        prop = Property.query.get(property_id)
        if not prop:
            return jsonify({'success': False, 'error': 'Property not found'}), 404

        if prop.status != 'Active':
            return jsonify({'success': False, 'error': 'This property is not currently accepting applications.'}), 400
            
        existing_app = Application.query.filter_by(
            tenant_id=session['user_id'],
            property_id=property_id
        ).first()

        if existing_app:
            return jsonify({'success': False, 'error': 'You have already applied for this property.'}), 409

        # Create new application with Enhanced Application Form data and proper error handling
        try:
            new_app = Application(
                property_id=property_id,
                tenant_id=session['user_id'],
                landlord_id=prop.owner_id,
                message=data.get('message', ''),
                
                # Personal Information
                full_name=data.get('full_name'),
                phone_number=data.get('phone_number'),
                email=data.get('email_address'),  # Note: frontend sends 'email_address', model expects 'email'
                date_of_birth=safe_date_parse(data.get('date_of_birth')),
                emergency_contact_name=data.get('emergency_contact_name'),
                emergency_contact_phone=data.get('emergency_contact_phone'),
                
                # Employment Information
                employment_status=data.get('employment_status'),
                employer_name=data.get('employer_name'),
                job_title=data.get('job_title'),
                employment_duration=data.get('employment_duration'),
                monthly_income=safe_numeric_parse(data.get('monthly_income')),
                additional_income=safe_numeric_parse(data.get('additional_income')),
                
                # Financial Information
                bank_name=data.get('bank_name'),
                credit_score=safe_int_parse(data.get('credit_score')),
                monthly_expenses=safe_numeric_parse(data.get('monthly_expenses')),
                current_rent=safe_numeric_parse(data.get('current_rent')),
                
                # Rental History
                previous_address=data.get('previous_address'),
                previous_landlord_name=data.get('previous_landlord_name'),
                previous_landlord_phone=data.get('previous_landlord_phone'),
                rental_duration=data.get('rental_duration'),
                reason_for_moving=data.get('reason_for_moving'),
                
                # Preferences
                move_in_date=safe_date_parse(data.get('move_in_date')),
                lease_duration_preference=data.get('lease_duration'),
                number_of_occupants=safe_int_parse(data.get('number_of_occupants')),
                pets=data.get('pets') == 'Yes',
                smoking=data.get('smoking') == 'Yes',
                additional_notes=data.get('additional_notes'),
                
                # Application Status
                step_completed=data.get('step_completed', 6),
                is_complete=data.get('is_complete', True)
            )
            print("Application object created successfully")
        except Exception as e:
            print(f"Error creating Application object: {str(e)}")
            return jsonify({'success': False, 'error': f'Error creating application: {str(e)}'}), 500
        
        try:
            db.session.add(new_app)
            print("Application added to session successfully")
        except Exception as e:
            print(f"Error adding application to session: {str(e)}")
            return jsonify({'success': False, 'error': f'Error adding application to session: {str(e)}'}), 500
        
        try:
            tenant = User.query.get(session['user_id'])
            print("Tenant retrieved successfully")
        except Exception as e:
            print(f"Error retrieving tenant: {str(e)}")
            return jsonify({'success': False, 'error': f'Error retrieving tenant: {str(e)}'}), 500
        
        try:
            landlord_notification = Notification(
                recipient_id=prop.owner_id,
                message=f"New comprehensive application for '{prop.title}' from {new_app.full_name or tenant.get_full_name()}.",
                link="/landlord"
            )
            db.session.add(landlord_notification)
            print("Notification created and added successfully")
        except Exception as e:
            print(f"Error creating notification: {str(e)}")
            return jsonify({'success': False, 'error': f'Error creating notification: {str(e)}'}), 500
        
        try:
            db.session.commit()
            print("Database commit successful")
        except Exception as e:
            print(f"Error committing to database: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Error saving to database: {str(e)}'}), 500
        
        try:
            response_data = new_app.to_dict()
            print("Application to_dict() successful")
        except Exception as e:
            print(f"Error converting application to dict: {str(e)}")
            return jsonify({'success': False, 'error': f'Error preparing response: {str(e)}'}), 500
        
        return jsonify({'success': True, 'application': response_data}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in submit_application: {str(e)}")  # For debugging
        return jsonify({'success': False, 'error': 'Internal server error occurred while processing application'}), 500

# Route for a landlord to view their applications
@application_bp.route('/landlord', methods=['GET'])
def get_landlord_applications():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
    apps = Application.query.filter_by(landlord_id=session['user_id']).order_by(Application.created_at.desc()).all()
    return jsonify({'success': True, 'applications': [app.to_dict() for app in apps]})


# NEW ROUTE: Landlord marks an application as seen
@application_bp.route('/<int:application_id>/mark-seen', methods=['POST'])
def mark_application_as_seen(application_id):
    # Ensure a landlord is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    # Find the application by its ID
    application = Application.query.get(application_id)

    if not application:
        return jsonify({'success': False, 'error': 'Application not found'}), 404

    # Security check: ensure the logged-in user is the landlord for this application
    if application.landlord_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    # Update the field to True
    application.is_seen_by_landlord = True

    # Commit the change to the database to save it
    db.session.commit()

    return jsonify({'success': True, 'message': 'Application marked as seen successfully'}), 200

# Route for a tenant to view their own applications
@application_bp.route('/tenant', methods=['GET'])
def get_tenant_applications():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
    apps = Application.query.filter_by(tenant_id=session['user_id']).order_by(Application.created_at.desc()).all()
    return jsonify({'success': True, 'applications': [app.to_dict() for app in apps]})

# Route for a tenant to withdraw (DELETE) an application
@application_bp.route('/<int:application_id>', methods=['DELETE'])
def withdraw_application(application_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    app = Application.query.get(application_id)
    if not app:
        return jsonify({'success': False, 'error': 'Application not found'}), 404

    if app.tenant_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized. You can only withdraw your own applications.'}), 403

    if app.status != 'pending':
        return jsonify({'success': False, 'error': f'Cannot withdraw an application with status "{app.status}".'}), 400

    db.session.delete(app)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Application withdrawn successfully'})


# Route for updating an application (draft to final submission)
@application_bp.route('/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        app = Application.query.get(application_id)
        if not app:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
            
        # Security check: ensure the logged-in user is the tenant who owns this application
        if app.tenant_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Unauthorized. You can only update your own applications.'}), 403
        
        data = request.get_json()
        
        # Update application fields with new data
        if 'full_name' in data:
            app.full_name = data['full_name']
        if 'phone_number' in data:
            app.phone_number = data['phone_number']
        if 'email_address' in data:
            app.email = data['email_address']
        if 'date_of_birth' in data:
            app.date_of_birth = safe_date_parse(data['date_of_birth'])
        if 'emergency_contact_name' in data:
            app.emergency_contact_name = data['emergency_contact_name']
        if 'emergency_contact_phone' in data:
            app.emergency_contact_phone = data['emergency_contact_phone']
            
        # Employment Information
        if 'employment_status' in data:
            app.employment_status = data['employment_status']
        if 'employer_name' in data:
            app.employer_name = data['employer_name']
        if 'job_title' in data:
            app.job_title = data['job_title']
        if 'employment_duration' in data:
            app.employment_duration = data['employment_duration']
        if 'monthly_income' in data:
            app.monthly_income = safe_numeric_parse(data['monthly_income'])
        if 'additional_income' in data:
            app.additional_income = safe_numeric_parse(data['additional_income'])
            
        # Financial Information
        if 'bank_name' in data:
            app.bank_name = data['bank_name']
        if 'credit_score' in data:
            app.credit_score = safe_int_parse(data['credit_score'])
        if 'monthly_expenses' in data:
            app.monthly_expenses = safe_numeric_parse(data['monthly_expenses'])
        if 'current_rent' in data:
            app.current_rent = safe_numeric_parse(data['current_rent'])
            
        # Rental History
        if 'previous_address' in data:
            app.previous_address = data['previous_address']
        if 'previous_landlord_name' in data:
            app.previous_landlord_name = data['previous_landlord_name']
        if 'previous_landlord_phone' in data:
            app.previous_landlord_phone = data['previous_landlord_phone']
        if 'rental_duration' in data:
            app.rental_duration = data['rental_duration']
        if 'reason_for_moving' in data:
            app.reason_for_moving = data['reason_for_moving']
            
        # Preferences
        if 'move_in_date' in data:
            app.move_in_date = safe_date_parse(data['move_in_date'])
        if 'lease_duration' in data:
            app.lease_duration_preference = data['lease_duration']
        if 'number_of_occupants' in data:
            app.number_of_occupants = safe_int_parse(data['number_of_occupants'])
        if 'pets' in data:
            app.pets = data['pets'] == 'Yes'
        if 'smoking' in data:
            app.smoking = data['smoking'] == 'Yes'
        if 'additional_notes' in data:
            app.additional_notes = data['additional_notes']
            
        # Application Status Updates
        if 'step_completed' in data:
            app.step_completed = data['step_completed']
        if 'is_complete' in data:
            app.is_complete = data['is_complete']
        if 'status' in data:
            app.status = data['status']
            
        # Update the updated_at timestamp
        app.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'application': app.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_application: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error occurred while updating application'}), 500


# Route for a landlord to update an application's status
@application_bp.route('/<int:application_id>/status', methods=['PUT'])
def update_application_status(application_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    app = Application.query.get(application_id)
    if not app:
        return jsonify({'success': False, 'error': 'Application not found'}), 404

    if app.landlord_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['approved', 'rejected']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400

    app.status = new_status

    prop = Property.query.get(app.property_id)

    # Create a notification for the tenant whose application status changed
    tenant_notification = Notification(
        recipient_id=app.tenant_id,
        message=f"Your application for '{prop.title}' has been {new_status}.",
        link="/dashboard"
    )
    db.session.add(tenant_notification)

    if new_status == 'approved':
        # 1. Update the property status to 'Rented'
        if prop:
            prop.status = 'Rented'
            db.session.add(prop)

        # 2. Reject all other pending applications for this same property
        other_pending_apps = Application.query.filter(
            Application.property_id == app.property_id,
            Application.id != application_id,
            Application.status == 'pending'
        ).all()

        for other_app in other_pending_apps:
            other_app.status = 'rejected'
            db.session.add(other_app)

            rejection_notification = Notification(
                recipient_id=other_app.tenant_id,
                message=f"A property you applied for, '{prop.title}', is no longer available.",
                link="/dashboard"
            )
            db.session.add(rejection_notification)

        # --- ✅ START: NEW AGREEMENT & PDF LOGIC ---
        # Check if an agreement already exists to avoid duplicates
        existing_agreement = TenancyAgreement.query.filter_by(application_id=app.id).first()
        if not existing_agreement:
            tenant = User.query.get(app.tenant_id)
            landlord = User.query.get(app.landlord_id)

            # Calculate lease end date and months, with defaults
            lease_end = None
            months = 12  # Default to 12 months if not specified
            if app.lease_duration_preference:
                try:
                    # Handle cases like "12 months" or just "12"
                    months = int(app.lease_duration_preference.split()[0])
                except (ValueError, IndexError):
                    # If parsing fails, fall back to the default
                    months = 12

            if app.move_in_date:
                lease_end = app.move_in_date + timedelta(days=months * 30)  # Approximation

            # 3. Create the TenancyAgreement record
            new_agreement = TenancyAgreement(
                application_id=app.id,
                property_id=app.property_id,
                landlord_id=app.landlord_id,
                tenant_id=app.tenant_id,
                monthly_rent=prop.price,
                # TODO: At some point review this so we can possibly have a dynamic calculation based on property size/rent or whatever
                payment_required=399.00,
                security_deposit=prop.price * 2,  # Example: 2 months rent
                lease_start_date=app.move_in_date,
                lease_end_date=lease_end,
                lease_duration_months=months,
                property_address=prop.location,
                property_type=prop.property_type,
                property_bedrooms=prop.bedrooms,
                property_bathrooms=prop.bathrooms,
                property_sqft=prop.sqft,
                tenant_full_name=app.full_name or tenant.get_full_name(),
                tenant_phone=app.phone_number or tenant.phone,
                tenant_email=app.email or tenant.email,
                landlord_full_name=landlord.get_full_name(),
                landlord_phone=landlord.phone,
                landlord_email=landlord.email,
            )
            db.session.add(new_agreement)
            db.session.commit()  # Commit here to get the new_agreement.id

            # 4. Generate and save the DRAFT PDF using your service
            try:
                pdf_path = pdf_service.generate_draft_pdf(new_agreement, prop)
                # 5. Save the file path to the database
                new_agreement.draft_pdf_path = pdf_path
                db.session.add(new_agreement)
            except Exception as e:
                current_app.logger.error(f"Failed to generate PDF for new agreement {new_agreement.id}: {e}")
        # --- ✅ END: NEW AGREEMENT & PDF LOGIC ---

    db.session.commit()

    return jsonify({'success': True, 'application': app.to_dict()})

@application_bp.route('/status', methods=['GET'])
def get_application_status_for_property():
    if 'user_id' not in session:
        return jsonify({'success': True, 'has_applied': False})

    property_id = request.args.get('property_id', type=int)
    if not property_id:
        return jsonify({'success': False, 'error': 'Property ID is required'}), 400

    existing_app = Application.query.filter_by(
        tenant_id=session['user_id'],
        property_id=property_id
    ).first()

    return jsonify({'success': True, 'has_applied': (existing_app is not None)})
