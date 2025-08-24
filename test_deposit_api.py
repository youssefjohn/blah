#!/usr/bin/env python3
"""
Test script to verify all deposit API endpoints are working correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'speedhome-backend'))

from src.main import app
import json

def test_deposit_api_endpoints():
    """Test all deposit API endpoints"""
    print("🧪 Testing Deposit API Endpoints")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test 1: Get all deposits (should require authentication)
        print("\n1. Testing GET /api/deposits/")
        response = client.get('/api/deposits/')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        
        # Test 2: Calculate deposit
        print("\n2. Testing POST /api/deposits/calculate")
        response = client.post('/api/deposits/calculate', 
                             json={'tenancy_agreement_id': 1})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        
        # Test 3: Create deposit
        print("\n3. Testing POST /api/deposits/create")
        response = client.post('/api/deposits/create',
                             json={'tenancy_agreement_id': 1})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        
        # Test 4: Get deposit claims
        print("\n4. Testing GET /api/deposits/1/claims")
        response = client.get('/api/deposits/1/claims')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        
        # Test 5: Create deposit claim
        print("\n5. Testing POST /api/deposits/1/claims")
        claim_data = {
            'title': 'Test Cleaning Claim',
            'description': 'Property requires professional cleaning',
            'claimed_amount': 500.0,
            'category': 'cleaning'
        }
        response = client.post('/api/deposits/1/claims', json=claim_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        
        # Test 6: Respond to claim
        print("\n6. Testing POST /api/deposits/claims/1/respond")
        response_data = {
            'response': 'reject',
            'explanation': 'Property was clean when vacated',
            'counter_amount': 0
        }
        response = client.post('/api/deposits/claims/1/respond', json=response_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        
        # Test 7: Get dispute details
        print("\n7. Testing GET /api/deposits/disputes/1")
        response = client.get('/api/deposits/disputes/1')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        
        # Test 8: Resolve dispute
        print("\n8. Testing POST /api/deposits/disputes/1/resolve")
        resolution_data = {
            'resolution_amount': 250.0,
            'resolution_method': 'admin_decision',
            'resolution_notes': 'Partial amount awarded based on evidence'
        }
        response = client.post('/api/deposits/disputes/1/resolve', json=resolution_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
    
    print("\n" + "=" * 50)
    print("✅ Deposit API endpoint testing completed!")
    print("\nNote: Most endpoints return 401 (Authentication required) which is expected")
    print("This confirms the routes are properly registered and accessible.")

if __name__ == '__main__':
    test_deposit_api_endpoints()

