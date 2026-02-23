"""Short summary generation from document text."""

from rag.llm import invoke_llm

# Use more text for summary so key points aren't cut off
SUMMARY_MAX_CHARS = 18_000


def summarize_text(text: str, max_sentences: int = 5) -> str:
    """
    Generate a clear, substantive summary of the document.

    Args:
        text: Full or truncated document text.
        max_sentences: Target number of sentences (default 5).

    Returns:
        Summary string.
    """
    if not text or not text.strip():
        return ""
    truncated = text.strip()[:SUMMARY_MAX_CHARS]
    system = (
        "You are an expert at summarizing documents. Your summary must:\n"
        "1. State the main topic or purpose in the first sentence.\n"
        "2. Include the most important points, facts, or findings.\n"
        "3. If the document has conclusions or recommendations, include them.\n"
        f"4. Be exactly {max_sentences} sentences (or fewer if the document is very short).\n"
        "5. Use clear, professional language. No preamble like 'This document is about...'—start directly with the content."
    )
    prompt = (
        "Summarize the following document. Capture the main idea and key information.\n\n"
        "---\n"
        f"{truncated}\n"
        "---\n\n"
        "Summary:"
    )
    return invoke_llm(prompt, system=system)
