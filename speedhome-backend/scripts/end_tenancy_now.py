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
        print("=== END TENANCY NOW SCRIPT ===")
        print("Making tenancy agreement end in the past for testing deposit flow...")

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

        print(f"📋 Found agreement: {agreement.id}")
        print(f"   Original start: {original_start_date}")
        print(f"   Original end: {original_end_date}")

        # Set lease end date to 1 day ago (tenancy has ended)
        new_end_date = date.today() - timedelta(days=1)
        agreement.lease_end_date = new_end_date

        # Set lease start date to be well in the past (1 year lease)
        new_start_date = new_end_date - timedelta(days=365)
        agreement.lease_start_date = new_start_date

        # Commit the changes
        db.session.commit()

        print(f"✅ Updated tenancy agreement:")
        print(f"   New start: {new_start_date}")
        print(f"   New end: {new_end_date} (1 day ago)")
        print(f"   Status: Tenancy has ENDED - 7-day inspection period is active")
        print(f"   Landlord can now inspect property and make deposit claims")
        print(f"   Days remaining in inspection period: 6 days")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

