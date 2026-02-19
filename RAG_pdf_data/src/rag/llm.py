"""LLM client (Groq) for summary, CV detection, and Q&A."""

from app.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, GROQ_API_KEY

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set. Cannot use LLM.")
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            raise ImportError(
                "langchain-groq is required. Install with: pip install langchain-groq"
            ) from None
        _llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
        )
    return _llm


def invoke_llm(prompt: str, system: str | None = None) -> str:
    """
    Send a prompt to the LLM and return the response text.

    Args:
        prompt: User/content prompt.
        system: Optional system message.

    Returns:
        Generated text (stripped).
    """
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = _get_llm()
    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))
    response = llm.invoke(messages)
    return (response.content or "").strip()
