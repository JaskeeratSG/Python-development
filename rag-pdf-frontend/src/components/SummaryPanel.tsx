import type { DocumentSummary } from '../api/types';

interface SummaryPanelProps {
  doc: DocumentSummary | null;
}

export function SummaryPanel({ doc }: SummaryPanelProps) {
  if (!doc) {
    return (
      <aside className="summary-panel">
        <h2 className="summary-panel__title">Document summary</h2>
        <p className="summary-panel__empty">Select a document to see its summary.</p>
      </aside>
    );
  }

  return (
    <aside className="summary-panel">
      <h2 className="summary-panel__title">Summary</h2>
      <div className="summary-panel__meta">
        <span className="summary-panel__filename">{doc.filename}</span>
        {doc.is_cv && <span className="summary-panel__badge">CV</span>}
      </div>
      {doc.summary ? (
        <p className="summary-panel__text">{doc.summary}</p>
      ) : (
        <p className="summary-panel__empty">No summary available for this document.</p>
      )}
    </aside>
  );
}
