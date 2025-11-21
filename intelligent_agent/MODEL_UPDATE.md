# Model Update Guide

## Issue
The model `llama-3.1-70b-versatile` has been decommissioned by Groq.

## Solution
Updated default model to `llama-3.1-8b-instant`

## Available Groq Models (2025)

### Recommended Models:
- `llama-3.1-8b-instant` - Fast, good for general use (DEFAULT)
- `llama-3.1-70b-versatile` - **DEPRECATED** (use alternatives below)
- `mixtral-8x7b-32768` - Good for longer context
- `gemma2-9b-it` - Alternative option
- `llama-3.3-70b-versatile` - If available (newer version)

## How to Update

### Option 1: Update .env file
If you have a `.env` file, update the model:
```env
DEFAULT_MODEL=llama-3.1-8b-instant
```

### Option 2: Use environment variable
```bash
export DEFAULT_MODEL=llama-3.1-8b-instant
```

### Option 3: The code will use the new default
The default in `config/settings.py` has been updated, so if you don't have a `.env` file, it will work automatically.

## Test the Update

After updating, restart your services:
```bash
# Restart FastAPI
python api_server.py

# Restart Streamlit
streamlit run streamlit_app.py
```

## Verify Model Works

Test with a simple query in Streamlit or via API:
```bash
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, test query"}'
```

