"""
Document upload service — orchestrates file saving and ingestion.

Extracted from the POST /upload-pdf endpoint handler.
"""

import os
from datetime import datetime

from fastapi import UploadFile

from app.core.config import Settings
from app.core.constants import VALID_DOCUMENT_TYPES
from app.schemas.responses import StatusResponse
from document_store import DocumentStore


async def process_upload(
    file: UploadFile,
    document_type: str,
    doc_store: DocumentStore,
    settings: Settings,
) -> StatusResponse:
    """Save uploaded PDF to disk and ingest into the document store.

    Args:
        file: The uploaded PDF file.
        document_type: Document classification for analysis prompts.
        doc_store: The application's DocumentStore instance.
        settings: Application settings (for upload directory path).

    Returns:
        StatusResponse with processing results.
    """
    if document_type not in VALID_DOCUMENT_TYPES:
        document_type = "general"

    # Save uploaded file locally
    pdf_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(pdf_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Clear previous documents (single-doc mode for now)
    doc_store.clear()

    # Ingest document — all local processing
    doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    metadata = doc_store.add_document(
        doc_id=doc_id,
        file_path=pdf_path,
        document_type=document_type,
    )

    return StatusResponse(
        status="success",
        message=(
            f"Document processed successfully. "
            f"{metadata.page_count} pages, {metadata.chunk_count} chunks created. "
            f"Type: {document_type}."
        ),
        pdf_loaded=file.filename,
    )
