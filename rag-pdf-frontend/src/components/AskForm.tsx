import { useState } from 'react';
import type { AskResponse } from '../api/types';

interface AskFormProps {
  isCv: boolean;
  onAsk: (question: string, maxWords?: number) => Promise<AskResponse>;
}

export function AskForm({ isCv, onAsk }: AskFormProps) {
  const [question, setQuestion] = useState('');
  const [maxWords, setMaxWords] = useState<number | ''>(isCv ? 100 : '');
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (!q || loading) return;
    setError(null);
    setAnswer(null);
    setLoading(true);
    try {
      const res = await onAsk(q, maxWords === '' ? undefined : Number(maxWords));
      setAnswer(res.answer);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Request failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="ask-form">
      <h2 className="ask-form__title">Ask a question</h2>
      <form onSubmit={handleSubmit} className="ask-form__form">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. What are the main responsibilities?"
          rows={3}
          className="ask-form__input"
          disabled={loading}
        />
        {isCv && (
          <label className="ask-form__max-words">
            Max words (optional)
            <input
              type="number"
              min={1}
              max={500}
              value={maxWords}
              onChange={(e) =>
                setMaxWords(e.target.value === '' ? '' : Number(e.target.value))
              }
              className="ask-form__max-words-input"
            />
          </label>
        )}
        <button type="submit" disabled={loading || !question.trim()} className="ask-form__submit">
          {loading ? 'Asking…' : 'Ask'}
        </button>
      </form>
      {error && <p className="ask-form__error">{error}</p>}
      {answer != null && (
        <div className="ask-form__answer">
          <h3>Answer</h3>
          <p>{answer}</p>
        </div>
      )}
    </section>
  );
}
