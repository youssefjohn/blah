#!/usr/bin/env python3
"""
Database Migration Script for Deposit System
Creates all necessary tables for the comprehensive deposit management system
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'speedhome-backend', 'src'))

def create_deposit_tables():
    """Create all deposit-related database tables"""
    
    print("🚀 Deposit System Database Migration")
    print("=" * 50)
    
    try:
        # Import Flask app and database
        from main import app, db
        
        # Import deposit models
        from models.deposit_transaction import DepositTransaction
        from models.deposit_claim import DepositClaim
        from models.deposit_dispute import DepositDispute
        
        with app.app_context():
            print("🏗️  Creating deposit system database tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Successfully created deposit system tables:")
            print("   - deposit_transactions")
            print("   - deposit_claims") 
            print("   - deposit_disputes")
            
            print("\n🧪 Testing deposit models...")
            
            # Test Malaysian deposit calculation
            monthly_rent = 2000.00
            amount, adjustments = DepositTransaction.calculate_deposit_amount(
                monthly_rent=monthly_rent,
                tenant_profile={'employment_type': 'corporate', 'credit_score': 780},
                property_details={'monthly_rent': monthly_rent}
            )
            
            print(f"   ✅ Malaysian deposit calculation - MYR {amount:,.2f} ({adjustments['final_multiplier']} months)")
            
            print("\n🎯 Deposit system database schema is ready!")
            print("✅ Deposit system database migration completed successfully!")
            
            return True
        
    except Exception as e:
        print(f"❌ Error creating deposit tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_deposit_tables()

