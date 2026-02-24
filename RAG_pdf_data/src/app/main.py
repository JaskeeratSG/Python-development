"""FastAPI application for RAG PDF Data."""

import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import DATABASE_URL, UPLOAD_DIR
from app.db import (
    get_document,
    init_db,
    insert_document,
    list_documents as db_list_documents,
    update_document_summary_and_cv,
)
from app.models import AskRequest, AskResponse, DocumentSummary, UploadResponse

app = FastAPI(
    title="RAG PDF Data API",
    description="Upload PDFs, get summaries, and ask questions. CV-aware Q&A with optional word limit.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stub store (replace with DB + RAG later)
_docs: dict[str, dict] = {}

# Set at startup: True if DB connection succeeded, False otherwise
_db_connected: bool = False


def _check_db() -> bool:
    """Try to connect to PostgreSQL if DATABASE_URL is set."""
    if not DATABASE_URL or not DATABASE_URL.strip().startswith("postgresql"):
        return False
    try:
        import psycopg
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"   → {type(e).__name__}: {e}")
        return False


@app.on_event("startup")
async def startup():
    """Check DB connection, create tables if needed, and log status."""
    global _db_connected
    if DATABASE_URL:
        _db_connected = _check_db()
        if _db_connected:
            try:
                init_db()
                print("✅ Database connected and tables ready.")
            except Exception as e:
                print(f"⚠️  DB connected but table init failed: {e}. Using in-memory storage.")
                _db_connected = False
        else:
            print("⚠️  DATABASE_URL set but connection failed. Using in-memory storage.")
    else:
        print("ℹ️  No DATABASE_URL set. Using in-memory storage.")


def _doc_id() -> str:
    return str(uuid.uuid4())


@app.get("/")
async def root():
    """API info and links."""
    return {
        "message": "RAG PDF Data API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": {
            "upload": "POST /api/upload",
            "documents": "GET /api/documents",
            "summary": "GET /api/documents/{doc_id}/summary",
            "ask": "POST /api/documents/{doc_id}/ask",
            "chroma": "GET /api/chroma",
            "chunks": "GET /api/documents/{doc_id}/chunks",
        },
    }


@app.get("/api/health")
async def health():
    """Health check. Includes db_connected when DATABASE_URL is set."""
    out = {
        "status": "healthy",
        "service": "rag-pdf-data",
        "db_connected": _db_connected,
    }
    if not DATABASE_URL:
        out["db_note"] = "DATABASE_URL not set; using in-memory storage."
    return out


@app.post("/api/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    """Upload a PDF. Returns doc_id, filename, is_cv, and summary (stub)."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    doc_id = _doc_id()
    path = UPLOAD_DIR / f"{doc_id}.pdf"
    try:
        contents = await file.read()
        path.write_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}") from e

    filename = file.filename or "document.pdf"
    file_path = str(path)
    summary, is_cv = None, False
    if _db_connected:
        try:
            insert_document(doc_id=doc_id, filename=filename, file_path=file_path, is_cv=False, summary=None)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save document record: {e}") from e
    else:
        _docs[doc_id] = {"doc_id": doc_id, "filename": filename, "is_cv": False, "summary": None}

    try:
        from rag import ingest_document
        summary, is_cv = ingest_document(file_path, doc_id)
        if _db_connected:
            update_document_summary_and_cv(doc_id, summary, is_cv)
        else:
            _docs[doc_id]["summary"], _docs[doc_id]["is_cv"] = summary, is_cv
    except Exception as e:
        # RAG failed (e.g. no GROQ key, missing deps); still return upload success
        pass

    return UploadResponse(doc_id=doc_id, filename=filename, is_cv=is_cv, summary=summary)


@app.post("/api/documents/{doc_id}/reprocess")
async def reprocess_document(doc_id: str):
    """Re-run RAG ingest (chunk, embed, store, summary, is_cv) for an existing document. Use after fixing cache/embedding issues."""
    d = _get_doc(doc_id)
    if not d:
        raise HTTPException(status_code=404, detail="Document not found.")
    file_path = d.get("file_path")
    if not file_path:
        raise HTTPException(
            status_code=400,
            detail="No file path stored for this document (reprocess only works for DB-stored docs).",
        )
    try:
        from rag import ingest_document
        summary, is_cv = ingest_document(file_path, doc_id)
        if _db_connected:
            update_document_summary_and_cv(doc_id, summary, is_cv)
        else:
            _docs[doc_id]["summary"], _docs[doc_id]["is_cv"] = summary, is_cv
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reprocess failed: {e}") from e
    return {"doc_id": doc_id, "summary": summary, "is_cv": is_cv, "message": "Reprocessed successfully."}


def _list_docs():
    """Return list of document dicts from DB or in-memory."""
    if _db_connected:
        try:
            return db_list_documents()
        except Exception:
            return list(_docs.values())
    return list(_docs.values())


@app.get("/api/documents", response_model=list[DocumentSummary])
async def list_documents():
    """List uploaded documents."""
    docs = _list_docs()
    return [
        DocumentSummary(
            doc_id=d["doc_id"],
            filename=d["filename"],
            is_cv=d["is_cv"],
            summary=d.get("summary"),
        )
        for d in docs
    ]


def _get_doc(doc_id: str) -> dict | None:
    """Get one document from DB or in-memory."""
    if _db_connected:
        try:
            return get_document(doc_id)
        except Exception:
            return _docs.get(doc_id)
    return _docs.get(doc_id)


@app.get("/api/documents/{doc_id}/summary")
async def get_summary(doc_id: str):
    """Get summary and is_cv for a document."""
    d = _get_doc(doc_id)
    if not d:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"doc_id": doc_id, "summary": d.get("summary"), "is_cv": d["is_cv"]}


@app.get("/api/chroma")
async def list_chroma_collections(preview: int | None = None):
    """
    List all Chroma DB collections (one per document) with chunk counts.
    Use ?preview=N to include the first N chunk texts per collection.
    """
    try:
        from rag.store import (
            CHROMA_PERSIST_DIR,
            get_chunk_previews,
            list_chroma_collections as store_list,
        )
        collections = store_list()
        out = {
            "chroma_path": str(CHROMA_PERSIST_DIR),
            "collections": collections,
        }
        if preview is not None and preview > 0:
            for c in out["collections"]:
                c["preview_chunks"] = get_chunk_previews(c["doc_id"], limit=min(preview, 20))
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chroma error: {e}") from e


@app.get("/api/documents/{doc_id}/chunks")
async def get_chunk_info(doc_id: str, preview: int | None = None):
    """
    Chunk info for a document (count, has_chunks).
    Use ?preview=N to return the first N chunk ids and texts.
    """
    d = _get_doc(doc_id)
    if not d:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        from rag.store import get_chunk_count, get_chunk_previews
        count = get_chunk_count(doc_id)
    except Exception as e:
        return {
            "doc_id": doc_id,
            "chunk_count": None,
            "has_chunks": False,
            "error": str(e),
        }
    payload = {
        "doc_id": doc_id,
        "chunk_count": count if count is not None else 0,
        "has_chunks": (count or 0) > 0,
    }
    if preview is not None and preview > 0:
        try:
            payload["chunks"] = get_chunk_previews(doc_id, limit=min(preview, 50))
        except Exception as e:
            payload["chunks_error"] = str(e)
    return payload


@app.post("/api/documents/{doc_id}/ask", response_model=AskResponse)
async def ask(doc_id: str, body: AskRequest):
    """Ask a question about a document. For CVs, use max_words to limit answer length."""
    d = _get_doc(doc_id)
    if not d:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        from rag import answer_question
        answer = answer_question(doc_id, body.question, max_words=body.max_words)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG error: {e}") from e
    return AskResponse(answer=answer, is_cv=d["is_cv"], doc_id=doc_id)
