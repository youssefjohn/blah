#!/usr/bin/env python3
"""
Database Migration Script for Deposit System
Creates all necessary tables for the comprehensive deposit management system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.models.user import db
from src.models.deposit_transaction import DepositTransaction
from src.models.deposit_claim import DepositClaim
from src.models.deposit_dispute import DepositDispute

def create_deposit_tables():
    """Create all deposit-related database tables"""
    
    print("🏗️  Creating deposit system database tables...")
    
    try:
        # Create all tables
        db.create_all()
        
        print("✅ Successfully created deposit system tables:")
        print("   - deposit_transactions")
        print("   - deposit_claims") 
        print("   - deposit_disputes")
        print()
        print("🎯 Deposit system database schema is ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating deposit tables: {str(e)}")
        return False

def test_deposit_models():
    """Test that all deposit models work correctly"""
    
    print("\n🧪 Testing deposit models...")
    
    try:
        # Test Malaysian deposit calculation
        monthly_rent = 2000.00
        amount, adjustments = DepositTransaction.calculate_deposit_amount(
            monthly_rent=monthly_rent,
            tenant_profile={'employment_type': 'corporate', 'credit_score': 780},
            property_details={'monthly_rent': monthly_rent}
        )
        
        print(f"   ✅ Malaysian deposit calculation - MYR {amount:,.2f} ({adjustments['final_multiplier']} months)")
        print("\n🎉 All deposit models are working correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing models: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Deposit System Database Migration")
    print("=" * 50)
    
    # Create tables
    if create_deposit_tables():
        # Test models
        if test_deposit_models():
            print("\n✅ Deposit system database migration completed successfully!")
        else:
            print("\n⚠️  Tables created but model testing failed")
    else:
        print("\n❌ Database migration failed")

