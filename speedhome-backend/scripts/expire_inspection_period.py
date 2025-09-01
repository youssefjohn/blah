#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date, timedelta
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
    from src.services.deposit_deadline_service import deposit_deadline_service

    with app.app_context():
        print("=== EXPIRE INSPECTION PERIOD SCRIPT ===")
        print("Making tenancy end 8+ days ago to expire the 7-day inspection period...")

        # Find the most recent active tenancy agreement
        agreement = TenancyAgreement.query.filter(
            TenancyAgreement.status.in_(['active', 'pending_signatures', 'signed'])
        ).order_by(TenancyAgreement.created_at.desc()).first()

        if not agreement:
            print("❌ No tenancy agreement found!")
            print("   Make sure you have created a tenancy agreement first.")
            exit(1)

        # Store original dates for reference
        original_start_date = agreement.lease_start_date
        original_end_date = agreement.lease_end_date

        # Set lease end date to 8 days ago (past the 7-day inspection window)
        days_past_inspection = 8
        new_end_date = date.today() - timedelta(days=days_past_inspection)
        agreement.lease_end_date = new_end_date

        # Set lease start date to be 1 year before the end date
        agreement.lease_start_date = new_end_date - timedelta(days=365)

        # Commit the changes
        db.session.commit()

        # Check inspection status
        inspection_status = deposit_deadline_service.get_inspection_status(agreement)

        print(f"📋 Found agreement: {agreement.id}")
        print(f"   Original start: {original_start_date}")
        print(f"   Original end: {original_end_date}")
        print()
        print("✅ Updated tenancy agreement:")
        print(f"   New start: {agreement.lease_start_date}")
        print(f"   New end: {agreement.lease_end_date} ({days_past_inspection} days ago)")
        print()
        print("🔍 Inspection Period Status:")
        print(f"   Is Active: {inspection_status['is_active']}")
        print(f"   Days Remaining: {inspection_status['days_remaining']}")
        print(f"   Can Add Claims: {inspection_status['can_add_claims']}")
        print()
        if not inspection_status['is_active']:
            print("✅ SUCCESS: 7-day inspection period has EXPIRED!")
            print("   - Claims should now be finalized")
            print("   - Tenant should be able to see and respond to claims")
            print("   - Undisputed balance should be released to tenant")
        else:
            print("❌ ERROR: Inspection period is still active")
        print()
        print("🎯 Next Steps:")
        print("   1. Refresh the tenant's deposit dispute page")
        print("   2. Claims should now be visible to tenant")
        print("   3. Check deposit management page for fund releases")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

