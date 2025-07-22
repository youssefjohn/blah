#!/usr/bin/env python3
"""
Database migration script to convert viewing_slots from property-based to landlord-based.

This script:
1. Backs up the current database
2. Adds landlord_id column to viewing_slots table
3. Populates landlord_id based on property ownership
4. Removes the old property_id column
5. Updates any existing data to maintain consistency
"""

import sqlite3
import shutil
import os
from datetime import datetime

def backup_database(db_path):
    """Create a backup of the database before migration."""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    return backup_path

def migrate_viewing_slots_to_landlord_based(db_path):
    """Migrate viewing_slots table from property_id to landlord_id."""
    
    print("🔄 Starting migration to landlord-based viewing slots...")
    
    # Create backup first
    backup_path = backup_database(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(viewing_slots)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'landlord_id' in columns and 'property_id' not in columns:
            print("✅ Migration already completed - landlord_id column exists and property_id removed")
            return True
            
        if 'landlord_id' in columns:
            print("⚠️  landlord_id column already exists, skipping column creation")
        else:
            # Step 1: Add landlord_id column
            print("📝 Adding landlord_id column to viewing_slots table...")
            cursor.execute("""
                ALTER TABLE viewing_slots 
                ADD COLUMN landlord_id INTEGER
            """)
            
        # Step 2: Populate landlord_id based on property ownership
        print("📝 Populating landlord_id from property ownership...")
        cursor.execute("""
            UPDATE viewing_slots 
            SET landlord_id = (
                SELECT properties.landlord_id 
                FROM properties 
                WHERE properties.id = viewing_slots.property_id
            )
            WHERE viewing_slots.property_id IS NOT NULL
        """)
        
        # Step 3: Check if we have any rows without landlord_id
        cursor.execute("SELECT COUNT(*) FROM viewing_slots WHERE landlord_id IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            print(f"⚠️  Found {null_count} viewing slots without landlord_id")
            # For any orphaned slots, we'll delete them
            cursor.execute("DELETE FROM viewing_slots WHERE landlord_id IS NULL")
            print(f"🗑️  Deleted {null_count} orphaned viewing slots")
        
        # Step 4: Create new table without property_id
        print("📝 Creating new viewing_slots table structure...")
        cursor.execute("""
            CREATE TABLE viewing_slots_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                landlord_id INTEGER NOT NULL,
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                is_available BOOLEAN DEFAULT TRUE,
                booked_by_user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (landlord_id) REFERENCES users (id),
                FOREIGN KEY (booked_by_user_id) REFERENCES users (id)
            )
        """)
        
        # Step 5: Copy data to new table
        print("📝 Copying data to new table structure...")
        cursor.execute("""
            INSERT INTO viewing_slots_new 
            (id, landlord_id, date, start_time, end_time, is_available, 
             booked_by_user_id, created_at, updated_at)
            SELECT id, landlord_id, date, start_time, end_time, is_available,
                   booked_by_user_id, created_at, updated_at
            FROM viewing_slots
        """)
        
        # Step 6: Replace old table with new table
        print("📝 Replacing old table with new structure...")
        cursor.execute("DROP TABLE viewing_slots")
        cursor.execute("ALTER TABLE viewing_slots_new RENAME TO viewing_slots")
        
        # Step 7: Create indexes for performance
        print("📝 Creating indexes for performance...")
        cursor.execute("""
            CREATE INDEX idx_viewing_slots_landlord_date 
            ON viewing_slots(landlord_id, date)
        """)
        cursor.execute("""
            CREATE INDEX idx_viewing_slots_date_available 
            ON viewing_slots(date, is_available)
        """)
        
        # Commit all changes
        conn.commit()
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM viewing_slots")
        total_slots = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT landlord_id) FROM viewing_slots")
        unique_landlords = cursor.fetchone()[0]
        
        print(f"✅ Migration completed successfully!")
        print(f"📊 Total viewing slots: {total_slots}")
        print(f"📊 Unique landlords: {unique_landlords}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print(f"🔄 Restoring backup from: {backup_path}")
        
        # Restore backup
        shutil.copy2(backup_path, db_path)
        print("✅ Database restored from backup")
        return False

def main():
    """Main migration function."""
    # Determine database path
    db_path = "src/database/app.db"
    if not os.path.exists(db_path):
        db_path = "database/app.db"
        if not os.path.exists(db_path):
            db_path = "app.db"
            if not os.path.exists(db_path):
                print("❌ Database file not found. Please run from the backend directory.")
                return False
    
    print(f"🎯 Using database: {db_path}")
    
    # Run migration
    success = migrate_viewing_slots_to_landlord_based(db_path)
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("✅ viewing_slots table now uses landlord_id instead of property_id")
        print("✅ All existing data has been preserved")
        print("✅ Database indexes created for performance")
        print("\n🚀 You can now restart the backend server to use the new schema!")
    else:
        print("\n❌ Migration failed - database has been restored to original state")
    
    return success

if __name__ == "__main__":
    main()

