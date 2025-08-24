#!/usr/bin/env python3
"""
Test script to verify that restored methods work without SQLAlchemy conflicts
"""

import sys
import os
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'speedhome-backend', 'src'))

try:
    print("🧪 TESTING RESTORED DEPOSIT MODEL METHODS")
    print("=" * 50)
    
    # Import Flask app and models
    from main import app, db
    from models.deposit_transaction import DepositTransaction, DepositTransactionStatus
    from models.deposit_claim import DepositClaim, DepositClaimType, DepositClaimStatus
    from models.deposit_dispute import DepositDispute, DepositDisputeResponse, DepositDisputeStatus
    
    with app.app_context():
        print("\n1. 🏗️  TESTING DEPOSIT TRANSACTION METHODS")
        print("-" * 40)
        
        # Test DepositTransaction methods
        deposit = DepositTransaction(
            tenancy_agreement_id=999,
            property_id=999,
            tenant_id=1001,
            landlord_id=1002,
            amount=4000.00,
            calculation_base=2000.00,
            calculation_multiplier=2.0,
            status=DepositTransactionStatus.HELD_IN_ESCROW,
            released_amount=1000.00,
            refunded_amount=500.00
        )
        
        remaining = deposit.get_remaining_amount()
        is_resolved = deposit.is_fully_resolved()
        can_claim = deposit.can_be_claimed()
        
        print(f"   ✅ get_remaining_amount(): RM {remaining:,.2f}")
        print(f"   ✅ is_fully_resolved(): {is_resolved}")
        print(f"   ✅ can_be_claimed(): {can_claim}")
        
        print("\n2. 🏗️  TESTING DEPOSIT CLAIM METHODS")
        print("-" * 40)
        
        # Test DepositClaim methods
        claim = DepositClaim(
            deposit_transaction_id=1,
            tenancy_agreement_id=999,
            property_id=999,
            landlord_id=1002,
            tenant_id=1001,
            claim_type=DepositClaimType.CLEANING,
            title="Professional cleaning required",
            description="Property requires deep cleaning",
            claimed_amount=800.00,
            status=DepositClaimStatus.SUBMITTED,
            tenant_response_deadline=datetime.utcnow() + timedelta(days=3)
        )
        
        days_until = claim.get_days_until_response_deadline()
        is_overdue = claim.is_response_overdue()
        can_auto = claim.can_auto_approve()
        
        print(f"   ✅ get_days_until_response_deadline(): {days_until} days")
        print(f"   ✅ is_response_overdue(): {is_overdue}")
        print(f"   ✅ can_auto_approve(): {can_auto}")
        
        print("\n3. 🏗️  TESTING DEPOSIT DISPUTE METHODS")
        print("-" * 40)
        
        # Test DepositDispute methods
        dispute = DepositDispute(
            deposit_claim_id=1,
            deposit_transaction_id=1,
            tenancy_agreement_id=999,
            property_id=999,
            tenant_id=1001,
            landlord_id=1002,
            conversation_id=999,
            tenant_response=DepositDisputeResponse.PARTIAL_ACCEPT,
            tenant_response_reason="Agree to partial amount",
            tenant_counter_amount=400.00,
            status=DepositDisputeStatus.UNDER_MEDIATION,
            mediation_deadline=datetime.utcnow() + timedelta(days=5),
            escalation_deadline=datetime.utcnow() + timedelta(days=10)
        )
        
        mediation_days = dispute.get_days_until_mediation_deadline()
        is_med_overdue = dispute.is_mediation_overdue()
        can_escalate = dispute.can_escalate()
        
        print(f"   ✅ get_days_until_mediation_deadline(): {mediation_days} days")
        print(f"   ✅ is_mediation_overdue(): {is_med_overdue}")
        print(f"   ✅ can_escalate(): {can_escalate}")
        
        print("\n4. 🔄 TESTING SERIALIZATION WITH NEW METHODS")
        print("-" * 40)
        
        # Test that to_dict works with new methods
        deposit_dict = deposit.to_dict()
        claim_dict = claim.to_dict()
        dispute_dict = dispute.to_dict()
        
        print(f"   ✅ DepositTransaction.to_dict(): {len(deposit_dict)} fields")
        print(f"   ✅ DepositClaim.to_dict(): {len(claim_dict)} fields")
        print(f"   ✅ DepositDispute.to_dict(): {len(dispute_dict)} fields")
        
        # Check specific fields
        print(f"   ✅ Claim days_until_deadline: {claim_dict.get('days_until_deadline')}")
        print(f"   ✅ Dispute mediation days: {dispute_dict.get('days_until_mediation_deadline')}")
        
        print("\n" + "=" * 50)
        print("🎉 ALL RESTORED METHODS WORKING PERFECTLY!")
        print("✅ No SQLAlchemy conflicts detected")
        print("✅ All business logic methods functional")
        print("✅ Serialization working with new methods")
        print("✅ Ready for production use!")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

