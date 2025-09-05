#!/usr/bin/env python3

import sys
import os

# Add the backend path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'speedhome-backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from src.main import app
    
    # Test the route registration
    print("=== TESTING DEPOSIT ROUTES ===")
    
    with app.app_context():
        # Check if the route is registered
        for rule in app.url_map.iter_rules():
            if 'deposit' in rule.rule and 'agreement' in rule.rule:
                print(f"Found route: {rule.rule} -> {rule.endpoint}")
        
        # Test the route directly
        with app.test_client() as client:
            # First, let's see what routes are available
            print("\nAll deposit routes:")
            for rule in app.url_map.iter_rules():
                if 'deposit' in rule.rule:
                    print(f"  {rule.methods} {rule.rule}")
            
            print("\nTesting /api/deposits/agreement/1 route...")
            response = client.get('/api/deposits/agreement/1')
            print(f"Status: {response.status_code}")
            print(f"Response: {response.get_json()}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

