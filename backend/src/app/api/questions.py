"""
Question-answering endpoint — POST /ask.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings
from app.core.dependencies import get_doc_store, get_app_settings
from app.schemas.requests import QuestionRequest
from app.schemas.responses import QuestionResponse
from app.services.rag_service import answer_question
from document_store import DocumentStore

router = APIRouter(tags=["questions"])


@router.post("/ask", response_model=QuestionResponse)
async def ask(
    request: QuestionRequest,
    doc_store: DocumentStore = Depends(get_doc_store),
    settings: Settings = Depends(get_app_settings),
):
    """Ask a question about the loaded document.

    Returns an answer with source citations (page numbers).
    All inference happens locally via Ollama.
    """
    if not doc_store.is_loaded:
        raise HTTPException(
            status_code=400,
            detail="No document loaded. Please upload a PDF first.",
        )

    try:
        return answer_question(
            question=request.question,
            doc_store=doc_store,
            settings=settings,
            save_audio=request.save_audio,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
