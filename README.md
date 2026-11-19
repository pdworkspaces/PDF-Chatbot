# AI PDF Chatbot

A beginner-friendly Retrieval-Augmented Generation (RAG) application.

## Features
- Upload PDF files and extract page-level text.
- Split documents into overlapping chunks.
- Generate embeddings locally with Ollama (`nomic-embed-text`).
- Persist vectors in ChromaDB.
- Ask questions using either local Ollama or Google Gemini.
- LangGraph workflow: retrieve → generate.
- FastAPI backend, Streamlit frontend, SQLite chat history.
- Source page numbers returned by the API.

## Architecture

`Streamlit → FastAPI → LangGraph → ChromaDB retrieval → Ollama/Gemini → answer + sources`

The same Ollama embedding model is used regardless of the generation provider. This keeps the vector index compatible when switching between Ollama and Gemini.

## Requirements
- Python 3.10+ (Python 3.11 recommended)
- Ollama installed for local embeddings; Ollama chat model also needed when selecting Ollama.
- Google AI Studio API key if selecting Gemini.

## Setup (Windows PowerShell)

```powershell
# 1. Create and activate environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install packages
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure environment
Copy-Item .env.example .env
# Edit .env and add GOOGLE_API_KEY if you want Gemini.

# 4. Prepare Ollama models
ollama pull nomic-embed-text
ollama pull llama3.2:3b

# Ollama should be running. If needed, open another terminal:
ollama serve
```

## Run locally

Open terminal 1 (project root):

```powershell
uvicorn backend.main:app --reload
```

Open terminal 2 (project root):

```powershell
streamlit run frontend/app.py
```

- Streamlit: http://localhost:8501
- FastAPI docs: http://localhost:8000/docs
- Health: http://localhost:8000/

## API

### Upload
`POST /api/upload` with multipart field `file`.

### Chat
`POST /api/chat`
```json
{
  "document_id": "ID_FROM_UPLOAD",
  "question": "Summarize this PDF",
  "provider": "ollama"
}
```
`provider` can be `ollama` or `gemini`.

### History
`GET /api/history/{document_id}`

### Delete document
`DELETE /api/documents/{document_id}`

## Important notes
- Local ChromaDB, uploaded PDFs and SQLite data are persisted in `data/`.
- This starter project is intended for local learning. It does not include user authentication or multi-tenant authorization.
- Do not expose the API publicly without authentication, rate limits, file scanning, and per-user document authorization.
- Scanned/image-only PDFs need OCR; this version extracts embedded PDF text.
- Gemini usage is subject to Google's current API quotas and pricing.
- Free hosting platforms often have ephemeral disks and sleep limits. Do not rely on local ChromaDB/SQLite/uploads persisting on free hosted instances. For a durable public deployment, use persistent object storage and a managed vector/database service.
