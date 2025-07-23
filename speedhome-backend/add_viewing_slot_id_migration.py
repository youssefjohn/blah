#!/usr/bin/env python3
"""
Migration script to add viewing_slot_id column to bookings table
This fixes the database schema mismatch that's causing the booking conflicts error.
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    # Database path
    db_path = 'src/database/app.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"🎯 Using database: {db_path}")
    
    try:
        # Create backup
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"🔄 Creating backup: {backup_path}")
        
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if viewing_slot_id column already exists
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'viewing_slot_id' in columns:
            print("✅ viewing_slot_id column already exists in bookings table")
            conn.close()
            return True
        
        print("📝 Adding viewing_slot_id column to bookings table...")
        
        # Add the viewing_slot_id column
        cursor.execute("""
            ALTER TABLE bookings 
            ADD COLUMN viewing_slot_id INTEGER 
            REFERENCES viewing_slots(id)
        """)
        
        # Create index for performance
        print("📝 Creating index for viewing_slot_id...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bookings_viewing_slot_id 
            ON bookings(viewing_slot_id)
        """)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Migration completed successfully!")
        print("🎉 viewing_slot_id column added to bookings table")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        
        # Restore backup if migration failed
        if os.path.exists(backup_path):
            print(f"🔄 Restoring backup from {backup_path}")
            with open(backup_path, 'rb') as src, open(db_path, 'wb') as dst:
                dst.write(src.read())
            print("✅ Database restored from backup")
        
        return False

if __name__ == "__main__":
    print("🚀 Starting migration to add viewing_slot_id to bookings table...")
    success = run_migration()
    
    if success:
        print("\n🎯 Migration completed successfully!")
        print("📋 Next steps:")
        print("  1. Restart your backend server")
        print("  2. Test the availability system")
        print("  3. The booking conflicts should now be resolved")
    else:
        print("\n❌ Migration failed!")
        print("📋 Please check the error messages above and try again")

