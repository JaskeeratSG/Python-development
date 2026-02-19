"""Text chunking for RAG."""

from app.config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """
    Split text into overlapping chunks for embedding and retrieval.

    Args:
        text: Full document text.
        chunk_size: Max characters per chunk. Default from config.
        overlap: Overlap between chunks. Default from config.

    Returns:
        List of text chunks.
    """
    size = chunk_size if chunk_size is not None else CHUNK_SIZE
    over = overlap if overlap is not None else CHUNK_OVERLAP
    if not text or not text.strip():
        return []

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=over,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text.strip())
    return [c for c in chunks if c.strip()]
