#!/usr/bin/env python3
"""
Comprehensive fix script to:
1. Add missing tenant response columns to deposit_claims table
2. Fix foreign key constraint issues in seed data
3. Recreate test tenancy agreement with proper deposit system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import app
from src.models.user import db, User
from src.models.property import Property
from src.models.tenancy_agreement import TenancyAgreement
from src.models.deposit_transaction import DepositTransaction
from src.models.deposit_claim import DepositClaim
from sqlalchemy import text
from datetime import datetime, timedelta
from decimal import Decimal

def add_missing_columns():
    """Add tenant response tracking fields to deposit_claims table"""
    
    print("🔧 Adding missing database columns...")
    
    migrations = [
        ("tenant_response", "VARCHAR(50)", "Tenant's response type (accept/partial_accept/reject)"),
        ("tenant_explanation", "TEXT", "Tenant's explanation for their response"),
        ("tenant_counter_amount", "DECIMAL(10,2)", "Amount tenant agrees to pay (for partial_accept)"),
        ("tenant_responded_at", "DATETIME", "When tenant submitted their response")
    ]
    
    for column_name, column_type, description in migrations:
        try:
            db.engine.execute(text(f'ALTER TABLE deposit_claims ADD COLUMN {column_name} {column_type}'))
            print(f'✅ Added {column_name} column - {description}')
        except Exception as e:
            if 'already exists' in str(e) or 'Duplicate column name' in str(e):
                print(f'⚠️  Column {column_name} already exists, skipping')
            else:
                print(f'❌ Error adding {column_name}: {e}')

def clean_database_safely():
    """Clean database in correct order to avoid foreign key violations"""
    
    print("🧹 Cleaning database safely...")
    
    try:
        # Delete in correct order to avoid foreign key violations
        print("Deleting deposit claims...")
        db.session.query(DepositClaim).delete()
        
        print("Deleting deposit transactions...")
        db.session.query(DepositTransaction).delete()
        
        print("Deleting tenancy agreements...")
        db.session.query(TenancyAgreement).delete()
        
        print("Deleting properties...")
        db.session.query(Property).delete()
        
        # Keep users for login
        print("Keeping users for login...")
        
        db.session.commit()
        print("✅ Database cleaned successfully")
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        db.session.rollback()
        raise

def create_test_data():
    """Create test tenancy agreement with deposit system"""
    
    print("🏠 Creating test data...")
    
    try:
        # Get existing users
        tenant = User.query.filter_by(email='tenant@example.com').first()
        landlord = User.query.filter_by(email='landlord@example.com').first()
        
        if not tenant or not landlord:
            print("❌ Required users not found. Please ensure tenant@example.com and landlord@example.com exist.")
            return False
        
        # Create property
        property = Property(
            title="Test Property for Deposit System",
            location="Kuala Lumpur",
            property_type="Apartment",
            bedrooms=2,
            bathrooms=2,
            size=800,
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('3750.00'),  # 2.5 months rent
            landlord_id=landlord.id,
            status='available',
            description="Test property for deposit management system testing"
        )
        
        db.session.add(property)
        db.session.flush()  # Get property ID
        
        # Create tenancy agreement
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)  # Ending soon for testing
        
        agreement = TenancyAgreement(
            property_id=property.id,
            tenant_id=tenant.id,
            landlord_id=landlord.id,
            monthly_rent=property.monthly_rent,
            deposit_amount=property.deposit_amount,
            lease_start_date=start_date,
            lease_end_date=end_date,
            status='active',
            landlord_signed=True,
            tenant_signed=True,
            website_fee_paid=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(agreement)
        db.session.flush()  # Get agreement ID
        
        # Create deposit transaction
        deposit = DepositTransaction(
            tenancy_agreement_id=agreement.id,
            property_id=property.id,
            tenant_id=tenant.id,
            landlord_id=landlord.id,
            amount=property.deposit_amount,
            status='HELD_IN_ESCROW',
            transaction_type='DEPOSIT_PAYMENT',
            created_at=datetime.utcnow()
        )
        
        db.session.add(deposit)
        db.session.flush()  # Get deposit ID
        
        # Create sample deposit claims for testing
        claims_data = [
            {
                'title': 'cleaning_fees',
                'description': 'too dirty',
                'amount': Decimal('500.00')
            },
            {
                'title': 'repair_damages', 
                'description': 'broke wall',
                'amount': Decimal('1000.00')
            },
            {
                'title': 'missing_items',
                'description': 'vase',
                'amount': Decimal('49.98')
            }
        ]
        
        for claim_data in claims_data:
            claim = DepositClaim(
                deposit_transaction_id=deposit.id,
                tenancy_agreement_id=agreement.id,
                property_id=property.id,
                landlord_id=landlord.id,
                tenant_id=tenant.id,
                claim_type='OTHER',  # Using OTHER since we don't have specific enums
                title=claim_data['title'],
                description=claim_data['description'],
                claimed_amount=claim_data['amount'],
                status='SUBMITTED',
                submitted_at=datetime.utcnow(),
                tenant_response_deadline=datetime.utcnow() + timedelta(days=7),
                created_at=datetime.utcnow()
            )
            
            db.session.add(claim)
        
        db.session.commit()
        
        print(f"✅ Created test data:")
        print(f"   - Property: {property.title}")
        print(f"   - Tenancy Agreement: {agreement.id} (ending {end_date})")
        print(f"   - Deposit Transaction: RM {deposit.amount}")
        print(f"   - Deposit Claims: {len(claims_data)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.session.rollback()
        return False

def main():
    """Main function to run all fixes"""
    
    print("🚀 Starting comprehensive database fix...")
    
    with app.app_context():
        try:
            # Step 1: Add missing columns
            add_missing_columns()
            
            # Step 2: Clean database safely
            clean_database_safely()
            
            # Step 3: Create test data
            if create_test_data():
                print("\n🎉 Database fix completed successfully!")
                print("\n📋 What was fixed:")
                print("   ✅ Added missing tenant response columns")
                print("   ✅ Cleaned database without foreign key violations")
                print("   ✅ Created new test tenancy agreement")
                print("   ✅ Created deposit transaction with sample claims")
                print("\n🔗 You can now:")
                print("   - Log in as tenant@example.com or landlord@example.com")
                print("   - Test the deposit management system")
                print("   - Submit tenant responses to claims")
                return True
            else:
                print("❌ Failed to create test data")
                return False
                
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

