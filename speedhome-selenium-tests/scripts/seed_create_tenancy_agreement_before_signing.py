#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta, date
from decimal import Decimal
from config.test_config import TestConfig
from dotenv import load_dotenv

# Use a reliable, absolute path inside the container
backend_path = '/app'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

dotenv_path = os.path.join(backend_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

try:
    from src.main import app
    from src.models.user import db, User
    from src.models.property import Property, PropertyStatus
    from src.models.application import Application
    from src.models.tenancy_agreement import TenancyAgreement
    from src.models.deposit_transaction import DepositTransaction
    from src.models.deposit_claim import DepositClaim
    from src.models.notification import Notification
    from src.models.conversation import Conversation
    from src.models.message import Message
    from src.models.booking import Booking
    from src.models.viewing_slot import ViewingSlot

    with app.app_context():
        print("=== SIMPLE SEED SCRIPT ===")
        print("Ensuring all database tables exist...")

        # --- FIX: Create all tables first to ensure they exist ---
        db.create_all()

        print("🧹 COMPLETE DATABASE CLEANUP - Deleting ALL records...")

        # Delete ALL records from ALL tables in correct order (child tables first)
        print("Clearing all messages...")
        db.session.query(Message).delete()
        
        print("Clearing all conversations...")
        db.session.query(Conversation).delete()
        
        print("Clearing all notifications...")
        db.session.query(Notification).delete()
        
        print("Clearing all viewing slots...")
        db.session.query(ViewingSlot).delete()
        
        print("Clearing all bookings...")
        db.session.query(Booking).delete()
        
        print("Clearing all deposit claims...")
        db.session.query(DepositClaim).delete()
        
        print("Clearing all deposit transactions...")
        db.session.query(DepositTransaction).delete()
        
        print("Clearing all tenancy agreements...")
        db.session.query(TenancyAgreement).delete()
        
        print("Clearing all applications...")
        db.session.query(Application).delete()
        
        print("Clearing all properties...")
        db.session.query(Property).delete()
        
        print("Clearing all users...")
        db.session.query(User).delete()
        
        # Commit the cleanup
        db.session.commit()
        print("✅ Database completely wiped clean!")

        print("\n🏗️ Creating fresh test data...")

        # ... (rest of your script is the same)
        # Create landlord
        landlord = User(
            email='landlord@test.com',
            username='landlord',
            first_name='John',
            last_name='Landlord',
            phone='+60123456789',
            role='landlord',
            is_verified=True
        )
        landlord.set_password(TestConfig.LANDLORD_PASSWORD)
        db.session.add(landlord)

        # Create tenant
        tenant = User(
            email='tenant@test.com',
            username='tenant',
            first_name='Jane',
            last_name='Tenant',
            phone='+60123456788',
            role='tenant',
            is_verified=True
        )
        tenant.set_password(TestConfig.TENANT_PASSWORD)
        db.session.add(tenant)
        db.session.commit()

        # Create property
        property_obj = Property(
            title='Test Property for Deposit System',
            description='A beautiful property for testing the deposit workflow',
            price=1500,
            location='Kuala Lumpur',
            property_type='apartment',
            bedrooms=2,
            bathrooms=2,
            sqft=800,
            owner_id=landlord.id,
            status=PropertyStatus.PENDING,
            date_added=datetime.utcnow() - timedelta(days=10)
        )
        db.session.add(property_obj)
        db.session.commit()

        # Create approved application
        application = Application(
            property_id=property_obj.id,
            tenant_id=tenant.id,
            landlord_id=landlord.id,
            status='approved',
            full_name=f"{tenant.first_name} {tenant.last_name}",
            email=tenant.email,
            phone_number=tenant.phone,
            employment_status='employed',
            monthly_income=5000.00,
            move_in_date=date.today() + timedelta(days=7),
            lease_duration_preference='12 months',
            is_complete=True,
            step_completed=6,
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        db.session.add(application)
        db.session.commit()

        # Create tenancy agreement (not signed yet)
        agreement = TenancyAgreement(
            property_id=property_obj.id,
            property_address=f"{property_obj.title}, {property_obj.location}",
            property_type=property_obj.property_type,
            tenant_id=tenant.id,
            tenant_full_name=f"{tenant.first_name} {tenant.last_name}",
            tenant_phone=tenant.phone,
            tenant_email=tenant.email,
            landlord_id=landlord.id,
            landlord_full_name=f"{landlord.first_name} {landlord.last_name}",
            landlord_phone=landlord.phone,
            landlord_email=landlord.email,
            monthly_rent=Decimal(str(property_obj.price)),
            security_deposit=Decimal(str(property_obj.price * 2.5)),
            lease_start_date=date.today() + timedelta(days=7),
            lease_end_date=date.today() + timedelta(days=372),
            lease_duration_months=12,
            status='pending_signatures',
            application_id=application.id,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(agreement)
        db.session.commit()

        print(f"✅ SUCCESS! Created fresh test data from scratch:")
        print(f"   🧹 Database completely wiped and reset")
        print(f"   👤 Landlord: {landlord.email} (ID: {landlord.id})")
        print(f"   👤 Tenant: {tenant.email} (ID: {tenant.id})")
        print(f"   🏠 Property: {property_obj.title} (ID: {property_obj.id})")
        print(f"   📋 Application: Approved (ID: {application.id})")
        print(f"   📄 Agreement: {agreement.status} (ID: {agreement.id})")
        print(f"   💰 Monthly Rent: RM {agreement.monthly_rent}")
        print(f"   💰 Security Deposit: RM {agreement.security_deposit}")
        print()
        print("🎯 READY FOR TESTING:")
        print("   1. Log in as landlord or tenant")
        print("   2. Navigate to tenancy agreements")
        print("   3. Sign the agreement")
        print("   4. Pay website fee")
        print("   5. Pay security deposit")
        print("   6. Test deposit management system")
        print()
        print(f"📝 NOTE: Agreement ID will always be 1 (fresh database)")
        print(f"📝 Deposit management URL: /deposit/1/manage")
        print()
        print("=== SEED COMPLETE ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()