#!/usr/bin/env python3
"""
Migration script to add tenant response fields to deposit_claims table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import app
from src.models.user import db
from sqlalchemy import text

def migrate_tenant_response_fields():
    """Add tenant response tracking fields to deposit_claims table"""
    
    with app.app_context():
        try:
            # Add the new columns to the existing table
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
            
            print('\n🎉 Database migration completed successfully!')
            
        except Exception as e:
            print(f'❌ Migration failed: {e}')
            return False
    
    return True

if __name__ == '__main__':
    migrate_tenant_response_fields()

