"""
Health and status endpoints — GET /, /health, /status.
"""

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.core.dependencies import get_doc_store, get_app_settings
from app.schemas.responses import StatusResponse, HealthResponse
from app.services.ollama_service import check_ollama_health
from document_store import DocumentStore

router = APIRouter(tags=["health"])


@router.get("/", response_model=StatusResponse)
async def root(doc_store: DocumentStore = Depends(get_doc_store)):
    """Root endpoint — check API status."""
    docs = doc_store.get_document_list()
    loaded = docs[-1]["filename"] if docs else None
    return StatusResponse(
        status="online",
        message="DocVault API is running — all processing is local",
        pdf_loaded=loaded,
    )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    doc_store: DocumentStore = Depends(get_doc_store),
    settings: Settings = Depends(get_app_settings),
):
    """Check system health: Ollama availability and model status."""
    ollama_available, model_loaded = await check_ollama_health(settings)

    return HealthResponse(
        status="ready" if (ollama_available and model_loaded and doc_store.is_loaded) else "setup_needed",
        ollama_available=ollama_available,
        model_loaded=model_loaded,
        model_name=settings.OLLAMA_MODEL,
        documents_loaded=doc_store.get_document_list(),
    )


@router.get("/status", response_model=StatusResponse)
async def get_status(doc_store: DocumentStore = Depends(get_doc_store)):
    """Get current system status."""
    docs = doc_store.get_document_list()
    loaded = docs[-1]["filename"] if docs else None
    return StatusResponse(
        status="ready" if doc_store.is_loaded else "no_document_loaded",
        message="System ready for questions" if doc_store.is_loaded else "Upload a document to start",
        pdf_loaded=loaded,
    )
