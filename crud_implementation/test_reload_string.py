#!/usr/bin/env python3
"""
Test script using import string - no warning
"""

import uvicorn
from fastapi import FastAPI

# Create a simple FastAPI app
app = FastAPI(title="Reload Test - String Version")

@app.get("/")
def read_root():
    return {"message": "Hello World", "version": "2.0"}

@app.get("/test")
def test_endpoint():
    return {"test": "This endpoint will change when you modify this file - STRING VERSION"}

if __name__ == "__main__":
    print("Testing uvicorn reload functionality with import string...")
    print("1. Start this script")
    print("2. Make a change to the test_endpoint function")
    print("3. Save the file")
    print("4. Watch if the server reloads (no warning!)")
    print("=" * 50)
    
    # This will NOT show the warning
    uvicorn.run(
        "test_reload_string:app",  # Import string - no warning
        host="127.0.0.1",
        port=8002,
        reload=True
    )
