import { DocumentCard } from './DocumentCard';
import type { DocumentSummary } from '../api/types';

interface DocumentListProps {
  documents: DocumentSummary[];
  loading?: boolean;
  error?: string | null;
}

export function DocumentList({ documents, loading, error }: DocumentListProps) {
  if (error) {
    return (
      <div className="document-list document-list--error">
        <p>{error}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="document-list document-list--loading">
        <p>Loading documents…</p>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="document-list document-list--empty">
        <p>No documents yet. Upload a PDF to get started.</p>
      </div>
    );
  }

  return (
    <ul className="document-list">
      {documents.map((doc) => (
        <li key={doc.doc_id}>
          <DocumentCard doc={doc} />
        </li>
      ))}
    </ul>
  );
}
