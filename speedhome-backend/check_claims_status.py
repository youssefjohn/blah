#!/usr/bin/env python3
"""
Check Claims Status

This script checks all deposit claims in the database and their current status.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend path
backend_path = '/app'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from dotenv import load_dotenv
load_dotenv()

try:
    from src.main import app
    from src.models.deposit_claim import DepositClaim, DepositClaimStatus
    from src.models.deposit_transaction import DepositTransaction
    from src.models.user import db

    with app.app_context():
        print("=== ALL DEPOSIT CLAIMS STATUS ===")
        
        # Find all claims
        all_claims = DepositClaim.query.all()
        
        print(f"Found {len(all_claims)} total claims:")
        
        for claim in all_claims:
            print(f"\nClaim {claim.id}:")
            print(f"  Status: {claim.status.value if claim.status else 'None'}")
            print(f"  Claimed amount: {claim.claimed_amount}")
            print(f"  Submitted at: {claim.submitted_at}")
            print(f"  Tenant response deadline: {claim.tenant_response_deadline}")
            print(f"  Auto-approve at: {claim.auto_approve_at}")
            print(f"  Current time: {datetime.utcnow()}")
            
            if claim.tenant_response_deadline:
                is_deadline_passed = datetime.utcnow() > claim.tenant_response_deadline
                print(f"  Response deadline passed: {is_deadline_passed}")
            
            if claim.auto_approve_at:
                is_auto_approve_time = datetime.utcnow() > claim.auto_approve_at
                print(f"  Auto-approve time passed: {is_auto_approve_time}")
            
            print(f"  Can auto-approve: {claim.can_auto_approve()}")
            print(f"  Tenant responded at: {claim.tenant_responded_at}")
            print(f"  Tenant response: {claim.tenant_response}")
        
        # Check specific statuses
        submitted_claims = DepositClaim.query.filter(
            DepositClaim.status == DepositClaimStatus.SUBMITTED
        ).all()
        print(f"\nClaims with SUBMITTED status: {len(submitted_claims)}")
        
        tenant_notified_claims = DepositClaim.query.filter(
            DepositClaim.status == DepositClaimStatus.TENANT_NOTIFIED
        ).all()
        print(f"Claims with TENANT_NOTIFIED status: {len(tenant_notified_claims)}")
        
        # Check if any claims have expired deadlines but wrong status
        expired_deadline_claims = DepositClaim.query.filter(
            DepositClaim.tenant_response_deadline < datetime.utcnow()
        ).all()
        print(f"\nClaims with expired response deadlines: {len(expired_deadline_claims)}")
        
        for claim in expired_deadline_claims:
            print(f"  Claim {claim.id}: Status={claim.status.value}, Deadline={claim.tenant_response_deadline}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

