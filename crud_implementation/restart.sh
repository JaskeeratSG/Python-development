#!/bin/bash

# CRUD Application Restart Script
echo "🔄 Restarting CRUD API..."

# Navigate to project directory
cd "$(dirname "$0")"

# Stop the application
echo "🛑 Stopping current application..."
./stop.sh

# Wait a moment
sleep 2

# Start the application
echo "🚀 Starting application..."
./start.sh
