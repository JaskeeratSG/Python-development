"""Database layer: document registry in PostgreSQL."""

from contextlib import contextmanager
from typing import Optional

from app.config import DATABASE_URL

# Table name used for document metadata (plan: documents)
DOCUMENTS_TABLE = "documents"

CREATE_DOCUMENTS_SQL = f"""
CREATE TABLE IF NOT EXISTS {DOCUMENTS_TABLE} (
    doc_id     UUID PRIMARY KEY,
    filename   VARCHAR(255) NOT NULL,
    file_path  TEXT NOT NULL,
    is_cv      BOOLEAN NOT NULL DEFAULT FALSE,
    summary    TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


@contextmanager
def get_connection():
    """Yield a DB connection. Use when DATABASE_URL is set."""
    import psycopg
    with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
        yield conn


def init_db() -> bool:
    """Create tables if they don't exist. Returns True on success."""
    if not DATABASE_URL or not DATABASE_URL.strip().startswith("postgresql"):
        return False
    try:
        with get_connection() as conn:
            conn.execute(CREATE_DOCUMENTS_SQL)
            conn.commit()
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to init DB: {e}") from e


def insert_document(
    doc_id: str,
    filename: str,
    file_path: str,
    is_cv: bool = False,
    summary: Optional[str] = None,
) -> None:
    """Insert one document row."""
    with get_connection() as conn:
        conn.execute(
            f"""
            INSERT INTO {DOCUMENTS_TABLE} (doc_id, filename, file_path, is_cv, summary)
            VALUES (%s::uuid, %s, %s, %s, %s)
            """,
            (doc_id, filename, file_path, is_cv, summary),
        )
        conn.commit()


def get_document(doc_id: str) -> Optional[dict]:
    """Get one document by doc_id. Returns None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            f"""
            SELECT doc_id::text, filename, file_path, is_cv, summary, created_at
            FROM {DOCUMENTS_TABLE} WHERE doc_id = %s::uuid
            """,
            (doc_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "doc_id": row[0],
        "filename": row[1],
        "file_path": row[2],
        "is_cv": row[3],
        "summary": row[4],
        "created_at": row[5],
    }


def list_documents() -> list[dict]:
    """List all documents, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT doc_id::text, filename, file_path, is_cv, summary, created_at
            FROM {DOCUMENTS_TABLE} ORDER BY created_at DESC
            """
        ).fetchall()
    return [
        {
            "doc_id": r[0],
            "filename": r[1],
            "file_path": r[2],
            "is_cv": r[3],
            "summary": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]


def update_document_summary_and_cv(doc_id: str, summary: Optional[str], is_cv: bool) -> None:
    """Update summary and is_cv for a document."""
    with get_connection() as conn:
        conn.execute(
            f"""
            UPDATE {DOCUMENTS_TABLE} SET summary = %s, is_cv = %s WHERE doc_id = %s::uuid
            """,
            (summary, is_cv, doc_id),
        )
        conn.commit()
