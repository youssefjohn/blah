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
    column_list = ['id', 'recipient.username', 'message', 'is_read', 'created_at']
    column_searchable_list = ['message']
    column_filters = ['is_read', 'created_at']
    column_editable_list = ['is_read']

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
    # admin.add_view(ApplicationAdminView(Application, db.session, name='Applications', category='Property Management'))  # Temporarily disabled
    
    return admin

