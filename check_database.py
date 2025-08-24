#!/usr/bin/env python3

import sys
import os

# Add the backend path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'speedhome-backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from src.main import app
    from src.models.user import db
    from src.models.tenancy_agreement import TenancyAgreement
    from src.models.deposit_transaction import DepositTransaction
    from src.models.property import Property
    
    with app.app_context():
        print("=== DATABASE CHECK ===")
        
        # Check tenancy agreements
        agreements = TenancyAgreement.query.all()
        print(f"\nTenancy Agreements: {len(agreements)}")
        for a in agreements:
            print(f"  ID: {a.id}, Status: {a.status}, Property: {a.property_address}")
        
        # Check deposits
        deposits = DepositTransaction.query.all()
        print(f"\nDeposit Transactions: {len(deposits)}")
        for d in deposits:
            print(f"  ID: {d.id}, Agreement: {d.tenancy_agreement_id}, Status: {d.status}")
        
        # Check properties
        properties = Property.query.filter_by(status='RENTED').all()
        print(f"\nRented Properties: {len(properties)}")
        for p in properties:
            print(f"  ID: {p.id}, Title: {p.title}, Status: {p.status}")
            
        print("\n=== END CHECK ===")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

