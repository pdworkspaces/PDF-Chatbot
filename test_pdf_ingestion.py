from backend.services.rag_service import (
    ingest_pdf,
    retrieve_context
)

PDF_PATH = "data/uploads/sample.pdf"
DOCUMENT_ID = "test_document_001"

# Step 1: Ingest PDF
print("\nStarting PDF ingestion...")

result = ingest_pdf(
    PDF_PATH,
    DOCUMENT_ID
)

print("\nINGESTION RESULT:")
print(result)

# Step 2: Search PDF
question = "How many annual leave days are provided?"

print("\nSearching:", question)

results = retrieve_context(
    question,
    DOCUMENT_ID
)

print("\nRETRIEVED DOCUMENTS:")

for index, doc in enumerate(results):

    print(f"\nChunk {index + 1}")
    print("Page:", doc.metadata.get("page", 0) + 1)
    print("Content:", doc.page_content[:300])