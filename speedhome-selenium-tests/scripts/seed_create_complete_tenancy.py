#!/usr/bin/env python3
"""
Complete Tenancy Agreement Creation Script

This script creates a tenancy agreement and automatically handles:
1. Creating landlord and tenant users
2. Creating property and application
3. Creating tenancy agreement
4. Signing the agreement (both parties)
5. Processing website fee payment
6. Creating and paying security deposit
7. Setting up deposit transaction

Ready for immediate deposit management testing!
"""

import sys
import os
from datetime import datetime, timedelta, date
from decimal import Decimal
from dotenv import load_dotenv

# Add the current directory to Python path for config import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.test_config import TestConfig

# Use a reliable, absolute path inside the container
backend_path = '/app'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Also add the speedhome-backend directory for local development
local_backend_path = os.path.join(os.path.dirname(os.path.dirname(parent_dir)), 'speedhome-backend')
if os.path.exists(local_backend_path) and local_backend_path not in sys.path:
    sys.path.insert(0, local_backend_path)

dotenv_path = os.path.join(backend_path, '.env')
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(local_backend_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

try:
    from src.main import app
    from src.models.user import db, User
    from src.models.property import Property, PropertyStatus
    from src.models.application import Application
    from src.models.tenancy_agreement import TenancyAgreement
    from src.models.deposit_transaction import DepositTransaction, DepositTransactionStatus
    from src.models.deposit_claim import DepositClaim
    from src.models.notification import Notification
    from src.models.conversation import Conversation
    from src.models.message import Message
    from src.models.booking import Booking
    from src.models.viewing_slot import ViewingSlot

    with app.app_context():
        print("=== COMPLETE TENANCY CREATION SCRIPT ===")
        print("Creating tenancy agreement with signing and payment...")

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
        
        # Reset auto-increment counters (PostgreSQL/SQLite compatible)
        print("Resetting auto-increment counters...")
        try:
            # For PostgreSQL
            db.session.execute(db.text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE properties_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE applications_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE tenancy_agreements_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE deposit_transactions_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE deposit_claims_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE notifications_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE conversations_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE messages_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE bookings_id_seq RESTART WITH 1"))
            db.session.execute(db.text("ALTER SEQUENCE viewing_slots_id_seq RESTART WITH 1"))
            db.session.commit()
            print("✅ PostgreSQL auto-increment counters reset!")
        except Exception as pg_error:
            print(f"PostgreSQL reset failed (might be SQLite): {pg_error}")
            try:
                # For SQLite
                db.session.execute(db.text("DELETE FROM sqlite_sequence"))
                db.session.commit()
                print("✅ SQLite auto-increment counters reset!")
            except Exception as sqlite_error:
                print(f"SQLite reset also failed: {sqlite_error}")
                print("⚠️ Auto-increment counters may not be reset - IDs might not start at 1")
        
        print("✅ Database completely wiped clean with reset counters!")

        print("\n🏗️ Creating fresh test data...")

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

        print(f"✅ Created users:")
        print(f"   👤 Landlord: {landlord.email} (ID: {landlord.id})")
        print(f"   👤 Tenant: {tenant.email} (ID: {tenant.id})")

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
            status=PropertyStatus.ACTIVE,  # Set to ACTIVE since it will be rented
            date_added=datetime.utcnow() - timedelta(days=10)
        )
        db.session.add(property_obj)
        db.session.commit()

        print(f"✅ Created property: {property_obj.title} (ID: {property_obj.id})")

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

        print(f"✅ Created application: Approved (ID: {application.id})")

        # Create tenancy agreement
        security_deposit_amount = Decimal(str(property_obj.price * 2.5))  # 2.5 months rent
        
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
            security_deposit=security_deposit_amount,
            lease_start_date=date.today() - timedelta(days=7),  # Started a week ago
            lease_end_date=date.today() + timedelta(days=365),  # Ends in a year
            lease_duration_months=12,
            status='pending_signatures',
            application_id=application.id,
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        db.session.add(agreement)
        db.session.commit()

        print(f"✅ Created tenancy agreement (ID: {agreement.id})")

        # STEP 1: Sign the agreement (both parties)
        print("\n📝 STEP 1: Signing the agreement...")
        
        # Landlord signs first
        agreement.landlord_signed_at = datetime.utcnow() - timedelta(days=8)
        agreement.landlord_signature = "John Landlord"
        
        # Tenant signs second
        agreement.tenant_signed_at = datetime.utcnow() - timedelta(days=7)
        agreement.tenant_signature = "Jane Tenant"
        
        # Update status to signed
        agreement.status = 'signed'
        agreement.fully_signed_at = agreement.tenant_signed_at
        
        db.session.commit()
        print("✅ Agreement signed by both parties")

        # STEP 2: Process website fee payment
        print("\n💳 STEP 2: Processing website fee payment...")
        
        # Simulate website fee payment (usually done by tenant)
        agreement.website_fee_paid = True
        agreement.website_fee_paid_at = datetime.utcnow() - timedelta(days=7)
        agreement.website_fee_amount = Decimal('50.00')  # Standard website fee
        
        db.session.commit()
        print("✅ Website fee payment processed")

        # STEP 3: Create and pay security deposit
        print("\n💰 STEP 3: Creating and paying security deposit...")
        
        # Create deposit transaction
        deposit_transaction = DepositTransaction(
            tenancy_agreement_id=agreement.id,
            property_id=property_obj.id,
            tenant_id=tenant.id,
            landlord_id=landlord.id,
            amount=security_deposit_amount,
            calculation_base=Decimal(str(property_obj.price)),
            calculation_multiplier=Decimal('2.5'),
            status=DepositTransactionStatus.HELD_IN_ESCROW,
            paid_at=datetime.utcnow() - timedelta(days=6),
            payment_method='credit_card',
            payment_intent_id=f'pi_dep_{agreement.id}_{int(datetime.utcnow().timestamp())}',
            escrow_held_at=datetime.utcnow() - timedelta(days=6),
            created_at=datetime.utcnow() - timedelta(days=6),
            updated_at=datetime.utcnow() - timedelta(days=6)
        )
        db.session.add(deposit_transaction)
        db.session.commit()

        print(f"✅ Security deposit transaction created (ID: {deposit_transaction.id})")
        print(f"   💰 Amount: RM {deposit_transaction.amount}")
        print(f"   📅 Paid: {deposit_transaction.paid_at.strftime('%Y-%m-%d')}")

        # STEP 4: Update property status to rented
        print("\n🏠 STEP 4: Updating property status...")
        
        property_obj.status = PropertyStatus.RENTED
        property_obj.current_tenant_id = tenant.id
        
        db.session.commit()
        print("✅ Property status updated to RENTED")

        # STEP 5: Update agreement status to active
        print("\n✅ STEP 5: Activating tenancy agreement...")
        
        agreement.status = 'active'
        agreement.activated_at = datetime.utcnow() - timedelta(days=6)
        
        db.session.commit()
        print("✅ Tenancy agreement activated")

        # STEP 6: Create initial notifications
        print("\n📢 STEP 6: Creating notifications...")
        
        # Notification for landlord
        landlord_notification = Notification(
            recipient_id=landlord.id,
            message=f'Your tenancy agreement for {property_obj.title} is now active. Security deposit of RM {security_deposit_amount} has been received.',
            is_read=False,
            created_at=datetime.utcnow() - timedelta(days=6)
        )
        db.session.add(landlord_notification)
        
        # Notification for tenant
        tenant_notification = Notification(
            recipient_id=tenant.id,
            message=f'Welcome to your new home! Your tenancy agreement for {property_obj.title} is now active. Your security deposit of RM {security_deposit_amount} is safely held in escrow.',
            is_read=False,
            created_at=datetime.utcnow() - timedelta(days=6)
        )
        db.session.add(tenant_notification)
        
        db.session.commit()
        print("✅ Initial notifications created")

        print(f"\n🎉 SUCCESS! Complete tenancy agreement created:")
        print(f"   🧹 Database completely wiped and reset")
        print(f"   👤 Landlord: {landlord.email} (ID: {landlord.id})")
        print(f"   👤 Tenant: {tenant.email} (ID: {tenant.id})")
        print(f"   🏠 Property: {property_obj.title} (ID: {property_obj.id}) - Status: {property_obj.status.value}")
        print(f"   📋 Application: Approved (ID: {application.id})")
        print(f"   📄 Agreement: {agreement.status} (ID: {agreement.id})")
        print(f"   💰 Monthly Rent: RM {agreement.monthly_rent}")
        print(f"   💰 Security Deposit: RM {agreement.security_deposit}")
        print(f"   💳 Website Fee: RM {agreement.website_fee_amount} (Paid)")
        print(f"   🏦 Deposit Transaction: {deposit_transaction.status.value} (ID: {deposit_transaction.id})")
        print(f"   📅 Lease Period: {agreement.lease_start_date} to {agreement.lease_end_date}")
        print()
        print("🎯 READY FOR DEPOSIT MANAGEMENT TESTING:")
        print("   ✅ Agreement is fully signed and active")
        print("   ✅ Security deposit is paid and held in escrow")
        print("   ✅ Property is marked as rented")
        print("   ✅ All payments are completed")
        print()
        print("🔗 DIRECT ACCESS URLS:")
        print(f"   📊 Landlord Dashboard: /landlord/dashboard")
        print(f"   📊 Tenant Dashboard: /tenant/dashboard")
        print(f"   💰 Deposit Management: /deposit/{deposit_transaction.id}/manage")
        print()
        print("🧪 TESTING SCENARIOS:")
        print("   1. End tenancy early to test deposit claims")
        print("   2. Create deposit claims as landlord")
        print("   3. Test tenant response to claims")
        print("   4. Test auto-approval when tenant doesn't respond")
        print("   5. Test fund release and breakdown")
        print()
        print("📝 NOTE: All IDs start from 1 (fresh database)")
        print("=== COMPLETE TENANCY CREATION COMPLETE ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

