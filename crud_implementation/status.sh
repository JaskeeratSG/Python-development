#!/bin/bash

# CRUD Application Status Script
echo "📊 CRUD API Status Check"
echo "========================"

# Check if application is running on port 8000
PID=$(lsof -ti:8000)

if [ -n "$PID" ]; then
    echo "✅ Application is running (PID: $PID)"
    
    # Test health endpoint
    echo "🔍 Testing health endpoint..."
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "✅ Health check passed: $HEALTH_RESPONSE"
    else
        echo "❌ Health check failed"
    fi
    
    # Show API info
    echo "🔍 Getting API information..."
    API_INFO=$(curl -s http://localhost:8000/ 2>/dev/null)
    echo "📋 API Info: $API_INFO"
    
else
    echo "❌ Application is not running"
    echo "💡 Run './start.sh' to start the application"
fi

echo ""
echo "🔗 Available endpoints:"
echo "   - API Base: http://localhost:8000"
echo "   - Documentation: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
