"""ChromaDB vector store: one collection per document (doc_id)."""

from pathlib import Path
from typing import List

from app.config import CHROMA_DIR

# Persist Chroma under project
CHROMA_PERSIST_DIR = Path(CHROMA_DIR)
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError("chromadb is required. Install with: pip install chromadb") from None
        _client = chromadb.PersistentClient(
            path=str(CHROMA_PERSIST_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
    return _client


def _collection_name(doc_id: str) -> str:
    """Chroma collection name for a document (safe for IDs)."""
    return f"doc_{doc_id.replace('-', '_')}"


def add_document_chunks(doc_id: str, chunks: List[str], embeddings: List[List[float]]) -> None:
    """
    Add chunks and their embeddings for a document.
    Replaces any existing chunks for this doc_id.

    Args:
        doc_id: Document ID.
        chunks: List of chunk texts.
        embeddings: List of embedding vectors (same length as chunks).
    """
    if not chunks or not embeddings or len(chunks) != len(embeddings):
        return
    client = _get_client()
    name = _collection_name(doc_id)
    try:
        client.delete_collection(name)
    except Exception:
        pass
    coll = client.create_collection(name=name, metadata={"doc_id": doc_id})
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    coll.add(ids=ids, documents=chunks, embeddings=embeddings)


def query_chunks(doc_id: str, query_text: str, top_k: int = 4) -> List[str]:
    """
    Retrieve top-k chunks most similar to the query for the given document.

    Args:
        doc_id: Document ID.
        query_text: Query string (will be embedded).
        top_k: Number of chunks to return.

    Returns:
        List of chunk texts (may be fewer than top_k if collection is small).
    """
    from rag.embeddings import embed_texts

    client = _get_client()
    name = _collection_name(doc_id)
    try:
        coll = client.get_collection(name=name)
    except Exception:
        return []
    query_embedding = embed_texts([query_text])[0]
    results = coll.query(query_embeddings=[query_embedding], n_results=min(top_k, coll.count()))
    if not results or not results.get("documents"):
        return []
    return list(results["documents"][0])


def get_chunk_count(doc_id: str) -> int | None:
    """
    Return number of chunks stored for this document, or None if no collection exists.
    """
    client = _get_client()
    name = _collection_name(doc_id)
    try:
        coll = client.get_collection(name=name)
        return coll.count()
    except Exception:
        return None


def delete_document_chunks(doc_id: str) -> None:
    """Remove all stored chunks for a document."""
    client = _get_client()
    name = _collection_name(doc_id)
    try:
        client.delete_collection(name)
    except Exception:
        pass
