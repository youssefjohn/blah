from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.property import Property
from src.models.application import Application
from src.models.notification import Notification

application_bp = Blueprint('application_bp', __name__, url_prefix='/api/applications')

# Route for a tenant to submit an application
@application_bp.route('/', methods=['POST'])
def submit_application():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    data = request.get_json()
    property_id = data.get('propertyId')
    message = data.get('message')
    
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

    new_app = Application(
        property_id=property_id,
        tenant_id=session['user_id'],
        landlord_id=prop.owner_id,
        message=message
    )
    db.session.add(new_app)
    
    tenant = User.query.get(session['user_id'])
    
    landlord_notification = Notification(
        recipient_id=prop.owner_id,
        message=f"New application for '{prop.title}' from {tenant.get_full_name()}.",
        link="/landlord"
    )
    db.session.add(landlord_notification)
    
    db.session.commit()
    
    return jsonify({'success': True, 'application': new_app.to_dict()}), 201

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

    # ✅ --- START: NEW AUTOMATION LOGIC ---
    if new_status == 'approved':
        # 1. Update the property status to 'Rented'
        if prop:
            prop.status = 'Rented'
            db.session.add(prop)

        # 2. Find all other pending applications for this same property
        other_pending_apps = Application.query.filter(
            Application.property_id == app.property_id,
            Application.id != application_id, # Exclude the application we just approved
            Application.status == 'pending'
        ).all()

        # 3. Reject other applications and notify the applicants
        for other_app in other_pending_apps:
            other_app.status = 'rejected'
            db.session.add(other_app)
            
            rejection_notification = Notification(
                recipient_id=other_app.tenant_id,
                message=f"A property you applied for, '{prop.title}', is no longer available.",
                link="/dashboard"
            )
            db.session.add(rejection_notification)
    # ✅ --- END: NEW AUTOMATION LOGIC ---

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
