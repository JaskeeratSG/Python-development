"""CV/Resume detection from document text."""

from rag.llm import invoke_llm


def is_cv(text: str) -> bool:
    """
    Classify whether the document is a CV/Resume.

    Args:
        text: Document text (full or a representative sample).

    Returns:
        True if the document appears to be a CV/Resume.
    """
    if not text or not text.strip():
        return False
    sample = text.strip()[:6000]
    system = (
        "You classify documents. Answer only with exactly 'yes' or 'no'. "
        "No explanation."
    )
    prompt = (
        "Is the following document a CV, resume, or curriculum vitae "
        "(i.e. a person's work/education history for job applications)?\n\n"
        f"{sample}"
    )
    answer = invoke_llm(prompt, system=system).lower()
    return "yes" in answer
