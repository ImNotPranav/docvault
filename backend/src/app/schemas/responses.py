"""
Response models for API endpoints.

Moved verbatim from app.py — no field changes.
"""

from typing import Optional

from pydantic import BaseModel


class Source(BaseModel):
    page: int
    content_preview: str
    relevance_score: float


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source] = []
    audio_file: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    message: str
    pdf_loaded: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    ollama_available: bool
    model_loaded: bool
    model_name: str
    documents_loaded: list[dict] = []


class AnalysisOption(BaseModel):
    type: str
    label: str
    icon: str


class AvailableAnalysesResponse(BaseModel):
    document_type: str
    analyses: list[AnalysisOption]
