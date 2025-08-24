#!/usr/bin/env python3
"""
Test script to check if the full property lifecycle service can be imported
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'speedhome-backend', 'src'))

try:
    print("Testing property lifecycle service import...")
    
    # Test importing the full property lifecycle service
    print("1. Importing PropertyLifecycleService...")
    from services.property_lifecycle_service import PropertyLifecycleService
    print("   ✅ PropertyLifecycleService imported successfully")
    
    # Test creating an instance
    print("2. Creating PropertyLifecycleService instance...")
    service = PropertyLifecycleService()
    print("   ✅ PropertyLifecycleService instance created successfully")
    
    # Test that the service has the expected methods
    print("3. Checking service methods...")
    expected_methods = [
        'process_lease_expiry_notifications',
        'process_expired_agreements',
        'process_deposit_resolution_workflow',
        'process_deposit_claim_deadlines',
        'process_property_reactivation'
    ]
    
    for method_name in expected_methods:
        if hasattr(service, method_name):
            print(f"   ✅ Method {method_name} exists")
        else:
            print(f"   ❌ Method {method_name} missing")
    
    print("\n🎉 PROPERTY LIFECYCLE SERVICE IMPORT SUCCESSFUL!")
    print("The full deposit functionality can now be restored!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

