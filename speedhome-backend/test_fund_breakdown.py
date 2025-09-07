#!/usr/bin/env python3
"""
Test Fund Breakdown Calculation

This script tests the fund breakdown calculation for deposits with claims.
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
    from src.services.fund_release_service import FundReleaseService
    from src.models.user import db

    with app.app_context():
        print("=== FUND BREAKDOWN TEST ===")
        
        # Find all deposit transactions
        transactions = DepositTransaction.query.all()
        
        print(f"Found {len(transactions)} deposit transactions:")
        
        for transaction in transactions:
            print(f"\nTransaction {transaction.id}:")
            print(f"  Amount: {transaction.amount}")
            print(f"  Status: {transaction.status.value if transaction.status else 'None'}")
            print(f"  Released amount: {transaction.released_amount}")
            print(f"  Refunded amount: {transaction.refunded_amount}")
            
            # Get claims for this transaction
            claims = DepositClaim.query.filter_by(deposit_transaction_id=transaction.id).all()
            print(f"  Claims: {len(claims)}")
            
            for claim in claims:
                print(f"    Claim {claim.id}: Status={claim.status.value if claim.status else 'None'}, Amount={claim.claimed_amount}")
            
            # Get fund breakdown
            try:
                breakdown = FundReleaseService.get_deposit_breakdown(transaction)
                if breakdown:
                    print(f"  Fund Breakdown:")
                    print(f"    Total deposit: {breakdown.get('total_deposit', 0)}")
                    print(f"    Released to landlord: {breakdown.get('released_to_landlord', 0)}")
                    print(f"    Refunded to tenant: {breakdown.get('refunded_to_tenant', 0)}")
                    print(f"    Remaining in escrow: {breakdown.get('remaining_in_escrow', 0)}")
                    print(f"    Accepted amount: {breakdown.get('accepted_amount', 0)}")
                    print(f"    Status: {breakdown.get('status', 'unknown')}")
                else:
                    print(f"  ❌ Failed to get fund breakdown")
            except Exception as e:
                print(f"  ❌ Error getting fund breakdown: {str(e)}")
                import traceback
                traceback.print_exc()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

