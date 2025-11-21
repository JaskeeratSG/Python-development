"""Run the FastAPI server for the intelligent agent API."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn

if __name__ == "__main__":
    # Use import string for reload to work properly
    uvicorn.run(
        "api.main:app",  # Import string format: "module.path:variable"
        host="0.0.0.0",
        port=8001,
        reload=True  # Auto-reload on code changes
    )

