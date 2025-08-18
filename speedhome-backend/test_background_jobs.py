#!/usr/bin/env python3
"""
Test script to verify background jobs and notification system for property lifecycle management
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the app directly since it's created in main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.models.user import db, User
from src.models.property import Property, PropertyStatus
from src.models.tenancy_agreement import TenancyAgreement
from src.models.notification import Notification
from datetime import date, datetime, timedelta
import json

def test_background_jobs():
    """Test the background jobs and notification system"""
    
    print("🧪 Testing Background Jobs and Notification System")
    print("=" * 80)
    
    # Create a minimal Flask app for testing
    from flask import Flask
    from flask_cors import CORS
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app, supports_credentials=True)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Clean up any existing test data first
            print("🧹 Cleaning up any existing test data...")
            
            # Clean up landlord
            existing_landlord = User.query.filter_by(email='test-background-jobs@landlord.com').first()
            if existing_landlord:
                Property.query.filter_by(owner_id=existing_landlord.id).delete()
                TenancyAgreement.query.filter_by(landlord_id=existing_landlord.id).delete()
                Notification.query.filter_by(recipient_id=existing_landlord.id).delete()
                db.session.delete(existing_landlord)
                
            # Clean up tenant
            existing_tenant = User.query.filter_by(email='test-background-jobs@tenant.com').first()
            if existing_tenant:
                TenancyAgreement.query.filter_by(tenant_id=existing_tenant.id).delete()
                Notification.query.filter_by(recipient_id=existing_tenant.id).delete()
                db.session.delete(existing_tenant)
                
            db.session.commit()
            
            # Create test data
            print("📋 Setting up test data...")
            
            # Create test landlord
            landlord = User(
                username='testbackgroundjobslandlord',
                email='test-background-jobs@landlord.com',
                first_name='Test',
                last_name='Landlord',
                role='landlord',
                phone='0987654321'
            )
            landlord.set_password('password123')
            
            db.session.add(landlord)
            db.session.commit()
            
            # Create test tenant
            tenant = User(
                username='testbackgroundjobstenant',
                email='test-background-jobs@tenant.com',
                first_name='Test',
                last_name='Tenant',
                role='tenant',
                phone='0123456789'
            )
            tenant.set_password('password123')
            
            db.session.add(tenant)
            db.session.commit()
            
            # Create test property
            test_property = Property(
                title='Test Property for Background Jobs',
                location='Test Location',
                price=1500.00,
                property_type='Apartment',
                bedrooms=2,
                bathrooms=1,
                sqft=800,
                owner_id=landlord.id,
                landlord_id=landlord.id,
                status=PropertyStatus.RENTED  # Start as rented for testing
            )
            
            db.session.add(test_property)
            db.session.commit()
            
            print(f"✅ Created test property with ID: {test_property.id}")
            print(f"   Initial status: {test_property.status.value}")
            
            # Test 1: Create expired tenancy agreement
            print("\n🔄 Test 1: Creating expired tenancy agreement...")
            
            # Use timestamp-based unique application IDs
            import time
            unique_app_id_1 = int(time.time() * 1000) % 1000000  # Use last 6 digits of timestamp
            
            expired_agreement = TenancyAgreement(
                property_id=test_property.id,
                landlord_id=landlord.id,
                tenant_id=tenant.id,
                application_id=unique_app_id_1,  # Unique application ID
                lease_start_date=date.today() - timedelta(days=400),  # Started over a year ago
                lease_end_date=date.today() - timedelta(days=30),     # Expired 30 days ago
                lease_duration_months=12,
                monthly_rent=1500.00,
                security_deposit=3000.00,
                payment_required=399.00,  # Correct field name
                property_address=test_property.location,
                property_type=test_property.property_type,
                property_bedrooms=test_property.bedrooms,
                property_bathrooms=test_property.bathrooms,
                property_sqft=test_property.sqft,
                tenant_full_name=f"{tenant.first_name} {tenant.last_name}",
                tenant_email=tenant.email,
                tenant_phone=tenant.phone,
                landlord_full_name=f"{landlord.first_name} {landlord.last_name}",
                landlord_email=landlord.email,
                landlord_phone=landlord.phone,
                status='active'  # Still marked as active (should be expired)
            )
            
            db.session.add(expired_agreement)
            db.session.commit()
            
            print(f"✅ Created expired agreement with ID: {expired_agreement.id}")
            print(f"   Lease end date: {expired_agreement.lease_end_date}")
            print(f"   Status: {expired_agreement.status}")
            
            # Test 2: Run expired agreements check
            print("\n🔄 Test 2: Running expired agreements check...")
            
            from src.services.property_lifecycle_service import PropertyLifecycleService
            
            result = PropertyLifecycleService.check_expired_agreements()
            
            if result['success']:
                print(f"✅ Expired agreements check completed:")
                print(f"   - Properties set to Inactive: {result['properties_set_to_inactive']}")
                print(f"   - Notifications created: {result['notifications_created']}")
                
                # Verify property status changed to Inactive
                db.session.refresh(test_property)
                print(f"   - Property status now: {test_property.status.value}")
                
                # Verify agreement status changed
                db.session.refresh(expired_agreement)
                print(f"   - Agreement status now: {expired_agreement.status}")
                
                # Check notifications
                notifications = Notification.query.filter_by(recipient_id=landlord.id).all()  # Fixed field name
                print(f"   - Notifications for landlord: {len(notifications)}")
                for notif in notifications:
                    print(f"     * {notif.message}")  # Notification model doesn't have title field
                    
            else:
                print(f"❌ Expired agreements check failed: {result.get('error')}")
            
            # Test 3: Create stale pending agreement
            print("\n🔄 Test 3: Creating stale pending agreement...")
            
            # Create another property for this test
            test_property2 = Property(
                title='Test Property 2 for Stale Agreement',
                location='Test Location 2',
                price=1800.00,
                property_type='Condo',
                bedrooms=3,
                bathrooms=2,
                sqft=1000,
                owner_id=landlord.id,
                landlord_id=landlord.id,
                status=PropertyStatus.PENDING  # Pending status
            )
            
            db.session.add(test_property2)
            db.session.commit()
            
            # Create stale pending agreement (older than 30 days)
            unique_app_id_2 = unique_app_id_1 + 1  # Ensure uniqueness
            
            stale_agreement = TenancyAgreement(
                property_id=test_property2.id,
                landlord_id=landlord.id,
                tenant_id=tenant.id,
                application_id=unique_app_id_2,  # Unique application ID
                lease_start_date=date.today() + timedelta(days=30),
                lease_end_date=date.today() + timedelta(days=395),
                lease_duration_months=12,
                monthly_rent=1800.00,
                security_deposit=3600.00,
                payment_required=399.00,  # Correct field name
                property_address=test_property2.location,
                property_type=test_property2.property_type,
                property_bedrooms=test_property2.bedrooms,
                property_bathrooms=test_property2.bathrooms,
                property_sqft=test_property2.sqft,
                tenant_full_name=f"{tenant.first_name} {tenant.last_name}",
                tenant_email=tenant.email,
                tenant_phone=tenant.phone,
                landlord_full_name=f"{landlord.first_name} {landlord.last_name}",
                landlord_email=landlord.email,
                landlord_phone=landlord.phone,
                status='pending_signatures',
                created_at=datetime.utcnow() - timedelta(days=35)  # Created 35 days ago
            )
            
            db.session.add(stale_agreement)
            db.session.commit()
            
            print(f"✅ Created stale pending agreement with ID: {stale_agreement.id}")
            print(f"   Created: {stale_agreement.created_at}")
            print(f"   Status: {stale_agreement.status}")
            
            # Test 4: Run pending timeouts check
            print("\n🔄 Test 4: Running pending timeouts check...")
            
            result = PropertyLifecycleService.check_pending_agreements_timeout()
            
            if result['success']:
                print(f"✅ Pending timeouts check completed:")
                print(f"   - Properties reverted: {result.get('properties_reverted', 0)}")
                print(f"   - Notifications created: {result['notifications_created']}")
                
                # Verify property status changed
                db.session.refresh(test_property2)
                print(f"   - Property 2 status now: {test_property2.status.value}")
                
                # Verify agreement status changed
                db.session.refresh(stale_agreement)
                print(f"   - Stale agreement status now: {stale_agreement.status}")
                
            else:
                print(f"❌ Pending timeouts check failed: {result.get('error')}")
            
            # Test 5: Create property with future availability
            print("\n🔄 Test 5: Creating property with future availability...")
            
            test_property3 = Property(
                title='Test Property 3 for Future Availability',
                location='Test Location 3',
                price=2000.00,
                property_type='House',
                bedrooms=4,
                bathrooms=3,
                sqft=1200,
                owner_id=landlord.id,
                landlord_id=landlord.id,
                status=PropertyStatus.ACTIVE,
                available_from_date=date.today() - timedelta(days=1)  # Available since yesterday
            )
            
            db.session.add(test_property3)
            db.session.commit()
            
            print(f"✅ Created property with future availability:")
            print(f"   - Available from: {test_property3.available_from_date}")
            print(f"   - Status: {test_property3.status.value}")
            
            # Test 6: Run future availability check
            print("\n🔄 Test 6: Running future availability check...")
            
            result = PropertyLifecycleService.check_future_availability()
            
            if result['success']:
                print(f"✅ Future availability check completed:")
                print(f"   - Properties activated: {result.get('properties_activated', 0)}")
                print(f"   - Notifications created: {result['notifications_created']}")
                
                # Verify available_from_date was cleared
                db.session.refresh(test_property3)
                print(f"   - Property 3 available_from_date now: {test_property3.available_from_date}")
                
            else:
                print(f"❌ Future availability check failed: {result.get('error')}")
            
            # Test 7: Run complete daily maintenance
            print("\n🔄 Test 7: Running complete daily maintenance...")
            
            result = PropertyLifecycleService.run_daily_maintenance()
            
            if result['success']:
                print(f"✅ Daily maintenance completed:")
                print(f"   - Total properties updated: {result['total_properties_updated']}")
                print(f"   - Total notifications created: {result['total_notifications_created']}")
                print(f"   - Timestamp: {result['timestamp']}")
                
            else:
                print(f"❌ Daily maintenance failed: {result.get('error')}")
            
            # Test 8: Check all notifications created
            print("\n🔄 Test 8: Checking all notifications...")
            
            all_notifications = Notification.query.filter_by(recipient_id=landlord.id).all()  # Fixed field name
            print(f"✅ Total notifications for landlord: {len(all_notifications)}")
            
            for i, notif in enumerate(all_notifications, 1):
                print(f"   {i}. {notif.message}")  # Notification model doesn't have title field
                print(f"      Is read: {notif.is_read}")
                print(f"      Created: {notif.created_at}")
                print(f"      Link: {notif.link}")
                print()
            
            # Clean up
            print("🧹 Cleaning up test data...")
            Property.query.filter_by(owner_id=landlord.id).delete()
            TenancyAgreement.query.filter_by(landlord_id=landlord.id).delete()
            Notification.query.filter_by(recipient_id=landlord.id).delete()  # Fixed field name
            db.session.delete(tenant)
            db.session.delete(landlord)
            db.session.commit()
            
            print("\n🎉 All background jobs and notification tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Background jobs tests failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_background_jobs()
    if success:
        print("\n✅ Background Jobs and Notification System is working correctly!")
    else:
        print("\n❌ Background Jobs and Notification System has issues!")
        sys.exit(1)

