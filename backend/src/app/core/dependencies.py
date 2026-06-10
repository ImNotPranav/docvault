"""
FastAPI dependency-injection providers.

These functions are used with ``Depends()`` in route handlers to inject
shared services (DocumentStore, Settings) without relying on module-level
globals.
"""

from fastapi import Request

from app.core.config import Settings, get_settings
from document_store import DocumentStore


def get_doc_store(request: Request) -> DocumentStore:
    """Return the singleton DocumentStore attached during app lifespan."""
    return request.app.state.doc_store


def get_app_settings() -> Settings:
    """Return the cached application Settings."""
    return get_settings()
