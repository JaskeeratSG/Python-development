#!/bin/bash

# CRUD Application Startup Script
echo "🚀 Starting CRUD API with MVC Architecture..."

# Navigate to project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install fastapi uvicorn sqlalchemy pydantic python-multipart python-dotenv psycopg2-binary
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
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

# Start the application
echo "🚀 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "📖 Alternative Docs: http://localhost:8000/redoc"
echo "🔗 API Base URL: http://localhost:8000"
echo "=" * 50

python main.py
