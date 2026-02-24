# RAG PDF – Frontend

React frontend for the RAG PDF Data API. Upload PDFs, view summaries, and ask questions.

## Setup

```bash
npm install
```

## Run (dev)

Start the backend (from `RAG_pdf_data`):

```bash
cd ../RAG_pdf_data && source start.sh && python run_server.py
```

Then start the frontend:

```bash
npm run dev
```

The app runs at `http://localhost:5173` and proxies `/api` to `http://localhost:8000`.

## Build

```bash
npm run build
```

Output is in `dist/`. To use a different API URL when serving the built app, set `VITE_API_URL` before building (e.g. in `.env`).

## Structure

- `src/api/` – API client and types
- `src/components/` – Layout, DocumentCard, DocumentList, UploadZone, SummaryBlock, AskForm
- `src/pages/` – HomePage (list + upload), DocumentPage (summary + Q&A)
