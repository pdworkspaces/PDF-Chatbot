
from backend.graph.rag_graph import ask_pdf

DOCUMENT_ID = "test_document_001"

question = "How many annual leave days are provided?"

print("\nStarting LangGraph RAG workflow...")

result = ask_pdf(
    question=question,
    document_id=DOCUMENT_ID,
    provider="ollama"
)

print("\n========== LANGGRAPH RESULT ==========")

print("\nQuestion:")
print(result["question"])

print("\nAI Answer:")
print(result["answer"])

print("\nSource Pages:")
print(result["source_pages"])
