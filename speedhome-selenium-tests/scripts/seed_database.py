#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta, date, time
# --- ADD THIS FOR MORE REALISTIC DATA ---
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('/app/.env')

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
from src.models.property import Property, PropertyStatus
from src.models.booking import Booking
from src.models.application import Application
from src.models.viewing_slot import ViewingSlot
from src.models.tenancy_agreement import TenancyAgreement
# --- FIX: Import the missing Notification model ---
from src.models.notification import Notification
from config.test_config import TestConfig


def seed_data():
    """
    Clears and seeds the database with a consistent set of test data.
    """
    with app.app_context():
        print("--- Starting database seed ---")
        print("Ensuring all tables are created...")
        db.create_all()

        # 1. Clear existing data to ensure a clean slate
        print("Clearing old data...")
        db.session.query(TenancyAgreement).delete()
        db.session.query(Application).delete()
        db.session.query(Booking).delete()
        db.session.query(ViewingSlot).delete()
        # --- FIX: Clear the Notification table as well ---
        db.session.query(Notification).delete()
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
            phone='0123456789',
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

        # 4. Create 50 properties for the landlord using a loop
        print("Creating 50 properties...")

        properties_to_add = []
        locations = ["Kuala Lumpur", "Petaling Jaya", "Subang Jaya", "Shah Alam", "Cyberjaya", "Putrajaya"]
        property_types = ["Condominium", "Apartment", "Terrace House", "Bungalow", "Studio"]
        furnished_options = ["Fully Furnished", "Partially Furnished", "Unfurnished"]

        for i in range(50):
            property_obj = Property(
                title=f"Spacious Property #{i + 1} in {random.choice(locations)}",
                location=random.choice(locations),
                price=random.randint(1500, 4500),
                sqft=random.randint(700, 2500),
                bedrooms=random.randint(1, 5),
                bathrooms=random.randint(1, 4),
                parking=random.randint(1, 3),
                property_type=property_types[i % len(property_types)],
                furnished=furnished_options[i % len(furnished_options)],
                description=f"A wonderful and well-maintained property, perfect for families and professionals. Property number {i + 1}.",
                owner_id=landlord.id,
                status=PropertyStatus.ACTIVE
            )
            properties_to_add.append(property_obj)

        db.session.add_all(properties_to_add)
        db.session.commit()
        print(f"Created {Property.query.count()} properties.")

        # --- The rest of your script for bookings and slots can be un-commented and used here ---
        # For example, to create slots for the landlord:
        #
        # print("Creating available slots for the landlord...")
        # for days_ahead in range(1, 15): # Next 14 days
        #     slot_date = (datetime.now() + timedelta(days=days_ahead)).date()
        #     for hour in range(9, 17): # 9am to 4:30pm
        #         for minute in [0, 30]:
        #             start_time = time(hour, minute)
        #             end_time = (datetime.combine(date.today(), start_time) + timedelta(minutes=30)).time()
        #             available_slot = ViewingSlot(
        #                 landlord_id=landlord.id,
        #                 date=slot_date,
        #                 start_time=start_time,
        #                 end_time=end_time,
        #                 is_available=True
        #             )
        #             db.session.add(available_slot)
        # db.session.commit()
        # print(f"✅ Created available slots. Total slots: {ViewingSlot.query.count()}")

        print("--- Database seeding complete! ---")
        print(f"📊 Summary:")
        print(f"   - Users: {User.query.count()}")
        print(f"   - Properties: {Property.query.count()}")
        print(f"   - Viewing Slots: {ViewingSlot.query.count()}")
        print(f"   - Bookings: {Booking.query.count()}")
        print(f"   - Notifications: {Notification.query.count()}")


if __name__ == "__main__":
    seed_data()