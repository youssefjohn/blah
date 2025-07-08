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
from src.models.notification import Notification

from src.routes.property import property_bp
from src.routes.auth import auth_bp
from src.routes.profile import profile_bp
from src.routes.booking import booking_bp
from src.routes.application import application_bp
from src.routes.notification import notification_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

CORS(app, origins=['http://localhost:5177'], supports_credentials=True)

# --- BLUEPRINT REGISTRATION ---
app.register_blueprint(property_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(profile_bp, url_prefix='/api')
app.register_blueprint(booking_bp, url_prefix='/api')
app.register_blueprint(application_bp)
app.register_blueprint(notification_bp, url_prefix='/api')

# --- DATABASE CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

# ❌ The db.create_all() call has been removed to let Flask-Migrate handle the schema.

# --- SERVE STATIC FILES (FOR PRODUCTION) ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
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
    app.run(host='0.0.0.0', port=5001, debug=True)
