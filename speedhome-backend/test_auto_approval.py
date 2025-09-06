#!/usr/bin/env python3
"""
Test Auto-Approval Functionality

This script tests if the auto-approval mechanism is working correctly
for deposit claims with expired deadlines.
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
    from src.services.property_lifecycle_service import PropertyLifecycleService
    from src.models.user import db

    with app.app_context():
        print("=== AUTO-APPROVAL TEST ===")
        
        # Find all claims that should be auto-approved
        overdue_claims = DepositClaim.query.filter(
            DepositClaim.status.in_([DepositClaimStatus.SUBMITTED, DepositClaimStatus.TENANT_NOTIFIED]),
            DepositClaim.auto_approve_at < datetime.utcnow()
        ).all()
        
        print(f"Found {len(overdue_claims)} overdue claims:")
        
        for claim in overdue_claims:
            print(f"\nClaim {claim.id}:")
            print(f"  Status: {claim.status.value}")
            print(f"  Auto-approve at: {claim.auto_approve_at}")
            print(f"  Current time: {datetime.utcnow()}")
            print(f"  Is overdue: {claim.auto_approve_at < datetime.utcnow()}")
            print(f"  Can auto-approve: {claim.can_auto_approve()}")
            print(f"  Tenant response deadline: {claim.tenant_response_deadline}")
            print(f"  Is response overdue: {claim.is_response_overdue()}")
            
            # Test auto-approval
            try:
                if claim.can_auto_approve():
                    print(f"  Attempting auto-approval...")
                    result = claim.auto_approve_claim()
                    print(f"  Auto-approval result: {result}")
                    if result:
                        print(f"  ✅ Claim {claim.id} auto-approved successfully")
                        print(f"  New status: {claim.status.value}")
                        print(f"  Approved amount: {claim.approved_amount}")
                    else:
                        print(f"  ❌ Auto-approval failed for claim {claim.id}")
                else:
                    print(f"  ❌ Claim {claim.id} cannot be auto-approved")
            except Exception as e:
                print(f"  ❌ Error during auto-approval: {str(e)}")
        
        # Test the background scheduler method
        print(f"\n=== TESTING BACKGROUND SCHEDULER ===")
        try:
            result = PropertyLifecycleService.check_deposit_claim_deadlines()
            print(f"Background scheduler result: {result}")
        except Exception as e:
            print(f"Background scheduler error: {str(e)}")
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

