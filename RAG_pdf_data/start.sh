#!/bin/bash
# Run with: source start.sh   (so the venv stays active in your shell)

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

# Optional: install/refresh deps
pip install -r requirements.txt -q

echo "Venv active. Run the server with: python run_server.py"
