"""
Analysis endpoints — POST /analyze, GET /analyses.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings
from app.core.dependencies import get_doc_store, get_app_settings
from app.schemas.requests import AnalysisRequest
from app.schemas.responses import QuestionResponse, AvailableAnalysesResponse, AnalysisOption
from app.services.rag_service import run_analysis
from document_store import DocumentStore
from analysis_prompts import get_analysis_prompt, get_available_analyses

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=QuestionResponse)
async def analyze_document(
    request: AnalysisRequest,
    doc_store: DocumentStore = Depends(get_doc_store),
    settings: Settings = Depends(get_app_settings),
):
    """Run a pre-built analysis workflow on the loaded document.

    Uses document-type-specific prompts for structured analysis.
    All inference happens locally via Ollama.
    """
    if not doc_store.is_loaded:
        raise HTTPException(
            status_code=400,
            detail="No document loaded. Please upload a PDF first.",
        )

    # Use the document's type if not specified
    document_type = request.document_type or doc_store.get_document_type()

    # Get the analysis prompt
    prompt_text = get_analysis_prompt(document_type, request.analysis_type)
    if not prompt_text:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown analysis type '{request.analysis_type}' for document type '{document_type}'.",
        )

    try:
        return run_analysis(
            prompt_text=prompt_text,
            doc_store=doc_store,
            settings=settings,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running analysis: {str(e)}")


@router.get("/analyses", response_model=AvailableAnalysesResponse)
async def get_analyses(doc_store: DocumentStore = Depends(get_doc_store)):
    """Get available analysis types for the currently loaded document type."""
    doc_type = doc_store.get_document_type()
    analyses = get_available_analyses(doc_type)
    return AvailableAnalysesResponse(
        document_type=doc_type,
        analyses=[AnalysisOption(**a) for a in analyses],
    )
