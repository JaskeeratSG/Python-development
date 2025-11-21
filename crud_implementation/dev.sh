#!/bin/bash

# CRUD Application Development Script (with auto-reload)
echo "🔧 Starting CRUD API in development mode..."

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating default SQLite configuration..."
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=sqlite:///./crud.db
EOF
fi

# Test database connection
echo "🔍 Testing database connection..."
python -c "
from config.database import test_connection
if test_connection():
    print('✅ Database connection successful!')
else:
    print('❌ Database connection failed!')
    exit(1)
"

# Start the application with uvicorn directly (better for development)
echo "🚀 Starting FastAPI server in development mode..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "📖 Alternative Docs: http://localhost:8000/redoc"
echo "🔗 API Base URL: http://localhost:8000"
echo "🔄 Auto-reload enabled for development"
echo "=" * 50

uvicorn main:app --host 127.0.0.1 --port 8000 --reload
