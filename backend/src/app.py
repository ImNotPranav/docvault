"""
DocVault — Privacy-First Document Analysis API

All processing happens locally:
- LLM: Gemma 3 4B via Ollama (local inference)
- Embeddings: HuggingFace sentence-transformers (local)
- Vector DB: FAISS (in-memory, local)
- TTS: pyttsx3 (local)

No document content is ever sent to external APIs or cloud services.
"""

import os
import httpx
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

import pyttsx3

from document_store import DocumentStore
from analysis_prompts import get_analysis_prompt, get_available_analyses

load_dotenv()

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
AUDIO_DIR = "audio_outputs"
UPLOAD_DIR = "uploads"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────

app = FastAPI(
    title="DocVault API",
    description="Privacy-first document analysis — all processing happens locally.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Global State
# ──────────────────────────────────────────────

doc_store = DocumentStore()

# ──────────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────────

class Source(BaseModel):
    page: int
    content_preview: str
    relevance_score: float

class QuestionRequest(BaseModel):
    question: str
    save_audio: bool = False

class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source] = []
    audio_file: Optional[str] = None

class AnalysisRequest(BaseModel):
    analysis_type: str
    document_type: Optional[str] = None

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

# ──────────────────────────────────────────────
# LLM Helpers
# ──────────────────────────────────────────────

def load_llm() -> ChatOllama:
    """Load the local Ollama LLM. No API keys needed."""
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.2,
        streaming=True
    )


def format_context_with_pages(docs) -> str:
    """Format retrieved documents with page numbers for citation.
    
    Each chunk is labeled with its source page number so the LLM
    can reference specific pages in its answer.
    """
    formatted_chunks = []
    for doc in docs:
        page_num = doc.metadata.get("page_display", doc.metadata.get("page", "?"))
        filename = doc.metadata.get("filename", "document")
        formatted_chunks.append(
            f"[Page {page_num} — {filename}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(formatted_chunks)


def extract_sources(docs_with_scores: list) -> list[Source]:
    """Extract structured source citations from retrieved documents.
    
    Returns a deduplicated list of sources sorted by page number.
    """
    seen_pages = set()
    sources = []
    
    for doc, score in docs_with_scores:
        page_num = doc.metadata.get("page_display", doc.metadata.get("page", 0) + 1)
        
        if page_num in seen_pages:
            continue
        seen_pages.add(page_num)
        
        # Create a short preview of the chunk content
        preview = doc.page_content[:150].strip()
        if len(doc.page_content) > 150:
            preview += "..."
        
        sources.append(Source(
            page=page_num,
            content_preview=preview,
            relevance_score=round(float(1 / (1 + score)), 3),  # Convert distance to similarity
        ))
    
    # Sort by page number for readability
    sources.sort(key=lambda s: s.page)
    return sources


# ──────────────────────────────────────────────
# RAG Chain Builder
# ──────────────────────────────────────────────

RAG_SYSTEM_PROMPT = """You are DocVault, a privacy-first document analysis assistant.

CRITICAL RULES:
1. Answer ONLY using the provided context. Never use external knowledge.
2. If the answer cannot be found in the context, explicitly say: "This information is not present in the provided documents."
3. For every claim you make, reference the source by page number.
4. Be precise, thorough, and cite evidence over speculation.
5. Never make up facts or hallucinate information.

Format your response clearly. When referencing sources, mention the page number naturally within your answer (e.g., "According to Page 3, ..." or "As stated on Page 7, ...").

Context (with page numbers):
{context}

Question: {question}"""


ANALYSIS_SYSTEM_PROMPT = """You are DocVault, a privacy-first document analysis assistant.

CRITICAL RULES:
1. Answer ONLY using the provided context. Never use external knowledge.
2. If the information cannot be found in the context, explicitly say so.
3. For every claim, cite the page number where you found the information.
4. Be thorough, precise, and structured in your analysis.
5. Never make up facts or hallucinate information.

Context (with page numbers):
{context}

Analysis Task: {question}"""


def build_rag_chain(llm: ChatOllama, retriever, system_prompt: str = RAG_SYSTEM_PROMPT):
    """Build a RAG chain with context-restricted answering and citation support."""
    
    prompt = ChatPromptTemplate.from_template(system_prompt)
    
    chain = (
        {
            "context": retriever | format_context_with_pages,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain


# ──────────────────────────────────────────────
# TTS Helper
# ──────────────────────────────────────────────

def save_audio(text: str) -> str:
    """Save text as audio file using local TTS engine."""
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = os.path.join(AUDIO_DIR, f"response_{timestamp}.wav")
    
    engine.save_to_file(text, audio_path)
    engine.runAndWait()
    engine.stop()
    
    return audio_path


# ──────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────

@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint — check API status."""
    docs = doc_store.get_document_list()
    loaded = docs[-1]["filename"] if docs else None
    return StatusResponse(
        status="online",
        message="DocVault API is running — all processing is local",
        pdf_loaded=loaded,
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health: Ollama availability and model status."""
    ollama_available = False
    model_loaded = False
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check if Ollama is running
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                ollama_available = True
                # Check if our model is available
                models = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                model_loaded = any(
                    OLLAMA_MODEL in name for name in model_names
                )
    except Exception:
        pass

    return HealthResponse(
        status="ready" if (ollama_available and model_loaded and doc_store.is_loaded) else "setup_needed",
        ollama_available=ollama_available,
        model_loaded=model_loaded,
        model_name=OLLAMA_MODEL,
        documents_loaded=doc_store.get_document_list(),
    )


@app.post("/upload-pdf", response_model=StatusResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    document_type: str = Form("general"),
):
    """Upload and process a PDF document.
    
    Creates embeddings and indexes the document for retrieval.
    All processing happens locally — no data leaves the machine.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    valid_types = ["contract", "financial", "compliance", "medical", "general"]
    if document_type not in valid_types:
        document_type = "general"
    
    try:
        # Save uploaded file locally
        pdf_path = os.path.join(UPLOAD_DIR, file.filename)
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
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
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
        # Get source documents with relevance scores for citations
        docs_with_scores = doc_store.search_with_scores(request.question, k=5)
        sources = extract_sources(docs_with_scores)
        
        # Build and invoke RAG chain
        llm = load_llm()
        retriever = doc_store.get_retriever(k=5)
        chain = build_rag_chain(llm, retriever)
        
        answer_text = chain.invoke(request.question)
        
        # Optional audio (fully local TTS)
        audio_file = None
        if request.save_audio:
            audio_path = save_audio(answer_text)
            audio_file = os.path.basename(audio_path)
        
        return QuestionResponse(
            question=request.question,
            answer=answer_text,
            sources=sources,
            audio_file=audio_file,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.post("/analyze", response_model=QuestionResponse)
async def analyze_document(request: AnalysisRequest):
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
        # Get source documents with relevance scores for citations
        docs_with_scores = doc_store.search_with_scores(prompt_text, k=5)
        sources = extract_sources(docs_with_scores)
        
        # Build and invoke analysis chain
        llm = load_llm()
        retriever = doc_store.get_retriever(k=5)
        chain = build_rag_chain(llm, retriever, system_prompt=ANALYSIS_SYSTEM_PROMPT)
        
        answer_text = chain.invoke(prompt_text)
        
        return QuestionResponse(
            question=prompt_text,
            answer=answer_text,
            sources=sources,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running analysis: {str(e)}")


@app.get("/analyses", response_model=AvailableAnalysesResponse)
async def get_analyses():
    """Get available analysis types for the currently loaded document type."""
    doc_type = doc_store.get_document_type()
    analyses = get_available_analyses(doc_type)
    return AvailableAnalysesResponse(
        document_type=doc_type,
        analyses=[AnalysisOption(**a) for a in analyses],
    )


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Download a generated audio file."""
    audio_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(audio_path, media_type="audio/wav", filename=filename)


@app.get("/list-audio")
async def list_audio_files():
    """List all generated audio files."""
    if not os.path.exists(AUDIO_DIR):
        return {"audio_files": [], "count": 0}
    files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]
    files.sort(reverse=True)
    return {"audio_files": files, "count": len(files)}


@app.delete("/audio/{filename}")
async def delete_audio(filename: str):
    """Delete a specific audio file."""
    audio_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    try:
        os.remove(audio_path)
        return {"status": "success", "message": f"Deleted {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current system status."""
    docs = doc_store.get_document_list()
    loaded = docs[-1]["filename"] if docs else None
    return StatusResponse(
        status="ready" if doc_store.is_loaded else "no_document_loaded",
        message="System ready for questions" if doc_store.is_loaded else "Upload a document to start",
        pdf_loaded=loaded,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)