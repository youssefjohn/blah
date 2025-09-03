from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user
from flask import redirect, url_for, request, flash
from werkzeug.security import check_password_hash
from ..models.user import User
from ..models.property import Property
from ..models.booking import Booking
from ..models.viewing_slot import ViewingSlot
from ..models.message import Message
from ..models.conversation import Conversation
from ..models.notification import Notification
from ..models.deposit_transaction import DepositTransaction
from ..models.deposit_claim import DepositClaim
# from ..models.application import Application  # Temporarily disabled due to migration issues import Notification

# Initialize Flask-Login
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AdminAuthMixin:
    """Mixin to require admin authentication for admin views"""
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        flash('You need admin privileges to access this page.', 'error')
        return redirect(url_for('admin_auth.login', next=request.url))

class SecureAdminIndexView(AdminAuthMixin, AdminIndexView):
    """Secure admin index view that requires authentication"""
    @expose('/')
    def index(self):
        # Get some basic stats for the dashboard
        stats = {
            'total_users': User.query.count(),
            'total_properties': Property.query.count(),
            'total_bookings': Booking.query.count(),
            # 'pending_applications': Application.query.filter_by(status='pending').count(),  # Temporarily disabled
            'total_messages': Message.query.count(),
        }
        return self.render('admin/index.html', stats=stats)

class UserAdminView(AdminAuthMixin, ModelView):
    """Admin view for User model"""
    column_list = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'created_at', 'is_active']
    column_searchable_list = ['username', 'email', 'first_name', 'last_name']
    column_filters = ['role', 'is_active', 'created_at']
    column_editable_list = ['is_active', 'role']
    form_excluded_columns = ['password_hash', 'created_at', 'updated_at']
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.set_password('admin123')  # Default password for admin-created users

class PropertyAdminView(AdminAuthMixin, ModelView):
    """Admin view for Property model"""
    column_list = ['id', 'title', 'owner.username', 'price', 'location', 'status', 'date_added']
    column_searchable_list = ['title', 'location', 'description']
    column_filters = ['status', 'property_type', 'date_added']
    column_editable_list = ['status']
    
class BookingAdminView(AdminAuthMixin, ModelView):
    """Admin view for Booking model"""
    column_list = ['id', 'user.username', 'property.title', 'status', 'appointment_date', 'created_at']
    column_filters = ['status', 'appointment_date', 'created_at']
    column_editable_list = ['status']

class ConversationAdminView(AdminAuthMixin, ModelView):
    """Admin view for Conversation model"""
    column_list = ['id', 'tenant.username', 'landlord.username', 'property.title', 'status', 'created_at']
    column_filters = ['status', 'created_at']
    column_editable_list = ['status']

class MessageAdminView(AdminAuthMixin, ModelView):
    """Admin view for Message model"""
    column_list = ['id', 'conversation_id', 'sender.username', 'message_body', 'created_at']
    column_searchable_list = ['message_body']
    column_filters = ['created_at', 'message_type', 'is_read']
    form_excluded_columns = ['created_at']

class ViewingSlotAdminView(AdminAuthMixin, ModelView):
    """Admin view for ViewingSlot model"""
    column_list = ['id', 'landlord.username', 'date', 'start_time', 'end_time', 'is_available', 'created_at']
    column_filters = ['is_available', 'date', 'created_at']
    column_editable_list = ['is_available']

class NotificationAdminView(AdminAuthMixin, ModelView):
    """Admin view for Notification model"""
    column_list = ['id', 'recipient_id', 'message', 'notification_type', 'is_read', 'created_at']
    column_searchable_list = ['message']  # Remove 'title' since it doesn't exist
    column_filters = ['notification_type', 'is_read', 'created_at', 'priority']
    column_editable_list = ['is_read']
    column_labels = {
        'recipient_id': 'Recipient',
        'notification_type': 'Type'
    }

class DepositTransactionAdminView(AdminAuthMixin, ModelView):
    """Admin view for Deposit Transactions"""
    column_list = ['id', 'property_id', 'tenant_id', 'landlord_id', 'amount', 'status', 'created_at']
    column_searchable_list = []  # Remove searchable fields that reference relationships
    column_filters = ['status', 'created_at']
    column_labels = {
        'property_id': 'Property',
        'tenant_id': 'Tenant', 
        'landlord_id': 'Landlord'
    }

class MediationClaimsAdminView(AdminAuthMixin, ModelView):
    """Admin view for Claims requiring mediation"""
    column_list = ['id', 'title', 'claimed_amount', 'tenant_counter_amount', 'status', 'created_at']
    column_searchable_list = ['title', 'description']
    column_filters = ['status', 'claim_type', 'created_at']
    column_labels = {
        'claimed_amount': 'Claimed Amount',
        'tenant_counter_amount': 'Tenant Counter-Offer'
    }
    
    # Enable custom row actions
    can_view_details = True
    
    def get_query(self):
        """Only show claims that are in mediation (under_review status)"""
        from ..models.deposit_claim import DepositClaimStatus
        return super(MediationClaimsAdminView, self).get_query().filter(
            self.model.status == DepositClaimStatus.UNDER_REVIEW
        )
    
    def get_count_query(self):
        """Count only mediation claims"""
        from ..models.deposit_claim import DepositClaimStatus
        return super(MediationClaimsAdminView, self).get_count_query().filter(
            self.model.status == DepositClaimStatus.UNDER_REVIEW
        )
    
    @expose('/details/')
    def details_view(self):
        """Override details view to redirect to mediation decision"""
        from flask import request, redirect, url_for
        id = request.args.get('id')
        if id:
            return redirect(url_for('admin_mediation.mediation_decision_view', id=id))
        return redirect(url_for('admin_mediation.index_view'))
    
    @expose('/mediation/<int:id>')
    def mediation_decision_view(self, id):
        """Custom view for making mediation decisions"""
        from ..models.deposit_claim import DepositClaim
        from ..models.deposit_transaction import DepositTransaction
        
        claim = DepositClaim.query.get_or_404(id)
        deposit = DepositTransaction.query.get(claim.deposit_transaction_id)
        
        # Get tenant and landlord info
        from ..models.user import User
        tenant = User.query.get(deposit.tenant_id)
        landlord = User.query.get(deposit.landlord_id)
        
        return self.render('admin/mediation_decision.html', 
                         claim=claim, 
                         deposit=deposit,
                         tenant=tenant,
                         landlord=landlord)
    
    @expose('/mediation/<int:id>/decide', methods=['POST'])
    def process_mediation_decision(self, id):
        """Process admin mediation decision"""
        from flask import request, flash, redirect, url_for
        from ..models.deposit_claim import DepositClaim, DepositClaimStatus
        from ..models.user import db
        from datetime import datetime
        
        claim = DepositClaim.query.get_or_404(id)
        
        decision = request.form.get('decision')
        admin_notes = request.form.get('admin_notes', '')
        custom_amount = request.form.get('custom_amount')
        
        try:
            if decision == 'award_full':
                claim.approved_amount = claim.claimed_amount
                claim.status = DepositClaimStatus.RESOLVED
                claim.resolution_notes = f"Admin Decision: Full amount awarded to landlord. {admin_notes}".strip()
                
            elif decision == 'award_partial':
                claim.approved_amount = float(custom_amount) if custom_amount else 0
                claim.status = DepositClaimStatus.RESOLVED
                claim.resolution_notes = f"Admin Decision: Partial amount (RM {claim.approved_amount}) awarded to landlord. {admin_notes}".strip()
                
            elif decision == 'reject_claim':
                claim.approved_amount = 0
                claim.status = DepositClaimStatus.RESOLVED
                claim.resolution_notes = f"Admin Decision: Claim rejected, full amount refunded to tenant. {admin_notes}".strip()
            
            claim.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash(f'Mediation decision processed successfully for claim: {claim.title}', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing decision: {str(e)}', 'error')
        
        return redirect(url_for('admin_mediation.index_view'))

class DepositClaimAdminView(AdminAuthMixin, ModelView):
    """Admin view for all Deposit Claims"""
    column_list = ['id', 'title', 'claimed_amount', 'approved_amount', 'status', 'claim_type', 'created_at']
    column_searchable_list = ['title', 'description']
    column_filters = ['status', 'claim_type', 'created_at']
    column_editable_list = ['approved_amount', 'status']
    column_labels = {
        'claimed_amount': 'Claimed Amount',
        'approved_amount': 'Approved Amount'
    }

def init_admin(app):
    """Initialize Flask-Admin with the Flask app"""
    from ..models.user import db
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'admin_auth.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    
    # Setup and return admin instance
    return setup_admin(app, db)
def setup_admin(app, db):
    """Setup Flask-Admin with all model views"""
    admin = Admin(app, name='SpeedHome Admin', template_mode='bootstrap4', index_view=SecureAdminIndexView())
    
    # Add model views with unique blueprint names
    admin.add_view(UserAdminView(User, db.session, name='Users', category='User Management', endpoint='admin_users'))
    admin.add_view(PropertyAdminView(Property, db.session, name='Properties', category='Property Management', endpoint='admin_properties'))
    admin.add_view(BookingAdminView(Booking, db.session, name='Bookings', category='Booking Management', endpoint='admin_bookings'))
    admin.add_view(ViewingSlotAdminView(ViewingSlot, db.session, name='Viewing Slots', category='Booking Management', endpoint='admin_viewing_slots'))
    admin.add_view(ConversationAdminView(Conversation, db.session, name='Conversations', category='Messaging', endpoint='admin_conversations'))
    admin.add_view(MessageAdminView(Message, db.session, name='Messages', category='Messaging', endpoint='admin_messages'))
    admin.add_view(NotificationAdminView(Notification, db.session, name='Notifications', category='System', endpoint='admin_notifications'))
    
    # Deposit Management Views
    admin.add_view(MediationClaimsAdminView(DepositClaim, db.session, name='Mediation Queue', category='Deposit Management', endpoint='admin_mediation'))
    admin.add_view(DepositClaimAdminView(DepositClaim, db.session, name='All Claims', category='Deposit Management', endpoint='admin_claims'))
    admin.add_view(DepositTransactionAdminView(DepositTransaction, db.session, name='Deposit Transactions', category='Deposit Management', endpoint='admin_deposits'))
    
    # admin.add_view(ApplicationAdminView(Application, db.session, name='Applications', category='Property Management'))  # Temporarily disabled
    
    return admin

