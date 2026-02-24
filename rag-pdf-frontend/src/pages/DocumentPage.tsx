import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';
import type { DocumentSummary } from '../api/types';
import { SummaryBlock } from '../components/SummaryBlock';
import { AskForm } from '../components/AskForm';

export function DocumentPage() {
  const { docId } = useParams<{ docId: string }>();
  const [doc, setDoc] = useState<DocumentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!docId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([api.getSummary(docId), api.listDocuments()])
      .then(([summary, list]) => {
        if (cancelled) return;
        const found = list.find((d) => d.doc_id === docId);
        setDoc({
          doc_id: docId,
          filename: found?.filename ?? docId,
          is_cv: summary.is_cv,
          summary: summary.summary,
        });
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [docId]);

  if (!docId) {
    return (
      <div className="page">
        <p>Missing document ID.</p>
        <Link to="/">Back to documents</Link>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <p>{error}</p>
        <Link to="/">Back to documents</Link>
      </div>
    );
  }

  if (loading || !doc) {
    return (
      <div className="page">
        <p>Loading…</p>
      </div>
    );
  }

  const handleAsk = (question: string, maxWords?: number) =>
    api.ask(docId, { question, max_words: maxWords ?? undefined });

  return (
    <div className="page page--document">
      <Link to="/" className="page__back">
        ← Documents
      </Link>
      <h1 className="page__title">{doc.filename || docId}</h1>
      <SummaryBlock summary={doc.summary} isCv={doc.is_cv} />
      <AskForm isCv={doc.is_cv} onAsk={handleAsk} />
    </div>
  );
}
