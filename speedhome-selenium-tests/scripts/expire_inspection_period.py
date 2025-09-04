#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Use a reliable, absolute path inside the container
backend_path = '/app'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

dotenv_path = os.path.join(backend_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

try:
    from src.main import app
    from src.models.tenancy_agreement import TenancyAgreement
    from src.models.deposit_transaction import DepositTransaction
    from src.models.user import db

    with app.app_context():
        print("=== EXPIRE INSPECTION PERIOD SCRIPT ===")
        print("Making tenancy end 8+ days ago to expire the 7-day inspection period...")

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

        # Store original dates for reference
        original_start_date = agreement.lease_start_date
        original_end_date = agreement.lease_end_date

        # Set lease end date to 8 days ago (past the 7-day inspection window)
        days_past_inspection = 8
        new_end_date = date.today() - timedelta(days=days_past_inspection)
        agreement.lease_end_date = new_end_date

        # Set lease start date to be 1 year before the end date (realistic lease duration)
        agreement.lease_start_date = new_end_date - timedelta(days=365)

        print(f"\n📝 UPDATING Agreement {agreement.id}:")
        print(f"   New Start: {agreement.lease_start_date}")
        print(f"   New End: {agreement.lease_end_date} ({days_past_inspection} days ago)")

        # Commit the changes
        db.session.commit()
        print("✅ Database changes committed!")

        # Verify the changes were saved
        db.session.refresh(agreement)
        print(f"\n🔍 VERIFICATION - Agreement {agreement.id} after commit:")
        print(f"   Saved Start: {agreement.lease_start_date}")
        print(f"   Saved End: {agreement.lease_end_date}")

        # Check if deposit transaction exists
        deposit_transaction = DepositTransaction.query.filter_by(
            tenancy_agreement_id=agreement.id
        ).first()

        if deposit_transaction:
            print(f"\n💰 DEPOSIT TRANSACTION FOUND:")
            print(f"   Deposit ID: {deposit_transaction.id}")
            print(f"   Amount: RM {deposit_transaction.amount}")
            print(f"   Status: {deposit_transaction.status}")
            
            # Calculate inspection period status manually
            lease_end_date = agreement.lease_end_date
            days_since_end = (date.today() - lease_end_date).days
            inspection_period_active = days_since_end <= 7
            days_remaining = max(0, 7 - days_since_end)
            
            print(f"\n🔍 INSPECTION PERIOD STATUS:")
            print(f"   Lease ended: {lease_end_date} ({days_since_end} days ago)")
            print(f"   Inspection period active: {inspection_period_active}")
            print(f"   Days remaining: {days_remaining}")
            
            if not inspection_period_active:
                print("✅ SUCCESS: 7-day inspection period has EXPIRED!")
                print("   - Claims should now be finalized")
                print("   - Tenant should be able to see and respond to claims")
                print("   - System should handle automatic fund release")
            else:
                print("❌ WARNING: Inspection period is still active")
                print(f"   - Need to set lease end date to {7 + 1} days ago or more")
        else:
            print(f"\n⚠️  WARNING: No deposit transaction found for agreement {agreement.id}")
            print("   You may need to run the create_missing_deposit_transaction script first")

        print(f"\n✅ SUCCESS! Tenancy agreement updated:")
        print(f"   📄 Agreement ID: {agreement.id} ⭐ (USE THIS ID)")
        print(f"   🏠 Property: {agreement.property_address}")
        print(f"   👤 Tenant: {agreement.tenant_full_name}")
        print(f"   👤 Landlord: {agreement.landlord_full_name}")
        print(f"   📅 Original Start Date: {original_start_date}")
        print(f"   📅 Original End Date: {original_end_date}")
        print(f"   📅 New Start Date: {agreement.lease_start_date}")
        print(f"   📅 New End Date: {agreement.lease_end_date} (ENDED {days_past_inspection} DAYS AGO)")
        print(f"   📅 Lease Duration: 1 year (realistic for testing)")
        print(f"   💰 Security Deposit: RM {agreement.security_deposit}")
        print()
        print("🎯 READY FOR TENANT TESTING:")
        print("   1. Log in as tenant")
        print("   2. Navigate to deposit dispute page")
        print("   3. Claims should be visible and respondable")
        print("   4. Test the tenant response workflow")
        print()
        print(f"🔗 DEPOSIT MANAGEMENT URL: http://localhost:5173/deposit/{agreement.id}/manage")
        print()
        print("=== INSPECTION PERIOD EXPIRED ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

