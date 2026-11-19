
from langchain_chroma import Chroma

from backend.config import CHROMA_DB_DIR
from backend.services.embedding_service import get_embedding_model


COLLECTION_NAME = "pdf_documents"


def get_vector_store():

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(CHROMA_DB_DIR)
    )

    return vector_store


def store_documents(chunks, document_id):

    vector_store = get_vector_store()

    for chunk in chunks:
        chunk.metadata["document_id"] = document_id

    ids = [
        f"{document_id}_{index}"
        for index in range(len(chunks))
    ]

    vector_store.add_documents(
        documents=chunks,
        ids=ids
    )

    print("Documents stored in ChromaDB!")

    return len(chunks)


def search_documents(question, document_id):

    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        question,
        k=4,
        filter={
            "document_id": document_id
        }
    )

    return results


# Delete all vectors belonging to a document
def delete_document_vectors(document_id):

    vector_store = get_vector_store()

    vector_store.delete(
        where={
            "document_id": document_id
        }
    )

    print(f"Deleted vectors for document: {document_id}")
