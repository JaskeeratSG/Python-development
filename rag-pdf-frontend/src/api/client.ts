const API_BASE =
  (import.meta as unknown as { env: { VITE_API_URL?: string } }).env?.VITE_API_URL ?? '';

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail ?? 'Request failed');
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; db_connected?: boolean }>('/api/health'),

  listDocuments: () =>
    request<import('./types').DocumentSummary[]>('/api/documents'),

  getSummary: (docId: string) =>
    request<{ doc_id: string; summary: string | null; is_cv: boolean }>(
      `/api/documents/${docId}/summary`
    ),

  getChunks: (docId: string, preview?: number) => {
    const q = preview != null ? `?preview=${preview}` : '';
    return request<import('./types').ChunkInfo>(
      `/api/documents/${docId}/chunks${q}`
    );
  },

  getChroma: (preview?: number) => {
    const q = preview != null ? `?preview=${preview}` : '';
    return request<import('./types').ChromaResponse>(`/api/chroma${q}`);
  },

  upload: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return request<import('./types').UploadResponse>('/api/upload', {
      method: 'POST',
      body: form,
    });
  },

  ask: (docId: string, body: import('./types').AskRequest) =>
    request<import('./types').AskResponse>(`/api/documents/${docId}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),

  reprocess: (docId: string) =>
    request<{ doc_id: string; summary: string | null; is_cv: boolean; message: string }>(
      `/api/documents/${docId}/reprocess`,
      { method: 'POST' }
    ),
};
