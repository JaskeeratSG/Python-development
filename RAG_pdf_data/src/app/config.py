"""Load settings from environment."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project paths (repo root = parent of src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = PROJECT_ROOT / "uploads"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
DATA_DIR = PROJECT_ROOT / "data"
# HuggingFace/sentence-transformers cache (avoids permission issues with ~/.cache)
HF_CACHE_DIR = PROJECT_ROOT / ".cache" / "huggingface"

# Ensure dirs exist
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Database (optional; for document metadata later)
DATABASE_URL = os.getenv("DATABASE_URL")

# RAG: chunking and retrieval
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "8"))  # chunks to retrieve for Q&A

# LLM (for summary / Q&A later)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "groq")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
