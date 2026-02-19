"""Request/response models for the RAG API."""

from typing import Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request body for POST /api/documents/{doc_id}/ask."""

    question: str = Field(..., min_length=1)
    max_words: Optional[int] = Field(None, ge=1, le=500, description="For CV: max words in answer.")


class AskResponse(BaseModel):
    """Response for ask endpoint."""

    answer: str
    is_cv: bool
    doc_id: str


class DocumentSummary(BaseModel):
    """Summary and metadata for one document."""

    doc_id: str
    filename: str
    is_cv: bool
    summary: Optional[str] = None


class UploadResponse(BaseModel):
    """Response after PDF upload."""

    doc_id: str
    filename: str
    is_cv: bool
    summary: Optional[str] = None
