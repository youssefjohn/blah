#!/usr/bin/env python3
"""
Expire Tenant Response Window Script

This script manually expires the tenant's 7-day response window for deposit claims,
triggering auto-approval of landlord claims when tenants don't respond.

Usage: python expire_tenant_response_window.py
"""

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
    from src.models.deposit_claim import DepositClaim, DepositClaimStatus
    from src.models.deposit_transaction import DepositTransaction
    from src.models.tenancy_agreement import TenancyAgreement
    from src.models.property import Property
    from src.models.user import db

    with app.app_context():
        print("=== EXPIRE TENANT RESPONSE WINDOW SCRIPT ===")
        print("Making tenant response deadline expire for testing auto-approval...")

        # Find ALL deposit claims first for debugging
        all_claims = DepositClaim.query.all()
        print(f"Found {len(all_claims)} total deposit claims:")
        for i, claim in enumerate(all_claims):
            print(f"  {i+1}. Claim {claim.id}: Status={claim.status.value if claim.status else 'None'}")
            print(f"      Submitted: {claim.submitted_at}")
            print(f"      Response Deadline: {claim.tenant_response_deadline}")
            print(f"      Auto-approve At: {claim.auto_approve_at}")
            print(f"      Tenant Responded: {claim.tenant_responded_at}")

        # Find claims that are submitted and waiting for tenant response
        submitted_claims = DepositClaim.query.filter(
            DepositClaim.status.in_([DepositClaimStatus.SUBMITTED, DepositClaimStatus.TENANT_NOTIFIED])
        ).all()

        if not submitted_claims:
            print("❌ No submitted claims found waiting for tenant response!")
            print("\n💡 To test this script:")
            print("   1. Create a tenancy agreement with deposit")
            print("   2. End the tenancy (using expire_tenancy.py)")
            print("   3. Create a deposit claim as landlord")
            print("   4. Run this script to expire the tenant response window")
            exit(1)

        print(f"\n🎯 Found {len(submitted_claims)} submitted claims waiting for tenant response")

        # Always target the MOST RECENT submitted claim
        claim = submitted_claims[-1]  # Last in list = most recent

        print(f"\n🎯 TARGETING MOST RECENT Claim {claim.id}:")
        print(f"   Current Status: {claim.status.value}")
        print(f"   Submitted At: {claim.submitted_at}")
        print(f"   Current Response Deadline: {claim.tenant_response_deadline}")
        print(f"   Current Auto-approve At: {claim.auto_approve_at}")
        print(f"   Claimed Amount: MYR {claim.claimed_amount}")
        print(f"   Claim Type: {claim.claim_type.value}")

        # Warn if this might not be the expected claim
        if len(submitted_claims) > 1:
            print(f"⚠️  WARNING: Found {len(submitted_claims)} submitted claims")
            print(f"   Targeting the most recent one (ID {claim.id})")

        # Set the response deadline and auto-approve time to the past
        past_time = datetime.utcnow() - timedelta(hours=1)  # 1 hour ago
        
        print(f"\n🔄 Setting response deadline to past time: {past_time}")
        
        # Update the claim deadlines
        claim.tenant_response_deadline = past_time
        claim.auto_approve_at = past_time
        
        # Commit the changes
        db.session.commit()
        
        print(f"✅ Successfully expired tenant response window for claim {claim.id}")
        print(f"   New Response Deadline: {claim.tenant_response_deadline}")
        print(f"   New Auto-approve At: {claim.auto_approve_at}")
        
        print(f"\n🎉 SCRIPT COMPLETED SUCCESSFULLY!")
        print(f"📋 What happens next:")
        print(f"   1. The background scheduler (runs every 10 minutes) will detect this expired claim")
        print(f"   2. The claim will be auto-approved for the full claimed amount")
        print(f"   3. Both landlord and tenant will receive notifications")
        print(f"   4. The deposit will be processed according to the approved claim")
        
        print(f"\n⏰ Expected behavior when tenant doesn't respond:")
        print(f"   - Claim status changes to: RESOLVED")
        print(f"   - Approved amount: MYR {claim.claimed_amount} (full claim)")
        print(f"   - Resolution method: Auto-approved due to no tenant response")
        print(f"   - Landlord gets: MYR {claim.claimed_amount}")
        print(f"   - Tenant gets: Remaining deposit (if any)")
        
        print(f"\n🔍 To verify the auto-approval:")
        print(f"   1. Wait for next background scheduler run (max 10 minutes)")
        print(f"   2. Check the claim status in the database or admin panel")
        print(f"   3. Look for notifications sent to both parties")
        print(f"   4. Check the deposit transaction for fund allocation")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

