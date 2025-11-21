"""
Async FastAPI Application
========================

Main FastAPI application with async support for better concurrency.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from config.async_database import create_tables, test_connection
from views.async_user_views import router as user_router
# Import other async routers when you create them
# from views.async_product_views import router as product_router
# from views.async_order_views import router as order_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for async startup/shutdown"""
    # Startup
    print("🚀 Starting Async CRUD API with MVC Architecture...")
    
    # Test database connection
    if await test_connection():
        print("✅ Async database connection successful!")
        # Create tables
        await create_tables()
        print("✅ Database tables created!")
    else:
        print("❌ Async database connection failed!")
        print("Please check your database configuration")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Async CRUD API...")

# Create FastAPI app with async lifespan
app = FastAPI(
    title="Async CRUD API with MVC Architecture",
    description="A complete async CRUD API implementation using FastAPI with MVC pattern",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include async routers
app.include_router(user_router)
# app.include_router(product_router)
# app.include_router(order_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Async CRUD API with MVC Architecture",
        "version": "1.0.0",
        "architecture": "MVC (Model-View-Controller) with Async Support",
        "docs": "/docs",
        "endpoints": {
            "users": "/users",
            "products": "/products", 
            "orders": "/orders"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Async API is running"}

@app.get("/async-test")
async def async_test():
    """Test async functionality"""
    # Simulate some async work
    await asyncio.sleep(0.1)  # Simulate I/O operation
    return {
        "message": "Async test successful",
        "concurrent_requests": "This endpoint can handle multiple requests concurrently"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting async server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📖 Alternative Docs: http://localhost:8000/redoc")
    print("🔗 API Base URL: http://localhost:8000")
    print("⚡ Async support enabled for better concurrency")
    print("=" * 50)
    
    uvicorn.run(
        "async_main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
