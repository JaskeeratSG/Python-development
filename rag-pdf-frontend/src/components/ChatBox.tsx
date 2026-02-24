import { useState, useRef, useEffect } from 'react';
import type { AskResponse } from '../api/types';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface ChatBoxProps {
  messages: ChatMessage[];
  onSend: (question: string, maxWords?: number) => Promise<AskResponse>;
  isCv: boolean;
  disabled?: boolean;
}

export function ChatBox({
  messages,
  onSend,
  isCv,
  disabled = false,
}: ChatBoxProps) {
  const [input, setInput] = useState('');
  const [maxWords, setMaxWords] = useState<number | ''>(isCv ? 100 : '');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    setMaxWords(isCv ? 100 : '');
  }, [isCv]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || sending || disabled) return;
    setError(null);
    setSending(true);
    try {
      await onSend(
        q,
        maxWords === '' ? undefined : Number(maxWords)
      );
      setInput('');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Request failed.');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="chat-box">
      <div className="chat-box__messages">
        {messages.length === 0 && (
          <p className="chat-box__placeholder">
            Ask a question about the selected document. Answers are generated from the PDF content.
          </p>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-box__message chat-box__message--${msg.role}`}
          >
            <span className="chat-box__message-role">
              {msg.role === 'user' ? 'You' : 'Assistant'}
            </span>
            <p className="chat-box__message-content">{msg.content}</p>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSubmit} className="chat-box__form">
        <label className="chat-box__max-words">
          Word limit (optional)
          <input
            type="number"
            min={1}
            max={500}
            value={maxWords}
            onChange={(e) =>
              setMaxWords(e.target.value === '' ? '' : Number(e.target.value))
            }
            placeholder="No limit"
            className="chat-box__max-words-input"
          />
        </label>
        <div className="chat-box__input-row">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question…"
            rows={2}
            className="chat-box__input"
            disabled={disabled || sending}
          />
          <button
            type="submit"
            disabled={disabled || sending || !input.trim()}
            className="chat-box__send"
          >
            {sending ? '…' : 'Send'}
          </button>
        </div>
        {error && <p className="chat-box__error">{error}</p>}
      </form>
    </div>
  );
}
