"""
Request models for API endpoints.

Moved verbatim from app.py — no field changes.
"""

from typing import Optional

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    save_audio: bool = False


class AnalysisRequest(BaseModel):
    analysis_type: str
    document_type: Optional[str] = None
