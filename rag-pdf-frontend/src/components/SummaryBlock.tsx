interface SummaryBlockProps {
  summary: string | null;
  isCv: boolean;
}

export function SummaryBlock({ summary, isCv }: SummaryBlockProps) {
  if (summary == null) {
    return (
      <section className="summary-block">
        <p className="summary-block__empty">No summary available.</p>
      </section>
    );
  }

  return (
    <section className="summary-block">
      {isCv && <span className="summary-block__badge">CV</span>}
      <h2 className="summary-block__title">Summary</h2>
      <p className="summary-block__text">{summary}</p>
    </section>
  );
}
