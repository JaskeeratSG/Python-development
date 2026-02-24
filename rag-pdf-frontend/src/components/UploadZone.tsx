import { useCallback, useState } from 'react';

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>;
  accept?: string;
  disabled?: boolean;
}

export function UploadZone({
  onUpload,
  accept = '.pdf',
  disabled = false,
}: UploadZoneProps) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    async (file: File | null) => {
      if (!file || disabled || uploading) return;
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Only PDF files are allowed.');
        return;
      }
      setError(null);
      setUploading(true);
      try {
        await onUpload(file);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Upload failed.');
      } finally {
        setUploading(false);
      }
    },
    [onUpload, disabled, uploading]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      handleFile(e.dataTransfer.files[0] ?? null);
    },
    [handleFile]
  );

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  }, []);

  const onDragLeave = useCallback(() => {
    setDragging(false);
  }, []);

  const onInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleFile(e.target.files?.[0] ?? null);
      e.target.value = '';
    },
    [handleFile]
  );

  return (
    <div
      className={`upload-zone ${dragging ? 'upload-zone--dragging' : ''} ${uploading ? 'upload-zone--uploading' : ''}`}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
    >
      <input
        type="file"
        accept={accept}
        onChange={onInputChange}
        disabled={disabled || uploading}
        className="upload-zone__input"
        aria-label="Upload PDF"
      />
      {uploading ? (
        <p className="upload-zone__text">Uploading…</p>
      ) : (
        <p className="upload-zone__text">
          Drop a PDF here or <span className="upload-zone__browse">browse</span>
        </p>
      )}
      {error && <p className="upload-zone__error">{error}</p>}
    </div>
  );
}
