# RAG PDF Data — Project Plan

## 1. Project Overview

| Item | Description |
|------|-------------|
| **Name** | RAG PDF Data |
| **Goal** | Let users upload PDFs, get summaries, and ask questions. If the document is a CV, support CV-specific Q&A with configurable word limits. |
| **Stack** | Python, FastAPI (backend), simple frontend for upload and chat. |

---

## 2. Features (What We Will Build)

### 2.1 Core

| # | Feature | Description |
|---|--------|-------------|
| 1 | **PDF upload** | User uploads a PDF via the frontend; backend stores it and processes text. |
| 2 | **Short summary** | System generates a concise summary of the uploaded PDF. |
| 3 | **General Q&A** | User can ask free-form questions about the document; answers are grounded in the PDF (RAG). |

### 2.2 CV-Specific

| # | Feature | Description |
|---|--------|-------------|
| 4 | **CV detection** | System classifies whether the document is a CV/Resume (e.g. via LLM or heuristics). |
| 5 | **CV-mode Q&A** | If CV: answers are focused on CV content and **respect a maximum word count** (e.g. “answer in at most N words”). |

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  • Upload PDF   • View summary   • Ask question (general / CV)   │
└────────────────────────────┬────────────────────────────────────┘
                              │ HTTP (e.g. /upload, /summary, /ask)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                               │
│  • Receive PDF   • Run RAG pipeline   • CV detection   • LLM     │
└────────────────────────────┬────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   ┌──────────┐        ┌────────────┐        ┌──────────┐
   │  PDF     │        │  Vector    │        │  LLM     │
   │  storage │        │  store     │        │  (e.g.   │
   │  (files) │        │  (Chroma)  │        │  Groq)   │
   └──────────┘        └────────────┘        └──────────┘
```

- **Frontend**: Upload form, summary display, question input, optional “CV mode” or word-count hint.
- **Backend**: FastAPI app that orchestrates upload → parse → embed → store → summary and Q&A (with CV detection and word-count when applicable).

---

## 4. Tech Stack (Proposed)

| Layer | Choice | Purpose |
|-------|--------|---------|
| **API** | FastAPI | Routes, request/response models, file upload. |
| **PDF parsing** | pypdf (or PyPDF2) | Extract text from uploaded PDFs. |
| **Text splitting** | LangChain `RecursiveCharacterTextSplitter` | Chunk document for RAG. |
| **Embeddings** | Sentence-transformers (e.g. `all-MiniLM-L6-v2`) or API | Turn chunks into vectors (local = no extra API key). |
| **Vector store** | ChromaDB | Store embeddings and run similarity search. |
| **LLM** | Groq (e.g. Llama) | Summary, CV detection, and answer generation (reuse existing key if available). |
| **Frontend** | HTML + CSS + JS (or simple React) | Upload, show summary, send questions. |

---

## 4.1 Database Choices

We need **two** kinds of storage:

### Vector store (for RAG only)

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **ChromaDB** | Local, no server, simple API, persists to disk | Single-node only | **Use this** for embeddings + similarity search. |
| FAISS | Fast, local | No metadata filtering out of the box; more manual | Alternative if we need maximum speed. |
| Qdrant / Pinecone | Scalable, cloud | Extra service, API keys | For production at scale later. |
| pgvector (PostgreSQL) | One DB for everything | More setup; need Postgres | Use if you already run Postgres and want one stack. |

**Decision: use ChromaDB** for the vector store (chunk embeddings + retrieval by `doc_id`).

### Metadata store (document list, summary, is_cv)

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **SQLite** | No server, single file, built into Python | Single writer | **Use this** for doc registry (doc_id, filename, is_cv, summary, uploaded_at). |
| JSON file(s) | Trivial | No concurrent writes, no queries | Only if we never list/filter docs. |
| PostgreSQL | Robust, you may already have it (e.g. intelligent_agent) | Requires running Postgres | Use if you prefer one DB for all projects. |
| No DB (Chroma metadata only) | Fewer dependencies | Chroma metadata is not ideal for “list all docs” / update summary | Possible but clunkier. |

**Decision: use SQLite** for document metadata (e.g. `documents` table: id, filename, path, is_cv, summary, created_at). Keeps the app self-contained and easy to run.

### Summary

| Purpose | DB | Where |
|--------|-----|-------|
| Chunk embeddings + similarity search | **ChromaDB** | `chroma_db/` (directory on disk) |
| Document registry (metadata, summary, is_cv) | **SQLite** | e.g. `rag_data.db` in project root or `data/` |

---

## 5. Data Flow (Structured Steps)

### 5.1 Upload & Ingest

1. User selects PDF in browser → POST to backend (e.g. `/api/upload`).
2. Backend saves file (e.g. `uploads/<doc_id>.pdf`).
3. Extract text with pypdf.
4. Split text into chunks (size/overlap TBD).
5. Generate embeddings for chunks.
6. Store chunks + embeddings in Chroma (indexed by `doc_id`).
7. Optionally store metadata: `doc_id`, filename, upload time, `is_cv` (filled later).

### 5.2 Summary

1. After ingest (or on demand), backend runs “summarize this document” over full text or key chunks.
2. LLM returns a short summary (e.g. 2–5 sentences).
3. Summary is returned to frontend and can be stored/cached per `doc_id`.

### 5.3 CV Detection

1. After ingest, run a small “classification” step:
   - **Option A**: LLM prompt — “Is this document a CV/Resume? Answer yes/no and optionally 1 line why.”
   - **Option B**: Heuristics (e.g. sections like “Experience”, “Education”, “Skills”) + optional LLM.
2. Set `is_cv: true/false` (and optionally “why”) for this `doc_id`.
3. Frontend can show “Detected as CV” and enable CV-specific UI (e.g. word count selector).

### 5.4 General Q&A (RAG)

1. User asks a question (e.g. POST `/api/ask` with `doc_id` and `question`).
2. Backend embeds the question, retrieves top-k chunks from Chroma for that `doc_id`.
3. Build a prompt: context (retrieved chunks) + user question.
4. LLM generates answer (no strict word limit).
5. Return answer to frontend.

### 5.5 CV Q&A (With Word Count)

1. Same as 5.4, but only for documents marked as CV (or when user explicitly chooses “CV mode”).
2. Request includes `max_words` (e.g. 50, 100).
3. Prompt to LLM: “Answer based only on the CV below. Keep the answer to at most {max_words} words.”
4. Return concise, CV-grounded answer.

---

## 6. API Design (Structured)

| Method | Endpoint | Purpose | Key request/response |
|--------|----------|---------|----------------------|
| POST | `/api/upload` | Upload PDF | Body: `file` (multipart). Response: `doc_id`, `filename`, `is_cv`, `summary` (optional). |
| GET  | `/api/documents` | List docs | Response: list of `doc_id`, `filename`, `is_cv`, `summary` (optional). |
| GET  | `/api/documents/{doc_id}/summary` | Get summary | Response: `summary`, `is_cv`. |
| POST | `/api/documents/{doc_id}/ask` | Ask question | Body: `question`, optional `max_words` (for CV). Response: `answer`, `is_cv`. |
| GET  | `/api/health` | Health check | Simple status. |

- All document-scoped routes take `doc_id` so the backend knows which Chroma collection or namespace to use.

---

## 7. Frontend Structure (Screens/Flows)

| Screen / Flow | Elements |
|---------------|----------|
| **Upload** | File input (PDF only), “Upload” button, success message with `doc_id` and “Detected: CV / Not CV”. |
| **Summary** | After upload (or after selecting a document): show short summary and “Is CV: Yes/No”. |
| **Ask question** | Dropdown or list to select document → text input for question → optional “Max words” (for CV) → “Ask” → display answer. |
| **Optional** | List of uploaded documents with summary and “Ask” link. |

---

## 8. Folder Structure (Proposed)

```text
RAG_pdf_data/
├── PLAN.md                 # This file
├── README.md               # Setup and run instructions
├── requirements.txt        # Python deps
├── .env.example            # GROQ_API_KEY, etc.
├── app/
│   ├── main.py             # FastAPI app, routes (upload, summary, ask)
│   ├── config.py           # Settings (paths, model, chunk size, etc.)
│   ├── models.py           # Pydantic request/response models
│   └── services/
│       ├── pdf_service.py  # PDF text extraction
│       ├── rag_service.py  # Chunking, embed, Chroma, retrieve
│       ├── summary_service.py  # Generate summary (LLM)
│       └── cv_service.py   # CV detection + CV Q&A with word count
├── uploads/                # Stored PDFs (gitignore)
├── chroma_db/              # Chroma vector store (gitignore)
├── data/                   # Optional: SQLite DB here (e.g. rag_data.db, gitignore)
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js
```

---

## 9. Implementation Phases (Order of Work)

| Phase | Tasks | Outcome |
|-------|--------|---------|
| **1. Setup** | Repo/folder, `requirements.txt`, `.env.example`, `app/config.py` | Backend runs; no routes yet. |
| **2. PDF + RAG base** | `pdf_service` (extract text), `rag_service` (split, embed, Chroma add/query) | Can ingest one PDF and run similarity search. |
| **3. Upload + summary** | `main.py`: upload route, save file, ingest into Chroma, call `summary_service`; return `doc_id` and summary. | Frontend can upload and see summary. |
| **4. CV detection** | `cv_service`: “is this a CV?” (LLM or heuristics); set `is_cv` per doc. | Upload response (or summary) includes `is_cv`. |
| **5. General Q&A** | `main.py`: POST `/documents/{doc_id}/ask` with RAG retrieval + LLM. | User can ask any question on any doc. |
| **6. CV Q&A with word count** | In ask route: if `is_cv` or CV mode, accept `max_words` and add to prompt. | CV answers respect word limit. |
| **7. Frontend** | HTML/CSS/JS (or small React): upload, list docs, summary, ask with optional `max_words`. | End-to-end flow in browser. |
| **8. Polish** | Error handling, validation (PDF only, file size), simple tests. | Production-ready behaviour. |

---

## 10. Open Decisions (To Confirm)

| # | Decision | Options |
|---|----------|---------|
| 1 | **Embeddings** | Local (sentence-transformers) vs API (e.g. OpenAI) — affects cost and setup. |
| 2 | **CV detection** | LLM-only vs heuristics vs hybrid. |
| 3 | **Default word count for CV** | e.g. 50 or 100 words; make it configurable in UI. |
| 4 | **Multi-document** | One global Chroma collection with `doc_id` filter vs one collection per document. |
| 5 | **Metadata DB** | **Decided:** SQLite for document registry. ChromaDB for vector store. See §4.1. |

---

Once you’re happy with this plan, next step is to implement phase by phase (starting with **Phase 1 – Setup** and **Phase 2 – PDF + RAG base**).
