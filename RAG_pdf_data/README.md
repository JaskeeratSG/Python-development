# RAG PDF Data

Upload PDFs, get short summaries, and ask questions. CV detection with optional word-limited answers.

## Setup

```bash
cd RAG_pdf_data
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` (or use existing `.env`) and set `GROQ_API_KEY` and `DATABASE_URL` if needed.

**Create DB tables (optional):** The server creates the `documents` table on startup if the DB is connected. To create tables manually (e.g. before first run):

```bash
python scripts/init_db.py
```

## Run the server

```bash
python run_server.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

## API (current)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/upload` | Upload PDF (multipart `file`) |
| GET | `/api/documents` | List documents |
| GET | `/api/documents/{doc_id}/summary` | Get summary and is_cv |
| POST | `/api/documents/{doc_id}/ask` | Ask a question (body: `question`, optional `max_words`) |

See [PLAN.md](PLAN.md) for full design and upcoming RAG/CV features.
