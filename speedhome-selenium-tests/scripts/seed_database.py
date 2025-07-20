import sys
import os
from datetime import datetime, timedelta

# This path addition tells the script where its own project root is,
# allowing it to find the 'config' module.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# This adds the backend project to Python's path.
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'speedhome-backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Now we can import from your Flask app
from src.main import app, db
from src.models.user import User
from src.models.property import Property
from src.models.booking import Booking      # <-- Import Booking
from src.models.application import Application # <-- Import Application
from config.test_config import TestConfig 

def seed_data():
    """
    Clears and seeds the database with a consistent set of test data.
    """
    with app.app_context():
        print("--- Starting database seed ---")

        # 1. Clear existing data to ensure a clean slate
        # We delete in this specific order to respect database relationships.
        print("Clearing old data...")
        db.session.query(Application).delete()
        db.session.query(Booking).delete()
        db.session.query(Property).delete()
        db.session.query(User).delete()
        db.session.commit()

        # 2. Create the standard test landlord
        print(f"Creating landlord: {TestConfig.LANDLORD_EMAIL}")
        landlord = User(
            username='testlandlord',
            email=TestConfig.LANDLORD_EMAIL,
            first_name='Test',
            last_name='Landlord',
            role='landlord',
            is_verified=True
        )
        landlord.set_password(TestConfig.LANDLORD_PASSWORD)
        db.session.add(landlord)

        # 3. Create the standard test tenant
        print(f"Creating tenant: {TestConfig.TENANT_EMAIL}")
        tenant = User(
            username='testtenant',
            email=TestConfig.TENANT_EMAIL,
            first_name='Test',
            last_name='Tenant',
            role='tenant',
            is_verified=True
        )
        tenant.set_password(TestConfig.TENANT_PASSWORD)
        db.session.add(tenant)
        
        db.session.commit()
        print("Users created successfully.")

        # 4. Create properties for the landlord
        print("Creating properties...")
        property1 = Property(
            title="Modern Condo in KL City",
            location="Kuala Lumpur",
            price=2500,
            sqft=1100,
            bedrooms=3,
            bathrooms=2,
            parking=2,
            property_type="Condominium",
            furnished="Fully Furnished",
            description="A beautiful condo in the heart of Kuala Lumpur.",
            owner_id=landlord.id,
            status="Active"
        )

        property2 = Property(
            title="Cozy Apartment in Petaling Jaya",
            location="Petaling Jaya",
            price=1800,
            sqft=850,
            bedrooms=2,
            bathrooms=2,
            parking=1,
            property_type="Apartment",
            furnished="Partially Furnished",
            description="A great place for a small family or couple.",
            owner_id=landlord.id,
            status="Active"
        )
        
        db.session.add_all([property1, property2])
        db.session.commit()
        print(f"Created {Property.query.count()} properties.")

        print("Injecting a confirmed viewing request...")
        confirmed_booking = Booking(
            user_id=tenant.id,
            property_id=property1.id,
            name=tenant.get_full_name(),
            email=tenant.email,
            phone="0123456789",
            appointment_date=datetime.now().date() + timedelta(days=7),
            appointment_time=datetime.strptime("11:00", "%H:%M").time(),
            status='confirmed',  # The request is already confirmed (lowercase 'c')
            is_seen_by_landlord=True
        )
        db.session.add(confirmed_booking)
        db.session.commit()
        print("✅ Confirmed viewing request created.")
        

        print("--- Database seeding complete! ---")

if __name__ == '__main__':
    seed_data()
