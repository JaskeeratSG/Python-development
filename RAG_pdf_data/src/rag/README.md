# RAG module

Structured RAG pipeline under `src/rag/`.

## Layout

| File | Role |
|------|------|
| `pdf.py` | Extract text from PDF (pypdf). |
| `chunker.py` | Split text into chunks (LangChain `RecursiveCharacterTextSplitter`). |
| `embeddings.py` | Embed chunks with sentence-transformers (`all-MiniLM-L6-v2`). |
| `store.py` | ChromaDB: one collection per `doc_id`; add chunks, query by similarity. |
| `llm.py` | Groq LLM client for summary, CV detection, and Q&A. |
| `summary.py` | Short summary from document text (LLM). |
| `cv.py` | CV/Resume detection (LLM yes/no). |
| `qa.py` | RAG Q&A: retrieve chunks → LLM answer; optional `max_words` for CV. |
| `pipeline.py` | Single `ingest_document(file_path, doc_id)` → (summary, is_cv). |

## Flow

1. **Upload** (in `app.main`): Save PDF → `ingest_document(path, doc_id)` → extract → chunk → embed → Chroma; then summarize + `is_cv` → update DB.
2. **Ask** (in `app.main`): `answer_question(doc_id, question, max_words)` → query Chroma → LLM with context.

## Config (from `app.config`)

- `CHUNK_SIZE`, `CHUNK_OVERLAP` – chunking.
- `CHROMA_DIR` – Chroma persistence (repo root `chroma_db/`).
- `GROQ_API_KEY`, `DEFAULT_MODEL`, `DEFAULT_TEMPERATURE` – LLM.

## Run

From project root:

```bash
python run_server.py
```

`run_server.py` adds `src` to `PYTHONPATH` so `app` and `rag` resolve to `src/app` and `src/rag`.
