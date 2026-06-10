"""
Ollama LLM service — instantiation and health checking.

Extracted from app.py. The load_llm() logic is identical; check_ollama_health()
is extracted from the health_check endpoint to keep the route handler thin.
"""

import httpx
from langchain_ollama import ChatOllama

from app.core.config import Settings


def load_llm(settings: Settings) -> ChatOllama:
    """Load the local Ollama LLM. No API keys needed."""
    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.2,
        streaming=True,
    )


async def check_ollama_health(settings: Settings) -> tuple[bool, bool]:
    """Check Ollama availability and whether the configured model is loaded.

    Returns:
        (ollama_available, model_loaded) tuple of booleans.
    """
    ollama_available = False
    model_loaded = False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                ollama_available = True
                models = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                model_loaded = any(
                    settings.OLLAMA_MODEL in name for name in model_names
                )
    except Exception:
        pass

    return ollama_available, model_loaded
