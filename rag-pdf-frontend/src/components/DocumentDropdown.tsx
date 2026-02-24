import type { DocumentSummary } from '../api/types';

interface DocumentDropdownProps {
  documents: DocumentSummary[];
  value: string;
  onChange: (docId: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function DocumentDropdown({
  documents,
  value,
  onChange,
  disabled = false,
  placeholder = 'Select a document',
}: DocumentDropdownProps) {
  return (
    <div className="document-dropdown">
      <label className="document-dropdown__label">Document</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="document-dropdown__select"
        aria-label="Select document"
      >
        <option value="">{documents.length === 0 ? 'No documents yet' : placeholder}</option>
        {documents.map((doc) => (
          <option key={doc.doc_id} value={doc.doc_id}>
            {doc.filename} {doc.is_cv ? '(CV)' : ''}
          </option>
        ))}
      </select>
    </div>
  );
}
