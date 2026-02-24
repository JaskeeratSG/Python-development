import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { DocumentSummary } from '../api/types';
import type { ChatMessage } from '../components/ChatBox';
import { DocumentDropdown } from '../components/DocumentDropdown';
import { UploadZone } from '../components/UploadZone';
import { ChatBox } from '../components/ChatBox';
import { SummaryPanel } from '../components/SummaryPanel';

export function HomePage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocId, setSelectedDocId] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocs = async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await api.listDocuments();
      setDocuments(list);
      if (!list.some((d) => d.doc_id === selectedDocId)) {
        setSelectedDocId('');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load documents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  useEffect(() => {
    setMessages([]);
  }, [selectedDocId]);

  const handleUpload = async (file: File) => {
    await api.upload(file);
    await fetchDocs();
  };

  const selectedDoc = documents.find((d) => d.doc_id === selectedDocId);

  const handleSendMessage = async (question: string, maxWords?: number) => {
    if (!selectedDocId) return {} as Awaited<ReturnType<typeof api.ask>>;
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: question,
    };
    setMessages((m) => [...m, userMsg]);
    const res = await api.ask(selectedDocId, {
      question,
      max_words: maxWords ?? undefined,
    });
    const assistantMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: res.answer,
    };
    setMessages((m) => [...m, assistantMsg]);
    return res;
  };

  return (
    <div className="page page--home">
      <h1 className="page__title">RAG PDF</h1>
      <UploadZone onUpload={handleUpload} />
      {error && <p className="page__error">{error}</p>}
      <div className="home-grid">
        <div className="home-grid__left">
          <DocumentDropdown
            documents={documents}
            value={selectedDocId}
            onChange={setSelectedDocId}
            disabled={loading}
            placeholder="Select a document to ask questions"
          />
          <ChatBox
            messages={messages}
            onSend={handleSendMessage}
            isCv={selectedDoc?.is_cv ?? false}
            disabled={!selectedDocId}
          />
        </div>
        <div className="home-grid__right">
          <SummaryPanel doc={selectedDoc ?? null} />
        </div>
      </div>
    </div>
  );
}
