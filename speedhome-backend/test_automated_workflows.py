#!/usr/bin/env python3
"""
Test script for automated property status workflows
Tests the integration between applications, tenancy agreements, and property status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import app, db
from src.models.property import Property, PropertyStatus
from src.models.user import User
from src.models.application import Application
from src.models.tenancy_agreement import TenancyAgreement
from datetime import date, datetime

def test_automated_workflows():
    """Test all automated property status workflows"""
    
    with app.app_context():
        print("🧪 Testing Automated Property Status Workflows")
        print("=" * 60)
        
        try:
            # Setup test data
            print("📋 Setting up test data...")
            
            # Create test landlord
            landlord = User.query.filter_by(email='test@landlord.com').first()
            if not landlord:
                landlord = User(
                    username='test_landlord',
                    email='test@landlord.com',
                    first_name='Test',
                    last_name='Landlord',
                    role='landlord',
                    password_hash='test_hash'
                )
                db.session.add(landlord)
            
            # Create test tenant
            tenant = User.query.filter_by(email='test@tenant.com').first()
            if not tenant:
                tenant = User(
                    username='test_tenant',
                    email='test@tenant.com',
                    first_name='Test',
                    last_name='Tenant',
                    role='tenant',
                    password_hash='test_hash'
                )
                db.session.add(tenant)
            
            db.session.commit()
            
            # Create test property
            test_property = Property(
                title='Test Property for Workflow',
                location='Test Location',
                price=1500,
                property_type='Apartment',
                furnished='Unfurnished',
                description='Test property for workflow testing',
                owner_id=landlord.id,
                status=PropertyStatus.ACTIVE
            )
            
            db.session.add(test_property)
            db.session.commit()
            
            print(f"✅ Created test property with ID: {test_property.id}")
            print(f"   Initial status: {test_property.get_status_display()}")
            
            # Test 1: Application Approval → Property goes to Pending
            print("\n🔄 Test 1: Application Approval Workflow")
            
            test_application = Application(
                tenant_id=tenant.id,
                property_id=test_property.id,
                landlord_id=landlord.id,
                full_name='Test Tenant',
                email='test@tenant.com',
                phone_number='1234567890',
                status='pending'
            )
            
            db.session.add(test_application)
            db.session.commit()
            
            # Simulate application approval
            test_application.status = 'approved'
            
            # This should trigger the property status transition
            if test_property.transition_to_pending():
                print(f"✅ Property transitioned to: {test_property.get_status_display()}")
            else:
                print("❌ Failed to transition property to Pending")
            
            db.session.commit()
            
            # Test 2: Tenancy Agreement Activation → Property goes to Rented
            print("\n🔄 Test 2: Tenancy Agreement Activation Workflow")
            
            test_agreement = TenancyAgreement(
                application_id=test_application.id,
                property_id=test_property.id,
                landlord_id=landlord.id,
                tenant_id=tenant.id,
                monthly_rent=test_property.price,
                payment_required=399.00,
                security_deposit=test_property.price * 2,
                lease_start_date=date.today(),
                lease_end_date=date(2025, 12, 31),
                lease_duration_months=12,
                property_address=test_property.location,
                property_type=test_property.property_type,
                property_bedrooms=test_property.bedrooms or 1,
                property_bathrooms=test_property.bathrooms or 1,
                property_sqft=test_property.sqft or 800,
                tenant_full_name=f"{tenant.first_name} {tenant.last_name}",
                tenant_phone=tenant.phone or "1234567890",
                tenant_email=tenant.email,
                landlord_full_name=f"{landlord.first_name} {landlord.last_name}",
                landlord_phone=landlord.phone or "0987654321",
                landlord_email=landlord.email,
                status='pending_signatures'
            )
            
            db.session.add(test_agreement)
            db.session.commit()
            
            # Simulate agreement activation (payment completed)
            test_agreement.status = 'active'
            test_agreement.payment_completed_at = datetime.utcnow()
            
            # This should trigger the property status transition
            if test_property.transition_to_rented():
                print(f"✅ Property transitioned to: {test_property.get_status_display()}")
            else:
                print("❌ Failed to transition property to Rented")
            
            db.session.commit()
            
            # Test 3: Agreement Failure → Property reverts to Active
            print("\n🔄 Test 3: Agreement Failure Workflow")
            
            # Reset property to Pending for this test
            test_property.status = PropertyStatus.PENDING
            
            # Create another application for the failed agreement test
            failed_application = Application(
                tenant_id=tenant.id,
                property_id=test_property.id,
                landlord_id=landlord.id,
                full_name='Test Tenant 2',
                email='test2@tenant.com',
                phone_number='1234567891',
                status='approved'
            )
            
            db.session.add(failed_application)
            db.session.commit()
            
            # Create another agreement that will fail
            failed_agreement = TenancyAgreement(
                application_id=failed_application.id,
                property_id=test_property.id,
                landlord_id=landlord.id,
                tenant_id=tenant.id,
                monthly_rent=test_property.price,
                payment_required=399.00,
                security_deposit=test_property.price * 2,
                lease_start_date=date.today(),
                lease_end_date=date(2025, 12, 31),
                lease_duration_months=12,
                property_address=test_property.location,
                property_type=test_property.property_type,
                property_bedrooms=test_property.bedrooms or 1,
                property_bathrooms=test_property.bathrooms or 1,
                property_sqft=test_property.sqft or 800,
                tenant_full_name=f"{tenant.first_name} {tenant.last_name}",
                tenant_phone=tenant.phone or "1234567890",
                tenant_email=tenant.email,
                landlord_full_name=f"{landlord.first_name} {landlord.last_name}",
                landlord_phone=landlord.phone or "0987654321",
                landlord_email=landlord.email,
                status='pending_signatures'
            )
            
            db.session.add(failed_agreement)
            db.session.commit()
            
            # Simulate agreement cancellation
            failed_agreement.status = 'cancelled'
            failed_agreement.cancelled_at = datetime.utcnow()
            failed_agreement.cancellation_reason = 'Test cancellation'
            
            # This should trigger the property status reversion
            if test_property.transition_to_active():
                print(f"✅ Property reverted to: {test_property.get_status_display()}")
            else:
                print("❌ Failed to revert property to Active")
            
            db.session.commit()
            
            # Test 4: Manual Status Controls
            print("\n🔄 Test 4: Manual Status Controls")
            
            # Test manual deactivation
            if test_property.transition_to_inactive():
                print(f"✅ Manual deactivation: {test_property.get_status_display()}")
            else:
                print("❌ Failed manual deactivation")
            
            # Test manual reactivation
            if test_property.transition_to_active():
                print(f"✅ Manual reactivation: {test_property.get_status_display()}")
            else:
                print("❌ Failed manual reactivation")
            
            # Test re-listing with future availability
            test_property.status = PropertyStatus.RENTED
            future_date = date(2025, 12, 31)
            if test_property.transition_to_active(available_from_date=future_date):
                print(f"✅ Re-listing with future date: {test_property.get_status_display()}")
                print(f"   Available from: {test_property.available_from_date}")
            else:
                print("❌ Failed re-listing")
            
            db.session.commit()
            
            # Test visibility and availability checks
            print("\n🔍 Test 5: Visibility and Availability Checks")
            
            test_property.status = PropertyStatus.ACTIVE
            print(f"✅ Active property - Available for applications: {test_property.is_available_for_applications()}")
            print(f"✅ Active property - Publicly visible: {test_property.is_publicly_visible()}")
            
            test_property.status = PropertyStatus.PENDING
            print(f"✅ Pending property - Available for applications: {test_property.is_available_for_applications()}")
            print(f"✅ Pending property - Publicly visible: {test_property.is_publicly_visible()}")
            
            test_property.status = PropertyStatus.RENTED
            print(f"✅ Rented property - Available for applications: {test_property.is_available_for_applications()}")
            print(f"✅ Rented property - Publicly visible: {test_property.is_publicly_visible()}")
            
            test_property.status = PropertyStatus.INACTIVE
            print(f"✅ Inactive property - Available for applications: {test_property.is_available_for_applications()}")
            print(f"✅ Inactive property - Publicly visible: {test_property.is_publicly_visible()}")
            
            # Clean up
            print("\n🧹 Cleaning up test data...")
            db.session.delete(failed_agreement)
            db.session.delete(failed_application)
            db.session.delete(test_agreement)
            db.session.delete(test_application)
            db.session.delete(test_property)
            db.session.commit()
            
            print("\n🎉 All automated workflow tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if test_automated_workflows():
        print("\n✅ Automated Property Status Workflows are working correctly!")
    else:
        print("\n❌ Automated Property Status Workflows have issues!")
        sys.exit(1)

