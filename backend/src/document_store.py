"""
Document Store — manages document ingestion, vector storage, and retrieval.

Designed to support single-document usage today, with architecture that
makes future multi-document support straightforward.

All processing is fully local — no external API calls.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class DocumentMetadata:
    """Metadata for an ingested document."""
    doc_id: str
    filename: str
    file_path: str
    document_type: str  # "contract", "financial", "compliance", "medical", "general"
    page_count: int
    chunk_count: int
    ingested_at: datetime = field(default_factory=datetime.now)


class DocumentStore:
    """Manages document ingestion and FAISS vector store.
    
    Currently supports single-document workflows. The architecture
    (document tracking by ID, per-document metadata, structured chunk
    metadata) is designed so that multi-document support can be added
    later without breaking changes.
    
    All processing is fully local:
    - Embeddings: HuggingFace sentence-transformers (downloaded once, runs locally)
    - Vector Store: FAISS (in-memory, fully local)
    - PDF Loading: PyPDFLoader (local file parsing)
    """

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.documents: dict[str, DocumentMetadata] = {}
        self.vectorstore: Optional[FAISS] = None
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

    def add_document(
        self,
        doc_id: str,
        file_path: str,
        document_type: str = "general",
    ) -> DocumentMetadata:
        """Ingest a PDF document into the vector store.
        
        Args:
            doc_id: Unique identifier for this document.
            file_path: Absolute path to the PDF file.
            document_type: Type of document for analysis prompt selection.
            
        Returns:
            DocumentMetadata for the ingested document.
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF not found at: {file_path}")

        # Load PDF pages
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        # Enrich page metadata with document info
        for page in pages:
            page.metadata["doc_id"] = doc_id
            page.metadata["document_type"] = document_type
            page.metadata["filename"] = os.path.basename(file_path)
            # PyPDFLoader already sets 'page' (0-indexed) and 'source'

        # Split into chunks (preserves metadata from parent pages)
        chunks = self._splitter.split_documents(pages)

        # Add chunk-level metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            # Ensure page number is human-readable (1-indexed)
            if "page" in chunk.metadata:
                chunk.metadata["page_display"] = chunk.metadata["page"] + 1

        # Build or extend the vector store
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings,
            )
        else:
            # Future: this path enables multi-document support
            new_store = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings,
            )
            self.vectorstore.merge_from(new_store)

        # Track document metadata
        metadata = DocumentMetadata(
            doc_id=doc_id,
            filename=os.path.basename(file_path),
            file_path=file_path,
            document_type=document_type,
            page_count=len(pages),
            chunk_count=len(chunks),
        )
        self.documents[doc_id] = metadata

        return metadata

    def get_retriever(self, k: int = 5):
        """Get a retriever for the current vector store.
        
        Args:
            k: Number of documents to retrieve per query.
            
        Returns:
            A LangChain retriever instance.
            
        Raises:
            ValueError: If no documents have been ingested.
        """
        if self.vectorstore is None:
            raise ValueError("No documents loaded. Please upload a document first.")
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

    def search_with_scores(self, query: str, k: int = 5):
        """Search for relevant chunks and return them with relevance scores.
        
        This is used for building structured source citations.
        
        Args:
            query: The search query.
            k: Number of results to return.
            
        Returns:
            List of (Document, score) tuples sorted by relevance.
        """
        if self.vectorstore is None:
            raise ValueError("No documents loaded. Please upload a document first.")
        return self.vectorstore.similarity_search_with_score(query, k=k)

    def get_document_list(self) -> list[dict]:
        """Get a list of all ingested documents with their metadata.
        
        Returns:
            List of document metadata dicts.
        """
        return [
            {
                "doc_id": meta.doc_id,
                "filename": meta.filename,
                "document_type": meta.document_type,
                "page_count": meta.page_count,
                "chunk_count": meta.chunk_count,
                "ingested_at": meta.ingested_at.isoformat(),
            }
            for meta in self.documents.values()
        ]

    def get_document_type(self) -> str:
        """Get the document type of the most recently loaded document.
        
        Returns the first document's type, or 'general' if none loaded.
        """
        if not self.documents:
            return "general"
        # Return the most recent document's type
        return list(self.documents.values())[-1].document_type

    def clear(self):
        """Remove all documents and reset the vector store."""
        self.documents.clear()
        self.vectorstore = None

    @property
    def is_loaded(self) -> bool:
        """Check if any documents have been ingested."""
        return self.vectorstore is not None and len(self.documents) > 0
