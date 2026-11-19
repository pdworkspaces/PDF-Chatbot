import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from backend.config import UPLOAD_DIR, MAX_UPLOAD_MB
from backend.services.rag_service import ingest_pdf
from backend.services.vector_service import delete_document_vectors
from backend.graph.rag_graph import rag_graph
from backend.database import (
    save_document, document_exists, save_chat, get_history,
    delete_document_record
)

router = APIRouter(prefix="/api", tags=["PDF Chatbot"])

class ChatRequest(BaseModel):
    document_id: str
    question: str = Field(min_length=1, max_length=4000)
    provider: str = "ollama"

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"PDF exceeds {MAX_UPLOAD_MB} MB.")
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

    document_id = str(uuid.uuid4())
    safe_path = UPLOAD_DIR / f"{document_id}.pdf"

    try:
        safe_path.write_bytes(content)
        result = ingest_pdf(str(safe_path), document_id)
        save_document(document_id, filename, result["total_pages"], result["total_chunks"])
        return {
            "message": "PDF processed successfully",
            "document_id": document_id,
            "filename": filename,
            **result
        }
    except ValueError as exc:
        safe_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        safe_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=502,
            detail="PDF processing failed. Check that Ollama is running and the embedding model is installed."
        )

@router.post("/chat")
def chat(request: ChatRequest):
    if request.provider not in ("ollama", "gemini"):
        raise HTTPException(status_code=400, detail="Provider must be ollama or gemini.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not document_exists(request.document_id):
        raise HTTPException(status_code=404, detail="Document not found. Upload it again.")

    try:
        result = rag_graph.invoke({
            "question": request.question.strip(),
            "document_id": request.document_id,
            "provider": request.provider,
            "documents": [],
            "answer": ""
        })
        answer = result["answer"]
        sources = sorted({
            int(doc.metadata.get("page", 0)) + 1
            for doc in result["documents"]
        })
        save_chat(request.document_id, request.question, answer, request.provider, sources)
        return {
            "question": request.question,
            "answer": answer,
            "provider": request.provider,
            "sources": sources
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Answer generation failed. Check the selected model and its connection/API key."
        )

@router.get("/history/{document_id}")
def history(document_id: str):
    if not document_exists(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    return get_history(document_id)

@router.delete("/documents/{document_id}")
def delete_document(document_id: str):
    if not document_exists(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        delete_document_vectors(document_id)
        (UPLOAD_DIR / f"{document_id}.pdf").unlink(missing_ok=True)
        delete_document_record(document_id)
        return {"message": "Document and its chat history deleted."}
    except Exception:
        raise HTTPException(status_code=500, detail="Could not delete document.")
