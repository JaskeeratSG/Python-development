"""Run the RAG PDF Data API server. Run from project root (RAG_pdf_data)."""

import sys
from pathlib import Path

# Add src so that "app" and "rag" resolve to src/app and src/rag
_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import uvicorn

from app.config import HOST, PORT

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        reload_dirs=[str(_src)] if _src.exists() else None,
    )
