#!/usr/bin/env python3
"""
Simple script to create messaging tables manually
"""
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.user import db
from src.models.conversation import Conversation
from src.models.message import Message
from src.main import app

def create_messaging_tables():
    """Create the messaging tables"""
    with app.app_context():
        try:
            # Create the tables
            db.create_all()
            print("✅ Messaging tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'conversations' in tables:
                print("✅ Conversations table created")
            else:
                print("❌ Conversations table not found")
                
            if 'messages' in tables:
                print("✅ Messages table created")
            else:
                print("❌ Messages table not found")
                
            print(f"📊 Total tables in database: {len(tables)}")
            print(f"📋 Tables: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Error creating messaging tables: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    create_messaging_tables()

