"""
RAG service — chain building and question/analysis orchestration.

This module consolidates the duplicated orchestration logic that previously
appeared in both the /ask and /analyze endpoint handlers. The private
_invoke_rag() method encapsulates the shared pattern:
    search_with_scores → extract_sources → build_chain → invoke → return

Public methods:
    answer_question()  — used by POST /ask
    run_analysis()     — used by POST /analyze
"""

import os
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.core.config import Settings
from app.prompts.rag_prompts import RAG_SYSTEM_PROMPT, ANALYSIS_SYSTEM_PROMPT
from app.schemas.responses import QuestionResponse
from app.utils.citations import format_context_with_pages, extract_sources
from app.services.ollama_service import load_llm
from app.services.audio_service import save_audio as _save_audio
from document_store import DocumentStore


def build_rag_chain(llm, retriever, system_prompt: str = RAG_SYSTEM_PROMPT):
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


def _invoke_rag(
    query: str,
    doc_store: DocumentStore,
    settings: Settings,
    system_prompt: str,
) -> tuple[str, list]:
    """Shared RAG invocation logic.

    Returns:
        (answer_text, sources) tuple.
    """
    # Get source documents with relevance scores for citations
    docs_with_scores = doc_store.search_with_scores(query, k=5)
    sources = extract_sources(docs_with_scores)

    # Build and invoke RAG chain
    llm = load_llm(settings)
    retriever = doc_store.get_retriever(k=5)
    chain = build_rag_chain(llm, retriever, system_prompt=system_prompt)

    answer_text = chain.invoke(query)

    return answer_text, sources


def answer_question(
    question: str,
    doc_store: DocumentStore,
    settings: Settings,
    save_audio: bool = False,
) -> QuestionResponse:
    """Answer a question using the RAG pipeline.

    This replaces the orchestration logic that was in the /ask endpoint.
    """
    answer_text, sources = _invoke_rag(
        query=question,
        doc_store=doc_store,
        settings=settings,
        system_prompt=RAG_SYSTEM_PROMPT,
    )

    # Optional audio (fully local TTS)
    audio_file: Optional[str] = None
    if save_audio:
        audio_path = _save_audio(answer_text, settings.AUDIO_DIR)
        audio_file = os.path.basename(audio_path)

    return QuestionResponse(
        question=question,
        answer=answer_text,
        sources=sources,
        audio_file=audio_file,
    )


def run_analysis(
    prompt_text: str,
    doc_store: DocumentStore,
    settings: Settings,
) -> QuestionResponse:
    """Run a pre-built analysis workflow using the RAG pipeline.

    This replaces the orchestration logic that was in the /analyze endpoint.
    """
    answer_text, sources = _invoke_rag(
        query=prompt_text,
        doc_store=doc_store,
        settings=settings,
        system_prompt=ANALYSIS_SYSTEM_PROMPT,
    )

    return QuestionResponse(
        question=prompt_text,
        answer=answer_text,
        sources=sources,
    )
