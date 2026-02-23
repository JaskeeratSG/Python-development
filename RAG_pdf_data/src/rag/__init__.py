"""
RAG pipeline: PDF → text → chunks → embeddings → Chroma.
Summary, CV detection, and Q&A use the vector store + LLM.
"""

from rag.chunker import chunk_text
from rag.cv import is_cv
from rag.pdf import extract_text_from_pdf
from rag.pipeline import ingest_document
from rag.qa import answer_question
from rag.store import add_document_chunks, delete_document_chunks, query_chunks
from rag.summary import summarize_text

__all__ = [
    "extract_text_from_pdf",
    "chunk_text",
    "add_document_chunks",
    "query_chunks",
    "delete_document_chunks",
    "ingest_document",
    "summarize_text",
    "is_cv",
    "answer_question",
]
