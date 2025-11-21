#!/usr/bin/env python3
"""
Test script to demonstrate the difference between
passing app as object vs import string
"""

import uvicorn
from fastapi import FastAPI

# Create a simple FastAPI app
app = FastAPI(title="Reload Test")

@app.get("/")
def read_root():
    return {"message": "Hello World", "version": "1.0"}

@app.get("/test")
def test_endpoint():
    return {"test": "This endpoint will change when you modify this file"}

if __name__ == "__main__":
    print("Testing uvicorn reload functionality...")
    print("1. Start this script")
    print("2. Make a change to the test_endpoint function")
    print("3. Save the file")
    print("4. Watch if the server reloads")
    print("=" * 50)
    
    # This will show the warning
    uvicorn.run(
        app,  # Direct object - will show warning
        host="127.0.0.1",
        port=8001,
        reload=True
    )
