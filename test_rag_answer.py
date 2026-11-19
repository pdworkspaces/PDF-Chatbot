
from langchain_core.prompts import ChatPromptTemplate

from backend.services.llm_service import get_llm
from backend.services.rag_service import retrieve_context


DOCUMENT_ID = "test_document_001"

# 1. Ask a question
question = "How many annual leave days are provided?"

print("\nQuestion:", question)

# 2. Retrieve relevant PDF chunks
documents = retrieve_context(
    question,
    DOCUMENT_ID
)

if not documents:
    print("No relevant documents found.")
    raise SystemExit(1)

# 3. Combine retrieved chunks into context
context = "\n\n".join(
    doc.page_content for doc in documents
)

# 4. Initialize local LLM
llm = get_llm("ollama")

# 5. Create prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful PDF question-answering assistant.
Answer using only the provided context.
If the answer is not present in the context, say:
'I could not find this information in the PDF.'
Do not make up information."""
    ),
    (
        "human",
        """Context:
{context}

Question:
{question}

Provide a clear and concise answer."""
    )
])

# 6. Generate answer
messages = prompt.format_messages(
    context=context,
    question=question
)

print("\nGenerating answer using Ollama...")

response = llm.invoke(messages)

# 7. Display answer
print("\n========== AI ANSWER ==========")
print(response.content)

# 8. Display source pages
print("\n========== SOURCE PAGES ==========")

for doc in documents:
    page = doc.metadata.get("page", 0) + 1
    print(f"Page {page}")
