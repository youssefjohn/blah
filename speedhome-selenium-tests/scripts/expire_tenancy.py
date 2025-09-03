#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date, timedelta
import random
from dotenv import load_dotenv

# --- FIX: Use a reliable, absolute path inside the container ---
backend_path = '/app'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Load the environment variables from the correct .env file path
dotenv_path = os.path.join(backend_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

try:
    from src.main import app
    from src.models.tenancy_agreement import TenancyAgreement
    from src.models.user import db

    with app.app_context():
        print("=== END TENANCY SOON SCRIPT ===")
        print("Making tenancy agreement end in the near future for testing...")

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

        # Set lease end date to a random day in the past 1-5 days (for deposit testing)
        days_in_past = random.randint(1, 5)
        new_end_date = date.today() - timedelta(days=days_in_past)
        agreement.lease_end_date = new_end_date

        # Also update the lease start date to be in the past if needed
        if agreement.lease_start_date and agreement.lease_start_date > new_end_date:
            agreement.lease_start_date = new_end_date - timedelta(days=365)  # 1 year ago

        # Commit the changes
        db.session.commit()

        print(f"✅ SUCCESS! Tenancy agreement updated:")
        print(f"   📄 Agreement ID: {agreement.id}")
        print(f"   🏠 Property: {agreement.property_address}")
        print(f"   👤 Tenant: {agreement.tenant_full_name}")
        print(f"   👤 Landlord: {agreement.landlord_full_name}")
        print(f"   📅 Original End Date: {original_end_date}")
        print(f"   📅 New End Date: {agreement.lease_end_date} (TENANCY ENDED)")
        print(f"   💰 Security Deposit: RM {agreement.security_deposit}")
        print()
        print("🎯 READY FOR DEPOSIT TESTING:")
        print("   1. Log in as landlord or tenant")
        print("   2. Navigate to deposit management")
        print("   3. Tenancy has ended - deposit release should be available!")
        print("   4. Test the deposit release/claim workflow")
        print()
        print("=== UPDATE COMPLETE ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()