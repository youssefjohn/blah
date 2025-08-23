#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta, date
from decimal import Decimal

# Add the backend path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'speedhome-backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from src.main import app
    from src.models.user import db, User
    from src.models.property import Property, PropertyStatus
    from src.models.application import Application
    from src.models.tenancy_agreement import TenancyAgreement
    
    with app.app_context():
        print("=== SIMPLE SEED SCRIPT ===")
        print("Creating test data for agreement stage...")
        
        # Clear existing data
        db.session.query(TenancyAgreement).delete()
        db.session.query(Application).delete()
        db.session.query(Property).delete()
        db.session.query(User).filter(User.email.in_(['landlord@test.com', 'tenant@test.com'])).delete()
        db.session.commit()
        
        # Create landlord
        landlord = User(
            email='landlord@test.com',
            username='landlord',
            password_hash='scrypt:32768:8:1$salt$hash',  # password123
            first_name='John',
            last_name='Landlord',
            phone='+60123456789',
            role='landlord',
            is_verified=True
        )
        db.session.add(landlord)
        
        # Create tenant
        tenant = User(
            email='tenant@test.com',
            username='tenant',
            password_hash='scrypt:32768:8:1$salt$hash',  # password123
            first_name='Jane',
            last_name='Tenant',
            phone='+60123456788',
            role='tenant',
            is_verified=True
        )
        db.session.add(tenant)
        db.session.commit()
        
        # Create property
        property = Property(
            title='Test Property for Deposit System',
            description='A beautiful property for testing the deposit workflow',
            price=1500,
            location='Kuala Lumpur',
            property_type='apartment',
            bedrooms=2,
            bathrooms=2,
            sqft=800,
            owner_id=landlord.id,
            status=PropertyStatus.PENDING,  # Will be PENDING after application approved
            date_added=datetime.utcnow() - timedelta(days=10)
        )
        db.session.add(property)
        db.session.commit()
        
        # Create approved application
        application = Application(
            property_id=property.id,
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
            property_id=property.id,
            property_address=f"{property.title}, {property.location}",
            tenant_id=tenant.id,
            tenant_full_name=f"{tenant.first_name} {tenant.last_name}",
            landlord_id=landlord.id,
            landlord_full_name=f"{landlord.first_name} {landlord.last_name}",
            monthly_rent=Decimal(str(property.price)),
            security_deposit=Decimal(str(property.price * 2.5)),  # 2.5 months
            lease_start_date=date.today() + timedelta(days=7),
            lease_end_date=date.today() + timedelta(days=372),  # ~1 year
            lease_duration_months=12,  # Required field
            status='pending_signatures',  # Not signed yet
            application_id=application.id,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(agreement)
        db.session.commit()
        
        print(f"✅ SUCCESS! Created test data:")
        print(f"   👤 Landlord: {landlord.email} (ID: {landlord.id})")
        print(f"   👤 Tenant: {tenant.email} (ID: {tenant.id})")
        print(f"   🏠 Property: {property.title} (ID: {property.id})")
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
        print("=== SEED COMPLETE ===")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

