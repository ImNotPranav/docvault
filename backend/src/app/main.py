"""
DocVault — Privacy-First Document Analysis API

All processing happens locally:
- LLM: Gemma 3 4B via Ollama (local inference)
- Embeddings: HuggingFace sentence-transformers (local)
- Vector DB: FAISS (in-memory, local)
- TTS: pyttsx3 (local)

No document content is ever sent to external APIs or cloud services.
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import health, documents, questions, analysis, audio
from document_store import DocumentStore

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — initialize and tear down shared resources."""
    settings = get_settings()
    settings.ensure_directories()

    # Create the singleton DocumentStore and attach to app state
    app.state.doc_store = DocumentStore()

    yield

    # Cleanup (if needed in the future)


app = FastAPI(
    title="DocVault API",
    description="Privacy-first document analysis — all processing happens locally.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all route handlers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(questions.router)
app.include_router(analysis.router)
app.include_router(audio.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
