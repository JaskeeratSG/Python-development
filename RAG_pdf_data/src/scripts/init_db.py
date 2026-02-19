"""Create database tables. Run from project root: python scripts/init_db.py"""

import sys
from pathlib import Path

# Add project root so `app` is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import DATABASE_URL
from app.db import DOCUMENTS_TABLE, init_db


def main():
    if not DATABASE_URL or not DATABASE_URL.strip().startswith("postgresql"):
        print("DATABASE_URL is not set or not PostgreSQL. Skipping init.")
        sys.exit(0)
    try:
        init_db()
        print(f"✅ Table '{DOCUMENTS_TABLE}' created or already exists.")
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
