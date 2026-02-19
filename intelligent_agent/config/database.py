"""Database configuration for thread persistence."""

import os
from typing import Optional, Union
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

# Database URL from environment (.env file)
DATABASE_URL = os.getenv("DATABASE_URL")

# Global variable to keep context manager alive
_checkpointer_context = None


def create_checkpointer() -> Union[PostgresSaver, MemorySaver]:
    """
    Create a checkpointer for LangGraph state persistence.
    
    Returns:
        PostgresSaver if DATABASE_URL is configured, otherwise MemorySaver
    """
    global _checkpointer_context
    
    # Check if DATABASE_URL is set and not empty
    db_url = os.getenv("DATABASE_URL", "").strip()
    
    if not db_url:
        print("⚠️  DATABASE_URL not set. Using in-memory checkpointer (threads won't persist across restarts).")
        return MemorySaver()
    
    try:
        # Create PostgreSQL checkpointer (from_conn_string returns a context manager)
        # Store the context manager globally to keep it alive
        _checkpointer_context = PostgresSaver.from_conn_string(db_url)
        checkpointer = _checkpointer_context.__enter__()
        
        # Initialize tables if they don't exist
        checkpointer.setup()
        
        print(f"✅ Database checkpointer initialized with: {db_url.split('@')[-1] if '@' in db_url else 'database'}")
        return checkpointer
        
    except Exception as e:
        print(f"⚠️  Failed to initialize database checkpointer: {e}")
        print("⚠️  Falling back to in-memory checkpointer.")
        import traceback
        traceback.print_exc()
        return MemorySaver()


def get_database_url() -> Optional[str]:
    """Get the database URL from environment."""
    return DATABASE_URL


def is_database_configured() -> bool:
    """Check if database is properly configured."""
    db_url = os.getenv("DATABASE_URL", "").strip()
    return bool(db_url and db_url != "")

