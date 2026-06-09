"""Reference standalone RAG pipeline — updated for DocVault (local Ollama).

This file is NOT used at runtime (everything runs through app.py).
It is kept here as a standalone reference and CLI tool for testing
the RAG pipeline outside of the FastAPI server.

All processing is fully local — no external API calls.
"""

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

import pyttsx3
from datetime import datetime


load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def load_pdf(pdf_path: str):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    return loader.load()


def split_docs(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    return splitter.split_documents(documents)


def create_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )
    return vectorstore


def load_llm():
    """Load the local Ollama LLM — no API keys needed."""
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.2,
    )
    return llm


def format_context_with_pages(docs) -> str:
    """Format retrieved documents with page numbers for citation."""
    formatted = []
    for doc in docs:
        page = doc.metadata.get("page", "?")
        page_display = page + 1 if isinstance(page, int) else page
        formatted.append(f"[Page {page_display}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


def create_rag_chain(vectorstore, llm):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    prompt = ChatPromptTemplate.from_template(
        """You are DocVault, a privacy-first document analysis assistant.

CRITICAL RULES:
1. Answer ONLY using the provided context. Never use external knowledge.
2. If the answer cannot be found in the context, explicitly say:
   "This information is not present in the provided documents."
3. For every claim you make, reference the source by page number.
4. Be precise and cite evidence over speculation.

Context (with page numbers):
{context}

Question: {question}"""
    )

    rag_chain = (
        {
            "context": retriever | format_context_with_pages,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


AUDIO_DIR = "audio_outputs"
os.makedirs(AUDIO_DIR, exist_ok=True)


def speak(text: str):
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def save_audio(text: str):
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = os.path.join(AUDIO_DIR, f"response_{timestamp}.wav")

    engine.save_to_file(text, audio_path)
    engine.runAndWait()
    engine.stop()

    print(f"[Audio saved] {audio_path}")


def ask_question(chain, query):
    response = chain.invoke(query)
    # StrOutputParser returns a string directly
    answer_text = response

    print("\nAnswer:\n")
    print(answer_text)
    print("-" * 60)

    speak(answer_text)

    choice = input("Save this response as audio? (y/n): ").strip().lower()
    if choice == "y":
        save_audio(answer_text)


if __name__ == "__main__":
    PDF_PATH = "../data/story.pdf"

    print("Loading PDF...")
    docs = load_pdf(PDF_PATH)

    print("Splitting document...")
    chunks = split_docs(docs)

    print("Creating vector store...")
    vectorstore = create_vector_store(chunks)

    print("Loading local Ollama LLM (Gemma 3 4B)...")
    llm = load_llm()

    print("Building RAG pipeline...")
    rag_chain = create_rag_chain(vectorstore, llm)

    print("\n✅ DocVault RAG system ready! (100% local processing)")
    print("Type a question or 'exit'\n")

    while True:
        q = input("Ask: ")
        if q.lower() == "exit":
            print("Bye!")
            break
        ask_question(rag_chain, q)
