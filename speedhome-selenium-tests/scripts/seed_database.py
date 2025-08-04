import sys
import os
from datetime import datetime, timedelta, date, time

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
from src.models.booking import Booking
from src.models.application import Application
# --- ADD THIS IMPORT ---
from src.models.viewing_slot import ViewingSlot
from config.test_config import TestConfig
from src.models.tenancy_agreement import TenancyAgreement


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
        db.session.query(ViewingSlot).delete()  # Also clear viewing slots
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
        #
        # # --- UPDATED BOOKING INJECTION LOGIC FOR LANDLORD-BASED SYSTEM ---
        # print("Injecting a pre-booked viewing slot...")
        #
        # # Step A: Create an available viewing slot for the landlord (LANDLORD-BASED)
        # appointment_datetime = datetime.now() + timedelta(days=7)
        # slot_to_book = ViewingSlot(
        #     landlord_id=landlord.id,  # ✅ FIXED: Use landlord_id instead of property_id
        #     date=appointment_datetime.date(),
        #     start_time=time(11, 0),  # 11:00 AM
        #     end_time=time(11, 30),  # 11:30 AM
        #     is_available=False,  # Mark as unavailable (booked)
        #     booked_by_user_id=tenant.id  # ✅ FIXED: Removed booked_for_property_id
        # )
        # db.session.add(slot_to_book)
        # db.session.commit()  # Commit to get the slot_to_book.id
        #
        # # Step B: Create a booking that is linked to the slot
        # confirmed_booking = Booking(
        #     user_id=tenant.id,
        #     property_id=property1.id,  # The property being viewed
        #     viewing_slot_id=slot_to_book.id,  # Link to the landlord's time slot
        #     name=tenant.get_full_name(),
        #     email=tenant.email,
        #     phone="0123456789",
        #     appointment_date=slot_to_book.date,
        #     appointment_time=slot_to_book.start_time,
        #     status='confirmed',
        #     is_seen_by_landlord=True
        # )
        # db.session.add(confirmed_booking)
        # db.session.commit()
        # print("✅ Confirmed viewing request and slot created successfully.")
        #
        # # --- OPTIONAL: Create some additional available slots for testing ---
        # print("Creating additional available slots for testing...")
        #
        # # Create slots for the next few days
        # for days_ahead in range(1, 8):  # Next 7 days
        #     slot_date = (datetime.now() + timedelta(days=days_ahead)).date()
        #
        #     # Create morning slots (9:00-12:00, 30-minute intervals)
        #     for hour in range(9, 12):
        #         for minute in [0, 30]:
        #             start_time = time(hour, minute)
        #             end_time = time(hour, minute + 30) if minute == 0 else time(hour + 1, 0)
        #
        #             available_slot = ViewingSlot(
        #                 landlord_id=landlord.id,
        #                 date=slot_date,
        #                 start_time=start_time,
        #                 end_time=end_time,
        #                 is_available=True,  # Available for booking
        #                 booked_by_user_id=None
        #             )
        #             db.session.add(available_slot)

        db.session.commit()
        print(f"✅ Created additional available slots. Total slots: {ViewingSlot.query.count()}")

        print("--- Database seeding complete! ---")
        print(f"📊 Summary:")
        print(f"   - Users: {User.query.count()}")
        print(f"   - Properties: {Property.query.count()}")
        print(f"   - Viewing Slots: {ViewingSlot.query.count()}")
        print(f"   - Bookings: {Booking.query.count()}")


if __name__ == "__main__":
    seed_data()