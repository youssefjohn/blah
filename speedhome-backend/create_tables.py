#!/usr/bin/env python3
"""
Script to create database tables with all required columns.
Run this after deleting the database to ensure all columns exist.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app, db
from src.models.user import User
from src.models.property import Property
from src.models.application import Application
from src.models.tenancy_agreement import TenancyAgreement

def create_all_tables():
    """Create all database tables with proper schema"""
    with app.app_context():
        print("Creating all database tables...")
        
        # Drop all tables first (if they exist)
        db.drop_all()
        print("Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("Created all tables")
        
        # Verify tenancy_agreements table has expires_at column
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns('tenancy_agreements')
        column_names = [col['name'] for col in columns]
        
        if 'expires_at' in column_names:
            print("✅ expires_at column exists in tenancy_agreements table")
        else:
            print("❌ expires_at column missing from tenancy_agreements table")
            
        if 'landlord_withdrawn_at' in column_names:
            print("✅ landlord_withdrawn_at column exists")
        else:
            print("❌ landlord_withdrawn_at column missing")
            
        if 'tenant_withdrawn_at' in column_names:
            print("✅ tenant_withdrawn_at column exists")
        else:
            print("❌ tenant_withdrawn_at column missing")
        
        print(f"Total columns in tenancy_agreements: {len(column_names)}")
        print("Database setup complete!")

if __name__ == '__main__':
    create_all_tables()

