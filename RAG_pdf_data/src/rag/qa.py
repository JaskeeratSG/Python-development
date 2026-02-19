"""RAG Q&A: retrieve relevant chunks and generate answer with LLM."""

from app.config import RAG_TOP_K
from rag.llm import invoke_llm
from rag.store import query_chunks


def answer_question(
    doc_id: str,
    question: str,
    max_words: int | None = None,
    top_k: int | None = None,
) -> str:
    """
    Answer a question about a document using retrieved chunks and the LLM.

    Args:
        doc_id: Document ID (Chroma collection).
        question: User question.
        max_words: If set (e.g. for CV), limit answer to this many words.
        top_k: Number of chunks to retrieve (default from config).

    Returns:
        Answer string.
    """
    if not question or not question.strip():
        return ""
    k = top_k if top_k is not None else RAG_TOP_K
    chunks = query_chunks(doc_id, question.strip(), top_k=k)
    context = "\n\n---\n\n".join(chunks) if chunks else ""

    if not context:
        return (
            "No relevant passages were found for this question in the document. "
            "Try rephrasing or asking about a different aspect of the document."
        )

    word_instruction = ""
    if max_words is not None and max_words > 0:
        word_instruction = (
            f" Keep your answer to at most {max_words} words. "
            "Be direct and concise; use short phrases or bullets if helpful."
        )

    system = (
        "You answer questions using ONLY the provided context from the document. "
        "Rules: (1) Base every claim on the context—do not add outside knowledge. "
        "(2) If the context does not contain the answer, say clearly: 'The document does not contain this information.' "
        "(3) Quote or paraphrase from the context when relevant. "
        "(4) Give a direct, complete answer without repeating the question."
        + word_instruction
    )
    prompt = (
        "Context from the document:\n\n"
        f"{context}\n\n"
        "Question: " + question.strip() + "\n\n"
        "Answer (based only on the context above):"
    )
    return invoke_llm(prompt, system=system)
