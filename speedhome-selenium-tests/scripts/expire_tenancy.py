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

        # Find ALL tenancy agreements first for debugging
        all_agreements = TenancyAgreement.query.all()
        print(f"Found {len(all_agreements)} total agreements:")
        for i, ag in enumerate(all_agreements):
            print(f"  {i+1}. Agreement {ag.id}: Status={ag.status}, Start={ag.lease_start_date}, End={ag.lease_end_date}")

        # Always target the MOST RECENT agreement regardless of status
        agreement = TenancyAgreement.query.order_by(TenancyAgreement.created_at.desc()).first()

        if not agreement:
            print("❌ No tenancy agreements found at all!")
            exit(1)

        print(f"\n🎯 TARGETING MOST RECENT Agreement {agreement.id}:")
        print(f"   Current Status: {agreement.status}")
        print(f"   Current Start: {agreement.lease_start_date}")
        print(f"   Current End: {agreement.lease_end_date}")
        print(f"   Created At: {agreement.created_at}")

        # Warn if this might not be the expected agreement
        if agreement.id != 1:
            print(f"⚠️  WARNING: Expected agreement ID 1, but found ID {agreement.id}")
            print(f"   This suggests multiple agreements exist in the database")
            print(f"   The seed script may not have wiped the database completely")

        # Store original dates for reference
        original_start_date = agreement.lease_start_date
        original_end_date = agreement.lease_end_date

        # Set lease end date to yesterday (for deposit testing)
        new_end_date = date.today() - timedelta(days=1)
        agreement.lease_end_date = new_end_date

        # Set lease start date to one day before the end date
        agreement.lease_start_date = new_end_date - timedelta(days=1)
        
        # Update status to reflect that tenancy has ended
        original_status = agreement.status
        agreement.status = 'ended'  # Mark as ended since lease date is in the past

        print(f"\n📝 UPDATING Agreement {agreement.id}:")
        print(f"   Original Status: {original_status} → New Status: {agreement.status}")
        print(f"   New Start: {agreement.lease_start_date}")
        print(f"   New End: {agreement.lease_end_date} (yesterday)")Commit the changes
        db.session.commit()
        print("✅ Database changes committed!")

        # Verify the changes were saved
        db.session.refresh(agreement)
        print(f"\n🔍 VERIFICATION - Agreement {agreement.id} after commit:")
        print(f"   Saved Start: {agreement.lease_start_date}")
        print(f"   Saved End: {agreement.lease_end_date}")

        print(f"\n✅ SUCCESS! Tenancy agreement updated:")
        print(f"   📄 Agreement ID: {agreement.id} ⭐ (USE THIS ID)")
        print(f"   🏠 Property: {agreement.property_address}")
        print(f"   👤 Tenant: {agreement.tenant_full_name}")
        print(f"   👤 Landlord: {agreement.landlord_full_name}")
        print(f"   📅 Original Start Date: {original_start_date}")
        print(f"   📅 Original End Date: {original_end_date}")
        print(f"   📅 New Start Date: {agreement.lease_start_date}")
        print(f"   📅 New End Date: {agreement.lease_end_date} (ENDED YESTERDAY)")
        print(f"   📅 Lease Duration: 1 day (for testing)")
        print(f"   💰 Security Deposit: RM {agreement.security_deposit}")
        print()
        print("🎯 READY FOR DEPOSIT TESTING:")
        print("   1. Log in as landlord or tenant")
        print("   2. Navigate to deposit management")
        print("   3. 1-day lease ended yesterday - deposit release should be available!")
        print("   4. Test the deposit release/claim workflow")
        print()
        print(f"🔗 DEPOSIT MANAGEMENT URL: http://localhost:5173/deposit/{agreement.id}/manage")
        print()
        print("=== UPDATE COMPLETE ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()