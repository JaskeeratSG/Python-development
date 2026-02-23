"""PDF text extraction."""

from pathlib import Path


def extract_text_from_pdf(file_path: str | Path) -> str:
    """
    Extract raw text from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Concatenated text from all pages.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a PDF or extraction fails.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("File is not a PDF.")

    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf is required. Install with: pip install pypdf") from None

    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    if not parts:
        raise ValueError("No text could be extracted from the PDF.")
    return "\n\n".join(parts)
