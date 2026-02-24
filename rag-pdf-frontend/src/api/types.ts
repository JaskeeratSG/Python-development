/** API types matching the FastAPI backend. */

export interface DocumentSummary {
  doc_id: string;
  filename: string;
  is_cv: boolean;
  summary: string | null;
}

export interface UploadResponse {
  doc_id: string;
  filename: string;
  is_cv: boolean;
  summary: string | null;
}

export interface AskRequest {
  question: string;
  max_words?: number | null;
}

export interface AskResponse {
  answer: string;
  is_cv: boolean;
  doc_id: string;
}

export interface ChunkInfo {
  doc_id: string;
  chunk_count: number;
  has_chunks: boolean;
  chunks?: { id: string; text: string }[];
  error?: string;
}

export interface ChromaCollection {
  name: string;
  doc_id: string;
  chunk_count: number;
  preview_chunks?: { id: string; text: string }[];
}

export interface ChromaResponse {
  chroma_path: string;
  collections: ChromaCollection[];
}
