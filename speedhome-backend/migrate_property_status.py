#!/usr/bin/env python3
"""
Database migration script for Property Status Lifecycle System
Converts existing string status to enum and adds available_from_date column
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.user import db
from src.models.property import Property, PropertyStatus
from flask import Flask
import sqlite3

def create_app():
    """Create Flask app for migration"""
    app = Flask(__name__)
    
    # Use the same database path as the main app
    import os
    db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def migrate_property_status():
    """Migrate property status from string to enum"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting Property Status Migration...")
        
        try:
            # Step 1: Add the new available_from_date column if it doesn't exist
            print("📅 Adding available_from_date column...")
            
            # Use raw SQL to add column since SQLAlchemy might not handle this well
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE properties ADD COLUMN available_from_date DATE"))
                conn.commit()
            print("✅ Added available_from_date column")
            
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("✅ available_from_date column already exists")
            else:
                print(f"⚠️  Error adding column: {e}")
        
        try:
            # Step 2: Update existing status values to ensure they're valid
            print("🔄 Updating existing property statuses...")
            
            # Get all properties and update their status
            properties = Property.query.all()
            updated_count = 0
            
            for prop in properties:
                old_status = prop.status
                
                # Convert string status to enum if needed
                if isinstance(prop.status, str):
                    status_mapping = {
                        'Active': PropertyStatus.ACTIVE,
                        'active': PropertyStatus.ACTIVE,
                        'Pending': PropertyStatus.PENDING,
                        'pending': PropertyStatus.PENDING,
                        'Rented': PropertyStatus.RENTED,
                        'rented': PropertyStatus.RENTED,
                        'Inactive': PropertyStatus.INACTIVE,
                        'inactive': PropertyStatus.INACTIVE,
                        'Hidden': PropertyStatus.INACTIVE,  # Legacy mapping
                        'hidden': PropertyStatus.INACTIVE,  # Legacy mapping
                    }
                    
                    new_status = status_mapping.get(prop.status, PropertyStatus.ACTIVE)
                    prop.status = new_status
                    updated_count += 1
                    
                    print(f"  Property {prop.id}: '{old_status}' → '{new_status.value}'")
            
            # Commit the changes
            db.session.commit()
            print(f"✅ Updated {updated_count} properties")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            return False
        
        print("🎉 Property Status Migration completed successfully!")
        return True

def verify_migration():
    """Verify the migration was successful"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Verifying migration...")
        
        try:
            # Check if we can query properties with the new enum
            properties = Property.query.all()
            status_counts = {}
            
            for prop in properties:
                status = prop.status.value if hasattr(prop.status, 'value') else str(prop.status)
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("📊 Property Status Distribution:")
            for status, count in status_counts.items():
                print(f"  {status}: {count} properties")
            
            # Check if available_from_date column exists
            sample_prop = properties[0] if properties else None
            if sample_prop and hasattr(sample_prop, 'available_from_date'):
                print("✅ available_from_date column is accessible")
            else:
                print("❌ available_from_date column not found")
                return False
            
            print("✅ Migration verification successful!")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Property Status Lifecycle Migration")
    print("=" * 50)
    
    # Run migration
    if migrate_property_status():
        # Verify migration
        if verify_migration():
            print("\n🎯 Migration completed successfully!")
            print("The Property Status Lifecycle System is now ready!")
        else:
            print("\n⚠️  Migration completed but verification failed")
            sys.exit(1)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)

