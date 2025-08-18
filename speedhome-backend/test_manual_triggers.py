#!/usr/bin/env python3
"""
Manual Testing Script for Property Lifecycle System

This script provides a guided workflow to test the complete property lifecycle system,
including manual triggers for expired agreements, pending timeouts, and future availability.

Usage:
    python test_manual_triggers.py

Requirements:
    - Backend server running on localhost:5001
    - Database with test data (properties, users, tenancy agreements)
"""

import requests
import json
import sys
from datetime import datetime, date, timedelta

BASE_URL = "http://localhost:5001"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n🔹 Step {step_num}: {description}")

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message"""
    print(f"ℹ️  {message}")

def make_request(method, endpoint, data=None):
    """Make an HTTP request and return the response"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to backend server. Make sure it's running on localhost:5001")
        return None
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None

def test_server_connection():
    """Test if the backend server is running"""
    print_step(1, "Testing server connection")
    
    response = make_request('GET', '/api/properties')
    if response and response.status_code == 200:
        print_success("Backend server is running and accessible")
        return True
    else:
        print_error("Backend server is not accessible")
        return False

def test_admin_endpoints():
    """Test if admin testing endpoints are available"""
    print_step(2, "Testing admin testing endpoints")
    
    # Test expired check endpoint
    response = make_request('POST', '/api/admin/trigger-expired-check')
    if response and response.status_code == 200:
        print_success("Admin testing endpoints are available")
        result = response.json()
        print_info(f"Expired check result: {result}")
        return True
    else:
        print_error("Admin testing endpoints are not available")
        if response:
            print_error(f"Status: {response.status_code}, Response: {response.text}")
        return False

def create_test_expired_tenancy():
    """Create a test expired tenancy for testing"""
    print_step(3, "Creating test expired tenancy")
    
    # First, get available properties
    response = make_request('GET', '/api/properties')
    if not response or response.status_code != 200:
        print_error("Could not fetch properties")
        return None

    properties_response = response.json()
    if not properties_response or not properties_response.get('data'):
        print_error("No properties found. Please create some test properties first.")
        return None

    properties = properties_response['data']
    # Use the first property
    property_id = properties[0]['id']
    print_info(f"Using property ID: {property_id} - {properties[0].get('title', 'Unknown')}")
    
    # Create test expired tenancy
    response = make_request('POST', '/api/admin/create-test-expired-tenancy', {
        'property_id': property_id
    })
    
    if response and response.status_code == 200:
        result = response.json()
        print_success("Test expired tenancy created successfully")
        print_info(f"Property status: {result['data']['property_status']}")
        print_info(f"Tenancy agreement ID: {result['data']['tenancy_agreement_id']}")
        print_info(f"Lease end date: {result['data']['lease_end_date']}")
        return result['data']
    else:
        print_error("Failed to create test expired tenancy")
        if response:
            print_error(f"Status: {response.status_code}, Response: {response.text}")
        return None

def trigger_expired_check():
    """Trigger the expired agreements check"""
    print_step(4, "Triggering expired agreements check")
    
    response = make_request('POST', '/api/admin/trigger-expired-check')
    if response and response.status_code == 200:
        result = response.json()
        print_success("Expired agreements check completed")
        print_info(f"Result: {result['result']}")
        return result
    else:
        print_error("Failed to trigger expired agreements check")
        if response:
            print_error(f"Status: {response.status_code}, Response: {response.text}")
        return None

def check_property_status(property_id):
    """Check the current status of a property"""
    print_step(5, f"Checking property {property_id} status")
    
    response = make_request('GET', f'/api/admin/property-status/{property_id}')
    if response and response.status_code == 200:
        result = response.json()
        data = result['data']
        print_success("Property status retrieved successfully")
        print_info(f"Property: {data['title']}")
        print_info(f"Status: {data['status']}")
        print_info(f"Available from: {data['available_from_date'] or 'Not set'}")
        print_info(f"Tenancy agreements: {len(data['tenancy_agreements'])}")
        
        for agreement in data['tenancy_agreements']:
            print_info(f"  - Agreement {agreement['id']}: {agreement['status']} "
                      f"({agreement['lease_start_date']} to {agreement['lease_end_date']})")
        
        return data
    else:
        print_error("Failed to get property status")
        if response:
            print_error(f"Status: {response.status_code}, Response: {response.text}")
        return None

def test_other_triggers():
    """Test other manual triggers"""
    print_step(6, "Testing other manual triggers")
    
    # Test pending timeout check
    print_info("Testing pending timeout check...")
    response = make_request('POST', '/api/admin/trigger-pending-timeout')
    if response and response.status_code == 200:
        result = response.json()
        print_success(f"Pending timeout check: {result['result']}")
    else:
        print_error("Pending timeout check failed")
    
    # Test future availability check
    print_info("Testing future availability check...")
    response = make_request('POST', '/api/admin/trigger-future-availability')
    if response and response.status_code == 200:
        result = response.json()
        print_success(f"Future availability check: {result['result']}")
    else:
        print_error("Future availability check failed")
    
    # Test daily maintenance
    print_info("Testing daily maintenance...")
    response = make_request('POST', '/api/admin/trigger-daily-maintenance')
    if response and response.status_code == 200:
        result = response.json()
        print_success(f"Daily maintenance: {result['result']}")
    else:
        print_error("Daily maintenance failed")

def main():
    """Main testing workflow"""
    print_header("Property Lifecycle System - Manual Testing")
    print("This script will test the complete property lifecycle system")
    print("including manual triggers and status transitions.")
    
    # Test server connection
    if not test_server_connection():
        sys.exit(1)
    
    # Test admin endpoints
    if not test_admin_endpoints():
        sys.exit(1)
    
    # Create test data
    test_data = create_test_expired_tenancy()
    if not test_data:
        print_error("Could not create test data. Continuing with existing data...")
        property_id = 1  # Assume property ID 1 exists
    else:
        property_id = test_data['property_id']
    
    # Trigger expired check
    trigger_result = trigger_expired_check()
    
    # Check property status after trigger
    final_status = check_property_status(property_id)
    
    # Test other triggers
    test_other_triggers()
    
    # Summary
    print_header("Testing Summary")
    if trigger_result and final_status:
        print_success("All tests completed successfully!")
        print_info("Expected behavior:")
        print_info("1. Property should have changed from 'rented' to 'inactive' status")
        print_info("2. Landlord should receive notification about tenancy ending")
        print_info("3. Property should be hidden from public listings")
        print_info("4. Landlord can manually re-activate the property when ready")
        
        if final_status['status'] == 'inactive':
            print_success("✅ Property status correctly changed to 'inactive'")
        else:
            print_error(f"❌ Property status is '{final_status['status']}', expected 'inactive'")
    else:
        print_error("Some tests failed. Please check the output above.")
    
    print("\n🎯 Next steps:")
    print("1. Check your landlord dashboard to see the property status change")
    print("2. Look for the 'Re-activate Listing' button on inactive properties")
    print("3. Test the manual re-activation workflow")
    print("4. Verify notifications were created for the landlord")

if __name__ == "__main__":
    main()

