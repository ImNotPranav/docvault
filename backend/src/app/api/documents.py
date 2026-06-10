"""
Document upload endpoint — POST /upload-pdf.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form

from app.core.config import Settings
from app.core.dependencies import get_doc_store, get_app_settings
from app.schemas.responses import StatusResponse
from app.services.document_service import process_upload
from document_store import DocumentStore

router = APIRouter(tags=["documents"])


@router.post("/upload-pdf", response_model=StatusResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    document_type: str = Form("general"),
    doc_store: DocumentStore = Depends(get_doc_store),
    settings: Settings = Depends(get_app_settings),
):
    """Upload and process a PDF document.

    Creates embeddings and indexes the document for retrieval.
    All processing happens locally — no data leaves the machine.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        return await process_upload(
            file=file,
            document_type=document_type,
            doc_store=doc_store,
            settings=settings,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
