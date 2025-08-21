import sys
import os
from datetime import datetime, timedelta, date, time
# --- ADD THIS FOR MORE REALISTIC DATA ---
import random
from decimal import Decimal

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
from src.models.deposit_transaction import DepositTransaction, DepositTransactionStatus
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
        db.session.query(DepositTransaction).delete()
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
            # Set the last property to RENTED status for the active tenancy
            status = PropertyStatus.RENTED if i == 49 else PropertyStatus.ACTIVE
            
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
                status=status
            )
            properties_to_add.append(property_obj)

        db.session.add_all(properties_to_add)
        db.session.commit()
        print(f"Created {Property.query.count()} properties.")

        # 5. Create a complete active tenancy agreement on the last property
        print("Creating active tenancy agreement with deposit...")
        
        # Get the last property (Property #50)
        last_property = Property.query.filter_by(owner_id=landlord.id).order_by(Property.id.desc()).first()
        
        # Create an application first (required for tenancy agreement)
        application = Application(
            property_id=last_property.id,
            tenant_id=tenant.id,
            landlord_id=landlord.id,
            status='approved',
            monthly_rent=last_property.price,
            lease_duration_months=12,
            lease_start_date=date.today() - timedelta(days=30),  # Started 30 days ago
            lease_end_date=date.today() + timedelta(days=5),     # Ends in 5 days (for testing)
            created_at=datetime.utcnow() - timedelta(days=35),
            approved_at=datetime.utcnow() - timedelta(days=32)
        )
        db.session.add(application)
        db.session.commit()
        
        # Create the tenancy agreement
        agreement = TenancyAgreement(
            application_id=application.id,
            property_id=last_property.id,
            tenant_id=tenant.id,
            landlord_id=landlord.id,
            status='active',
            monthly_rent=Decimal(str(last_property.price)),
            security_deposit=Decimal(str(last_property.price * 2.5)),  # 2.5 months
            lease_start_date=application.lease_start_date,
            lease_end_date=application.lease_end_date,
            lease_duration_months=12,
            
            # Property details snapshot
            property_address=f"{last_property.title}, {last_property.location}",
            property_type=last_property.property_type,
            property_bedrooms=last_property.bedrooms,
            property_bathrooms=last_property.bathrooms,
            property_sqft=last_property.sqft,
            
            # Tenant details snapshot
            tenant_full_name=f"{tenant.first_name} {tenant.last_name}",
            tenant_phone=tenant.phone or "0123456789",
            tenant_email=tenant.email,
            
            # Landlord details snapshot
            landlord_full_name=f"{landlord.first_name} {landlord.last_name}",
            landlord_phone=landlord.phone,
            landlord_email=landlord.email,
            
            # Signatures and payment
            landlord_signed_at=datetime.utcnow() - timedelta(days=30),
            tenant_signed_at=datetime.utcnow() - timedelta(days=29),
            payment_completed_at=datetime.utcnow() - timedelta(days=28),
            payment_intent_id="pi_test_agreement_fee_paid",
            activated_at=datetime.utcnow() - timedelta(days=27),
            
            created_at=datetime.utcnow() - timedelta(days=31),
            updated_at=datetime.utcnow() - timedelta(days=27)
        )
        db.session.add(agreement)
        db.session.commit()
        
        # Create the deposit transaction
        deposit_amount = float(agreement.security_deposit)
        deposit = DepositTransaction(
            tenancy_agreement_id=agreement.id,
            property_id=last_property.id,
            tenant_id=tenant.id,
            landlord_id=landlord.id,
            amount=Decimal(str(deposit_amount)),
            calculation_base=agreement.monthly_rent,
            calculation_multiplier=Decimal('2.5'),
            status=DepositTransactionStatus.HELD_IN_ESCROW,
            payment_method='stripe',
            payment_intent_id="pi_test_deposit_paid_successfully",
            paid_at=datetime.utcnow() - timedelta(days=27),
            escrow_held_at=datetime.utcnow() - timedelta(days=27),
            created_at=datetime.utcnow() - timedelta(days=28),
            updated_at=datetime.utcnow() - timedelta(days=27)
        )
        db.session.add(deposit)
        db.session.commit()
        
        print(f"✅ Created active tenancy agreement:")
        print(f"   - Agreement ID: {agreement.id}")
        print(f"   - Property: {agreement.property_address}")
        print(f"   - Monthly Rent: RM {agreement.monthly_rent}")
        print(f"   - Security Deposit: RM {agreement.security_deposit}")
        print(f"   - Lease End Date: {agreement.lease_end_date} (5 days from now)")
        print(f"   - Deposit ID: {deposit.id}")
        print(f"   - Deposit Status: {deposit.status.value}")

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
        print(f"   - Applications: {Application.query.count()}")
        print(f"   - Tenancy Agreements: {TenancyAgreement.query.count()}")
        print(f"   - Deposit Transactions: {DepositTransaction.query.count()}")
        print(f"   - Viewing Slots: {ViewingSlot.query.count()}")
        print(f"   - Bookings: {Booking.query.count()}")
        print(f"   - Notifications: {Notification.query.count()}")
        print(f"")
        print(f"🧪 Ready for testing:")
        print(f"   - Login as landlord: {TestConfig.LANDLORD_EMAIL}")
        print(f"   - Test deposit management: /deposit/{agreement.id}/manage")
        print(f"   - Agreement ends in 5 days (tenancy ending soon)")


if __name__ == "__main__":
    seed_data()

