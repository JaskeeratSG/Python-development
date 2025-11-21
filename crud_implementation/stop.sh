#!/bin/bash

# CRUD Application Stop Script
echo "🛑 Stopping CRUD API..."

# Find and kill the process running on port 8000
PID=$(lsof -ti:8000)

if [ -n "$PID" ]; then
    echo "🔍 Found process $PID running on port 8000"
    kill $PID
    echo "✅ Application stopped successfully"
else
    echo "ℹ️  No application found running on port 8000"
fi

# Also kill any python main.py processes
PYTHON_PIDS=$(pgrep -f "python.*main.py")

if [ -n "$PYTHON_PIDS" ]; then
    echo "🔍 Found Python main.py processes: $PYTHON_PIDS"
    kill $PYTHON_PIDS
    echo "✅ Python processes stopped"
else
    echo "ℹ️  No Python main.py processes found"
fi

echo "🏁 All done!"
