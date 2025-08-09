#!/usr/bin/env python3
"""
Test script to verify the Property Status Lifecycle System is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import app, db
from src.models.property import Property, PropertyStatus
from src.models.user import User
from datetime import date, datetime

def test_property_status_system():
    """Test the property status lifecycle system"""
    
    with app.app_context():
        print("🧪 Testing Property Status Lifecycle System")
        print("=" * 50)
        
        try:
            # Create a test user (landlord) if one doesn't exist
            test_user = User.query.filter_by(email='test@landlord.com').first()
            if not test_user:
                test_user = User(
                    username='test_landlord',
                    email='test@landlord.com',
                    first_name='Test',
                    last_name='Landlord',
                    role='landlord',
                    password_hash='test_hash'
                )
                db.session.add(test_user)
                db.session.commit()
                print("✅ Created test landlord user")
            
            # Create a test property
            test_property = Property(
                title='Test Property for Status System',
                location='Test Location',
                price=1500,
                property_type='Apartment',
                furnished='Unfurnished',
                description='Test property for status lifecycle',
                owner_id=test_user.id,
                status=PropertyStatus.ACTIVE  # Test enum assignment
            )
            
            db.session.add(test_property)
            db.session.commit()
            print(f"✅ Created test property with ID: {test_property.id}")
            print(f"   Initial status: {test_property.get_status_display()}")
            
            # Test status transitions
            print("\n🔄 Testing Status Transitions:")
            
            # Test Active → Pending
            if test_property.transition_to_pending():
                print(f"✅ Active → Pending: {test_property.get_status_display()}")
            else:
                print("❌ Failed: Active → Pending")
            
            # Test Pending → Rented
            if test_property.transition_to_rented():
                print(f"✅ Pending → Rented: {test_property.get_status_display()}")
            else:
                print("❌ Failed: Pending → Rented")
            
            # Test Rented → Active (with future availability)
            future_date = date(2025, 12, 31)
            if test_property.transition_to_active(available_from_date=future_date):
                print(f"✅ Rented → Active: {test_property.get_status_display()}")
                print(f"   Available from: {test_property.available_from_date}")
            else:
                print("❌ Failed: Rented → Active")
            
            # Test Active → Inactive
            if test_property.transition_to_inactive():
                print(f"✅ Active → Inactive: {test_property.get_status_display()}")
            else:
                print("❌ Failed: Active → Inactive")
            
            # Test Inactive → Active
            if test_property.transition_to_active():
                print(f"✅ Inactive → Active: {test_property.get_status_display()}")
            else:
                print("❌ Failed: Inactive → Active")
            
            db.session.commit()
            
            # Test helper methods
            print("\n🔍 Testing Helper Methods:")
            print(f"✅ is_available_for_applications(): {test_property.is_available_for_applications()}")
            print(f"✅ is_publicly_visible(): {test_property.is_publicly_visible()}")
            
            # Test to_dict serialization
            print("\n📄 Testing Serialization:")
            property_dict = test_property.to_dict()
            print(f"✅ Status in dict: {property_dict['status']}")
            print(f"✅ Available from in dict: {property_dict['available_from_date']}")
            
            # Test invalid transitions
            print("\n🚫 Testing Invalid Transitions:")
            test_property.status = PropertyStatus.INACTIVE
            if not test_property.can_transition_to(PropertyStatus.PENDING):
                print("✅ Correctly blocked invalid transition: Inactive → Pending")
            else:
                print("❌ Invalid transition was allowed (this should not happen)")
            
            # Clean up
            db.session.delete(test_property)
            db.session.commit()
            print("\n🧹 Cleaned up test data")
            
            print("\n🎉 All Property Status Lifecycle tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if test_property_status_system():
        print("\n✅ Property Status Lifecycle System is working correctly!")
    else:
        print("\n❌ Property Status Lifecycle System has issues!")
        sys.exit(1)

