"""
Main FastAPI Application
MVC Pattern: Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import create_tables, test_connection
from views import user_router, product_router, order_router

# Create FastAPI app
app = FastAPI(
    title="CRUD API with MVC Architecture",
    description="A complete CRUD API implementation using FastAPI with MVC pattern",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting CRUD API with MVC Architecture...")
    
    # Test database connection
    if test_connection():
        print("✅ Database connection successful!")
        # Create tables
        create_tables()
        print("✅ Database tables created!")
    else:
        print("❌ Database connection failed!")
        print("Please check your database configuration in config/database.py")

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to CRUD API with MVC Architecture",
        "version": "1.0.0",
        "architecture": "MVC (Model-View-Controller)",
        "docs": "/docs",
        "endpoints": {
            "users": "/users",
            "products": "/products", 
            "orders": "/orders"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📖 Alternative Docs: http://localhost:8000/redoc")
    print("🔗 API Base URL: http://localhost:8000")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

