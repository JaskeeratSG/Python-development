import { Link } from 'react-router-dom';
import type { DocumentSummary } from '../api/types';

interface DocumentCardProps {
  doc: DocumentSummary;
}

export function DocumentCard({ doc }: DocumentCardProps) {
  return (
    <Link to={`/documents/${doc.doc_id}`} className="document-card">
      <div className="document-card__meta">
        <span className="document-card__filename">{doc.filename}</span>
        {doc.is_cv && <span className="document-card__badge">CV</span>}
      </div>
      {doc.summary && (
        <p className="document-card__summary">
          {doc.summary.length > 160 ? `${doc.summary.slice(0, 160)}…` : doc.summary}
        </p>
      )}
    </Link>
  );
}
