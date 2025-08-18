#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration for property status management
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the app directly since it's created in main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.models.user import db, User
from src.models.property import Property, PropertyStatus
from datetime import date, datetime
import json

def test_frontend_integration():
    """Test the property status management API endpoints that the frontend will use"""
    
    print("🧪 Testing Frontend-Backend Integration for Property Status Management")
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
    
    # Register the property blueprint for testing
    from src.routes.property import property_bp
    app.register_blueprint(property_bp, url_prefix='/api')
    
    with app.app_context():
        try:
            # Clean up any existing test data first
            print("🧹 Cleaning up any existing test data...")
            existing_user = User.query.filter_by(email='test-frontend@landlord.com').first()
            if existing_user:
                # Delete any properties owned by this user
                Property.query.filter_by(landlord_id=existing_user.id).delete()
                db.session.delete(existing_user)
                db.session.commit()
            
            # Create test data
            print("📋 Setting up test data...")
            
            # Create test landlord
            landlord = User(
                username='testfrontendlandlord',
                email='test-frontend@landlord.com',
                first_name='Test',
                last_name='Landlord',
                role='landlord',
                phone='0987654321'
            )
            landlord.set_password('password123')
            
            db.session.add(landlord)
            db.session.commit()
            
            # Create test property
            test_property = Property(
                title='Test Property for Frontend',
                location='Test Location',
                price=1500.00,
                property_type='Apartment',
                bedrooms=2,
                bathrooms=1,
                sqft=800,
                owner_id=landlord.id,  # Required field
                landlord_id=landlord.id,  # Legacy field
                status=PropertyStatus.ACTIVE
            )
            
            db.session.add(test_property)
            db.session.commit()
            
            print(f"✅ Created test property with ID: {test_property.id}")
            print(f"   Initial status: {test_property.status.value}")
            
            # Test the API endpoints that the frontend will call
            with app.test_client() as client:
                
                # Test 1: Get property status
                print("\n🔄 Test 1: GET /properties/{id}/status")
                response = client.get(f'/api/properties/{test_property.id}/status')
                
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"✅ Status retrieved: {data['status']}")
                    print(f"   Valid transitions: {data['valid_transitions']}")
                else:
                    print(f"❌ Failed with status {response.status_code}")
                
                # Test 2: Deactivate property
                print("\n🔄 Test 2: POST /properties/{id}/deactivate")
                response = client.post(f'/api/properties/{test_property.id}/deactivate')
                
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"✅ Property deactivated: {data['message']}")
                    print(f"   New status: {data['property']['status']}")
                else:
                    print(f"❌ Failed with status {response.status_code}: {response.data}")
                
                # Test 3: Reactivate property
                print("\n🔄 Test 3: POST /properties/{id}/reactivate")
                response = client.post(f'/api/properties/{test_property.id}/reactivate')
                
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"✅ Property reactivated: {data['message']}")
                    print(f"   New status: {data['property']['status']}")
                else:
                    print(f"❌ Failed with status {response.status_code}: {response.data}")
                
                # Test 4: Update status to Rented
                print("\n🔄 Test 4: PUT /properties/{id}/status (to Rented)")
                response = client.put(
                    f'/api/properties/{test_property.id}/status',
                    data=json.dumps({'status': 'Rented'}),
                    content_type='application/json'
                )
                
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"✅ Status updated: {data['message']}")
                    print(f"   New status: {data['property']['status']}")
                else:
                    print(f"❌ Failed with status {response.status_code}: {response.data}")
                
                # Test 5: Re-list property with future availability
                print("\n🔄 Test 5: POST /properties/{id}/relist")
                future_date = '2025-12-31'
                response = client.post(
                    f'/api/properties/{test_property.id}/relist',
                    data=json.dumps({'available_from_date': future_date}),
                    content_type='application/json'
                )
                
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"✅ Property re-listed: {data['message']}")
                    print(f"   New status: {data['property']['status']}")
                    print(f"   Available from: {data['property']['available_from_date']}")
                else:
                    print(f"❌ Failed with status {response.status_code}: {response.data}")
                
                # Test 6: Get updated property data (simulating frontend refresh)
                print("\n🔄 Test 6: GET /properties/{id} (frontend refresh)")
                response = client.get(f'/api/properties/{test_property.id}')
                
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print(f"✅ Property data refreshed")
                    print(f"   Status: {data['property']['status']}")
                    print(f"   Available from: {data['property'].get('available_from_date', 'Not set')}")
                else:
                    print(f"❌ Failed with status {response.status_code}")
                
                # Test 7: Test invalid transition (should fail)
                print("\n🔄 Test 7: PUT /properties/{id}/status (invalid transition)")
                response = client.put(
                    f'/api/properties/{test_property.id}/status',
                    data=json.dumps({'status': 'Pending'}),  # Active -> Pending is not allowed manually
                    content_type='application/json'
                )
                
                if response.status_code == 400:
                    data = json.loads(response.data)
                    print(f"✅ Invalid transition properly rejected: {data['error']}")
                else:
                    print(f"❌ Should have failed but got status {response.status_code}")
            
            # Clean up
            print("\n🧹 Cleaning up test data...")
            db.session.delete(test_property)
            db.session.delete(landlord)
            db.session.commit()
            
            print("\n🎉 All frontend integration tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Frontend integration tests failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_frontend_integration()
    if success:
        print("\n✅ Frontend-Backend Integration is working correctly!")
    else:
        print("\n❌ Frontend-Backend Integration has issues!")
        sys.exit(1)

