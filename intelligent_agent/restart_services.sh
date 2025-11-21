#!/bin/bash
# Script to restart both backend and frontend services

cd "$(dirname "$0")"

echo "🛑 Stopping existing services..."
lsof -ti:8001,8501 2>/dev/null | xargs kill -9 2>/dev/null
sleep 2

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🚀 Starting Backend (FastAPI) on port 8001..."
python api_server.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

sleep 3

echo "🚀 Starting Frontend (Streamlit) on port 8501..."
streamlit run streamlit_app.py --server.port 8501 --server.headless true > frontend.log 2>&1 &
STREAMLIT_PID=$!
echo "Streamlit PID: $STREAMLIT_PID"

sleep 3

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Backend API: http://localhost:8001"
echo "📖 API Docs: http://localhost:8001/docs"
echo "🎨 Frontend UI: http://localhost:8501"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID $STREAMLIT_PID"
echo "   or: lsof -ti:8001,8501 | xargs kill -9"

