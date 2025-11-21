#!/bin/bash
# Script to run Streamlit app for Intelligent Agent System

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Streamlit
streamlit run streamlit_app.py --server.port 8501 --server.address localhost

