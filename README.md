# DocVault — Privacy-First Document Analysis

> Analyze contracts, financial reports, compliance documents, and more — **100% locally**. No document content ever leaves your device.

## Architecture

```
Document → PDF Loader → Chunker → Local Embeddings → FAISS → Retriever → Local LLM (Gemma 3 4B) → Answer + Citations
```

All components run locally:
- **LLM**: Gemma 3 4B via [Ollama](https://ollama.com) (local inference)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace, runs locally)
- **Vector DB**: FAISS (in-memory, local)
- **TTS**: pyttsx3 (offline text-to-speech)

## Prerequisites

1. **Python 3.10+**
2. **Node.js 18+** (for the frontend)
3. **Ollama** — Install from [ollama.com](https://ollama.com)

## Setup

### 1. Install & Start Ollama

```bash
# Install Ollama (see https://ollama.com for platform-specific instructions)

# Pull the Gemma 3 4B model (~3GB download, runs on most modern hardware)
ollama pull gemma3:4b

# Verify it's running
ollama list
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
cd src
python app.py
```

The backend will start at `http://localhost:8000`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will start at `http://localhost:5173`.

## Usage

1. Open `http://localhost:5173` in your browser
2. Select a **document type** (Contract, Financial, Compliance, Medical, or General)
3. Upload a PDF
4. Use **Quick Analysis** buttons for structured insights, or ask free-form questions
5. Every answer includes **page-level source citations** you can verify

## Document Types & Analysis Workflows

| Document Type | Available Analyses |
|---|---|
| **Contract** | Summary, Obligations, Deadlines, Termination Clauses, Penalties, Renewal Conditions |
| **Financial** | Summary, Key Metrics, Risk Factors, Trends & Projections |
| **Compliance** | Summary, Requirements, Deadlines, Issues & Violations |
| **Medical** | Summary, Key Findings, Recommendations |
| **General** | Summary, Key Points |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | System health check (Ollama + model status) |
| `POST` | `/upload-pdf` | Upload and process a PDF document |
| `POST` | `/ask` | Ask a question (returns answer + source citations) |
| `POST` | `/analyze` | Run a pre-built analysis workflow |
| `GET` | `/analyses` | Get available analysis types for loaded document |
| `GET` | `/status` | Current system status |

## Privacy Guarantees

- ✅ All LLM inference runs locally via Ollama
- ✅ All embeddings are computed locally
- ✅ No API keys required (no external services)
- ✅ No telemetry or tracking
- ✅ No internet required after initial setup
- ✅ Documents are stored only on your local filesystem

## Tech Stack

**Backend**: Python, FastAPI, LangChain, FAISS, Ollama, pyttsx3  
**Frontend**: React, TypeScript, Vite, TailwindCSS  
**LLM**: Gemma 3 4B (via Ollama)  
**Embeddings**: sentence-transformers/all-MiniLM-L6-v2
