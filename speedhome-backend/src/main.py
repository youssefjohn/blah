import os
import sys


# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from datetime import timedelta
from flask_migrate import Migrate
from src.models.user import db, User
from src.models.property import Property
from src.models.booking import Booking
from src.models.application import Application
from src.models.tenancy_agreement import TenancyAgreement
from src.models.notification import Notification
from src.models.viewing_slot import ViewingSlot
from src.models.conversation import Conversation
from src.models.message import Message

from src.routes.property import property_bp
from src.routes.property_landlord import landlord_bp
from src.routes.auth import auth_bp
from src.routes.profile import profile_bp
from src.routes.booking import booking_bp
from src.routes.application import application_bp
from src.routes.tenancy_agreement import tenancy_agreement_bp
from src.routes.notification import notification_bp
from src.routes.messaging import messaging_bp
from src.routes.documents import documents_bp
from src.routes.webhooks import webhooks_bp
from src.routes.stripe_config import stripe_config_bp
from src.routes.admin_testing import admin_testing_bp
from src.routes.deposit import deposit_bp
from src.routes.tenant_deposit import tenant_deposit_bp
from src.routes.deposit_payment import deposit_payment_bp
from src.routes.admin_deposit import admin_deposit_bp

# Import admin components
from src.admin.admin_config import init_admin
from src.admin.auth import admin_auth_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Stripe configuration (from environment variables)
app.config['STRIPE_SECRET_KEY'] = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_default')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_default')

CORS(app, origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], supports_credentials=True)

# --- BLUEPRINT REGISTRATION ---
app.register_blueprint(property_bp, url_prefix='/api')
app.register_blueprint(landlord_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(profile_bp, url_prefix='/api')
app.register_blueprint(booking_bp, url_prefix='/api')
app.register_blueprint(application_bp)
app.register_blueprint(tenancy_agreement_bp)
app.register_blueprint(notification_bp, url_prefix='/api')
app.register_blueprint(messaging_bp, url_prefix='/api')
app.register_blueprint(documents_bp)
app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')
app.register_blueprint(stripe_config_bp, url_prefix='/api/stripe')
app.register_blueprint(admin_testing_bp)
app.register_blueprint(deposit_bp)
app.register_blueprint(tenant_deposit_bp)
app.register_blueprint(deposit_payment_bp)
app.register_blueprint(admin_deposit_bp)

# Register admin authentication blueprint
app.register_blueprint(admin_auth_bp)

# --- DATABASE CONFIGURATION ---
# Use PostgreSQL from environment variable (no SQLite fallback)
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable is required")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

# Initialize Flask-Admin
admin = init_admin(app)

# Initialize and start background scheduler for property lifecycle management
try:
    from src.services.background_scheduler import init_scheduler, start_scheduler
    print("Initializing property lifecycle background scheduler...")
    init_scheduler(app)
    start_scheduler()
    print("✅ Background scheduler started successfully")
except Exception as e:
    print(f"❌️ Failed to start background scheduler: {str(e)}")
    print("Application will continue without background jobs")

# ✅ The db.create_all() call has been removed to let Flask-Migrate handle the schema.

# --- SERVE STATIC FILES (FOR PRODUCTION) ---
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    uploads_dir = os.path.join(app.root_path, '..', 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# --- RUN THE APP ---
if __name__ == '__main__':
    # Run expiry check on startup
    try:
        with app.app_context():
            from src.services.expiry_service import expiry_service
            expired_count = expiry_service.check_and_expire_agreements()
            if expired_count > 0:
                print(f"Startup: Expired {expired_count} agreements")
            else:
                print("Startup: No agreements to expire")
    except Exception as e:
        print(f"Startup expiry check failed: {str(e)}")
    
    # Initialize and start deposit background jobs
    try:
        from src.services.background_jobs import start_background_jobs
        print("Starting deposit background jobs...")
        start_background_jobs()
        print("✅ Deposit background jobs started successfully")
    except Exception as e:
        print(f"❌️ Failed to start deposit background jobs: {str(e)}")
        print("Application will continue without deposit background processing")

    app.run(host='0.0.0.0', port=5001, debug=True)


