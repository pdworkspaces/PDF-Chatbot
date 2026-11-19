from backend.services.pdf_service import (
    load_pdf,
    split_documents
)

from backend.services.vector_service import (
    store_documents,
    search_documents
)


def ingest_pdf(file_path, document_id):

    # Step 1: Load PDF
    documents = load_pdf(file_path)

    # Step 2: Split documents
    chunks = split_documents(documents)

    # Step 3: Store in vector database
    total_chunks = store_documents(
        chunks,
        document_id
    )

    return {
        "document_id": document_id,
        "total_pages": len(documents),
        "total_chunks": total_chunks
    }


def retrieve_context(question, document_id):

    results = search_documents(
        question,
        document_id
    )

    return results