#!/usr/bin/env python3

import sys
import os
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv

# Use a reliable, absolute path inside the container
backend_path = '/app'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

dotenv_path = os.path.join(backend_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

try:
    from src.main import app
    from src.models.user import db
    from src.models.tenancy_agreement import TenancyAgreement
    from src.models.deposit_transaction import DepositTransaction, DepositTransactionStatus

    with app.app_context():
        print("=== CREATE MISSING DEPOSIT TRANSACTION SCRIPT ===")
        print("Finding tenancy agreements without deposit transactions...")

        # Find all active tenancy agreements
        agreements = TenancyAgreement.query.filter(
            TenancyAgreement.status.in_(['active', 'signed', 'website_fee_paid'])
        ).all()

        print(f"Found {len(agreements)} tenancy agreements:")
        
        missing_deposits = []
        
        for agreement in agreements:
            # Check if deposit transaction exists
            existing_deposit = DepositTransaction.query.filter_by(
                tenancy_agreement_id=agreement.id
            ).first()
            
            if existing_deposit:
                print(f"  ✅ Agreement {agreement.id}: Has deposit transaction {existing_deposit.id}")
            else:
                print(f"  ❌ Agreement {agreement.id}: Missing deposit transaction")
                missing_deposits.append(agreement)

        if not missing_deposits:
            print("\n🎉 All agreements have deposit transactions!")
            exit(0)

        print(f"\n🔧 Creating {len(missing_deposits)} missing deposit transactions...")

        for agreement in missing_deposits:
            # Calculate deposit amount (2.5 months: 2 security + 0.5 utility)
            monthly_rent = agreement.monthly_rent
            security_deposit = monthly_rent * 2
            utility_deposit = monthly_rent * 0.5
            total_amount = security_deposit + utility_deposit

            # Create deposit transaction
            deposit = DepositTransaction(
                tenancy_agreement_id=agreement.id,
                property_id=agreement.property_id,
                tenant_id=agreement.tenant_id,
                landlord_id=agreement.landlord_id,
                amount=total_amount,
                calculation_base=monthly_rent,
                calculation_multiplier=2.5,
                adjustments={
                    'security_deposit': float(security_deposit),
                    'utility_deposit': float(utility_deposit),
                    'total': float(total_amount)
                },
                status=DepositTransactionStatus.HELD_IN_ESCROW,  # Assume already paid
                payment_method='stripe',
                payment_intent_id=f'pi_test_{agreement.id}_{int(datetime.utcnow().timestamp())}',
                paid_at=datetime.utcnow(),
                escrow_held_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.session.add(deposit)
            
            print(f"  ✅ Created deposit {deposit.id} for agreement {agreement.id}")
            print(f"     Amount: RM {total_amount} (Security: RM {security_deposit} + Utility: RM {utility_deposit})")

        # Commit all changes
        db.session.commit()
        print("\n✅ All deposit transactions created successfully!")

        print(f"\n🎯 SUMMARY:")
        print(f"   📄 Processed {len(agreements)} tenancy agreements")
        print(f"   💰 Created {len(missing_deposits)} deposit transactions")
        print(f"   🏦 All deposits set to HELD_IN_ESCROW status")
        print()
        print("🎯 READY FOR DEPOSIT TESTING:")
        print("   1. Navigate to deposit management pages")
        print("   2. All agreements should now have deposit data")
        print("   3. Test the deposit release/claim workflow")
        print()
        print("=== SCRIPT COMPLETE ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

