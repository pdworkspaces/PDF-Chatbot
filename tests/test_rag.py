from langchain_core.documents import Document
from backend.services.pdf_service import split_documents

def test_document_splitting_creates_chunks():
    docs = [Document(page_content="A sentence about RAG. " * 150, metadata={"page": 0})]
    chunks = split_documents(docs)
    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 1000 for chunk in chunks)

def test_page_metadata_is_preserved():
    docs = [Document(page_content="PDF page content", metadata={"page": 3})]
    chunks = split_documents(docs)
    assert chunks[0].metadata["page"] == 3
