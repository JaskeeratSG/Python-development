"""Embedding model for RAG (sentence-transformers)."""

import os
from typing import List

from app.config import HF_CACHE_DIR

# Use project-local cache so we don't need write access to ~/.cache/huggingface
os.environ["TRANSFORMERS_CACHE"] = str(HF_CACHE_DIR)
os.environ["HF_HOME"] = str(HF_CACHE_DIR)

# Default model: good balance of speed and quality for retrieval
DEFAULT_EMBED_MODEL = "all-MiniLM-L6-v2"

_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required. Install with: pip install sentence-transformers"
            ) from None
        _model = SentenceTransformer(DEFAULT_EMBED_MODEL)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of texts into vectors.

    Args:
        texts: List of strings (e.g. chunk texts).

    Returns:
        List of embedding vectors (each a list of floats).
    """
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, convert_to_numpy=True)
    return vectors.tolist()
