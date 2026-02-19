"""Single pipeline: PDF → text → chunks → embed → store → summary + CV detection."""

from typing import Tuple

from rag.chunker import chunk_text
from rag.cv import is_cv
from rag.embeddings import embed_texts
from rag.pdf import extract_text_from_pdf
from rag.store import add_document_chunks
from rag.summary import summarize_text


def ingest_document(file_path: str, doc_id: str) -> Tuple[str, bool]:
    """
    Ingest a PDF: extract text, chunk, embed, store in Chroma, then compute summary and is_cv.

    Args:
        file_path: Path to the PDF file.
        doc_id: Document ID (used for Chroma collection and consistency with DB).

    Returns:
        (summary, is_cv)

    Raises:
        FileNotFoundError: If PDF is missing.
        ValueError: If PDF has no text or extraction fails.
    """
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    # If chunker returned nothing (e.g. very short doc), store full text as one chunk so Q&A works
    if not chunks and text.strip():
        chunks = [text.strip()[:50_000]]  # single chunk, cap size
    if chunks:
        embeddings = embed_texts(chunks)
        add_document_chunks(doc_id, chunks, embeddings)
    summary = summarize_text(text)
    cv = is_cv(text)
    summary = summarize_text(text)
    cv = is_cv(text)
    return summary, cv
