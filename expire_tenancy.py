#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date, timedelta

# Add the backend path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'speedhome-backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from src.main import app
    from src.models.tenancy_agreement import TenancyAgreement
    from src.models.user import db
    
    with app.app_context():
        print("=== EXPIRE TENANCY SCRIPT ===")
        print("Making tenancy agreement end early for deposit testing...")
        
        # Find the most recent active tenancy agreement
        agreement = TenancyAgreement.query.filter(
            TenancyAgreement.status.in_(['active', 'pending_signatures', 'signed'])
        ).order_by(TenancyAgreement.created_at.desc()).first()
        
        if not agreement:
            print("❌ No tenancy agreement found!")
            print("   Make sure you have created a tenancy agreement first.")
            exit(1)
        
        # Store original dates for reference
        original_end_date = agreement.lease_end_date
        
        # Set lease end date to yesterday (making it expired)
        yesterday = date.today() - timedelta(days=1)
        agreement.lease_end_date = yesterday
        
        # Also update the lease start date to be in the past if needed
        if agreement.lease_start_date and agreement.lease_start_date > yesterday:
            agreement.lease_start_date = yesterday - timedelta(days=365)  # 1 year ago
        
        # Commit the changes
        db.session.commit()
        
        print(f"✅ SUCCESS! Tenancy agreement expired:")
        print(f"   📄 Agreement ID: {agreement.id}")
        print(f"   🏠 Property: {agreement.property_address}")
        print(f"   👤 Tenant: {agreement.tenant_full_name}")
        print(f"   👤 Landlord: {agreement.landlord_full_name}")
        print(f"   📅 Original End Date: {original_end_date}")
        print(f"   📅 New End Date: {agreement.lease_end_date} (EXPIRED)")
        print(f"   💰 Security Deposit: RM {agreement.security_deposit}")
        print()
        print("🎯 READY FOR DEPOSIT TESTING:")
        print("   1. Log in as landlord or tenant")
        print("   2. Navigate to deposit management")
        print("   3. You should now see deposit release options!")
        print("   4. Test the deposit release/claim workflow")
        print()
        print("=== EXPIRY COMPLETE ===")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

