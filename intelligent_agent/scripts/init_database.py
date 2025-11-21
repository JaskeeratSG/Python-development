#!/usr/bin/env python3
"""
Database initialization script for thread persistence.

This script sets up the PostgreSQL database and tables required for
LangGraph checkpoint persistence.

Usage:
    python scripts/init_database.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database import create_checkpointer, DATABASE_URL, is_database_configured
from dotenv import load_dotenv

load_dotenv()


def init_database():
    """Initialize the database for thread persistence."""
    print("🔧 Initializing database for thread persistence...")
    print("=" * 60)
    
    # Check if database is configured
    if not is_database_configured():
        print("⚠️  DATABASE_URL not configured in environment variables.")
        print("\nTo set up database persistence:")
        print("1. Set DATABASE_URL in your .env file:")
        print("   DATABASE_URL=postgresql://user:password@localhost:5432/intelligent_agent_db")
        print("\n2. Or export it:")
        print("   export DATABASE_URL=postgresql://user:password@localhost:5432/intelligent_agent_db")
        print("\n3. For SQLite (development only):")
        print("   DATABASE_URL=sqlite:///./threads.db")
        print("\n⚠️  Falling back to in-memory storage (threads won't persist).")
        return False
    
    try:
        print(f"📊 Database URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
        
        # Create checkpointer (this will also initialize tables)
        checkpointer = create_checkpointer()
        
        # Check if it's actually a database checkpointer
        from langgraph.checkpoint.postgres import PostgresSaver
        if isinstance(checkpointer, PostgresSaver):
            print("✅ Database tables initialized successfully!")
            print("\n📝 Database is ready for thread persistence.")
            print("   Threads will now persist across application restarts.")
            return True
        else:
            print("⚠️  Using in-memory checkpointer (threads won't persist).")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check database credentials")
        print("3. Verify database exists:")
        print("   CREATE DATABASE intelligent_agent_db;")
        print("4. Check network connectivity to database server")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)





