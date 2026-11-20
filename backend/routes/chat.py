
import uuid
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import TypedDict, List, Any
from backend.config import UPLOAD_DIR, MAX_UPLOAD_MB
from backend.services.rag_service import ingest_pdf
from backend.services.vector_service import delete_document_vectors
from backend.graph.rag_graph import rag_graph, RAGState
from backend.database import (
    save_document,
    document_exists,
    save_chat,
    get_history,
    delete_document_record
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["PDF Chatbot"])

class RAGState(TypedDict):
    question: str
    document_id: str
    provider: str
    documents: List[Any]
    context: str
    source_pages: List[int]
    answer: str
class ChatRequest(BaseModel):
    document_id: str
    question: str = Field(min_length=1, max_length=4000)
    provider: str = "gemini"


def normalize_answer(content):
    """
    Convert Gemini content blocks or ordinary text into a string.
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)

        return "\n".join(text_parts)

    return str(content)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    filename = file.filename or "uploaded.pdf"

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    content = await file.read()

    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"PDF exceeds {MAX_UPLOAD_MB} MB."
        )

    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF."
        )

    document_id = str(uuid.uuid4())
    safe_path = UPLOAD_DIR / f"{document_id}.pdf"

    try:
        safe_path.write_bytes(content)

        result = ingest_pdf(str(safe_path), document_id)

        save_document(
            document_id,
            filename,
            result["total_pages"],
            result["total_chunks"]
        )

        logger.info(
            "PDF uploaded successfully: %s, pages=%s, chunks=%s",
            document_id,
            result["total_pages"],
            result["total_chunks"]
        )

        return {
            "message": "PDF processed successfully",
            "document_id": document_id,
            "filename": filename,
            **result
        }

    except ValueError as exc:
        safe_path.unlink(missing_ok=True)

        logger.exception("PDF validation failed: %s", exc)

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except Exception as exc:
        safe_path.unlink(missing_ok=True)

        logger.exception("PDF upload/ingestion failed: %s", exc)

        raise HTTPException(
            status_code=502,
            detail="PDF processing failed. Check the backend logs."
        )


@router.post("/chat")
def chat(request: ChatRequest):

    if request.provider not in ("ollama", "gemini"):
        raise HTTPException(
            status_code=400,
            detail="Provider must be ollama or gemini."
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if not document_exists(request.document_id):
        raise HTTPException(
            status_code=404,
            detail="Document not found. Upload it again."
        )

    try:
        initial_state: RAGState = {
            "question": request.question.strip(),
            "document_id": request.document_id,
            "provider": request.provider,
            "documents": [],
            "context": "",
            "source_pages": [],
            "answer": ""
        }

        result = rag_graph.invoke(initial_state)

        answer = normalize_answer(result["answer"])

        sources = sorted({
            int(doc.metadata.get("page", 0)) + 1
            for doc in result.get("documents", [])
        })

        save_chat(
            request.document_id,
            request.question,
            answer,
            request.provider,
            sources
        )

        return {
            "question": request.question,
            "answer": answer,
            "provider": request.provider,
            "sources": sources
        }

    except ValueError as exc:
        logger.exception("Chat validation/configuration error")
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.exception("Chat endpoint failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Answer generation failed. Check backend logs."
        )


@router.get("/history/{document_id}")
def history(document_id: str):

    if not document_exists(document_id):
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return get_history(document_id)


@router.delete("/documents/{document_id}")
def delete_document(document_id: str):

    if not document_exists(document_id):
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    try:
        delete_document_vectors(document_id)

        (UPLOAD_DIR / f"{document_id}.pdf").unlink(
            missing_ok=True
        )

        delete_document_record(document_id)

        logger.info(
            "Document deleted successfully: %s",
            document_id
        )

        return {
            "message": "Document and its chat history deleted."
        }

    except Exception as exc:
        logger.exception(
            "Document deletion failed: %s",
            exc
        )

        raise HTTPException(
            status_code=500,
            detail="Could not delete document. Check backend logs."
        )
