"""
Citation and context-formatting utilities.

Extracted from app.py — logic preserved exactly.
"""

from app.schemas.responses import Source


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
